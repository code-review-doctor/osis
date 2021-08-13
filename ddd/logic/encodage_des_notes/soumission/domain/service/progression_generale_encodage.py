##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2021 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
import collections
from typing import List, Dict, Set, Tuple, Any, Callable, Iterable

from ddd.logic.encodage_des_notes.shared_kernel.service.i_attribution_enseignant import \
    IAttributionEnseignantTranslator
from ddd.logic.encodage_des_notes.shared_kernel.service.i_periode_encodage_notes import \
    IPeriodeEncodageNotesTranslator
from ddd.logic.encodage_des_notes.shared_kernel.service.i_signaletique_etudiant import \
    ISignaletiqueEtudiantTranslator
from ddd.logic.encodage_des_notes.shared_kernel.service.i_unite_enseignement import IUniteEnseignementTranslator
from ddd.logic.encodage_des_notes.soumission.domain.model.note_etudiant import NoteEtudiant
from ddd.logic.encodage_des_notes.soumission.dtos import ProgressionGeneraleEncodageNotesDTO, \
    ProgressionEncodageNotesUniteEnseignementDTO, DateEcheanceDTO, UniteEnseignementDTO
from ddd.logic.encodage_des_notes.soumission.repository.i_note_etudiant import INoteEtudiantRepository
from osis_common.ddd import interface


class ProgressionGeneraleEncodage(interface.DomainService):

    @classmethod
    def get(
            cls,
            matricule_fgs_enseignant: str,
            note_etudiant_repo: 'INoteEtudiantRepository',
            attribution_translator: 'IAttributionEnseignantTranslator',
            periode_soumission_note_translator: 'IPeriodeEncodageNotesTranslator',
            signaletique_etudiant_translator: 'ISignaletiqueEtudiantTranslator',
            unite_enseignement_translator: 'IUniteEnseignementTranslator',
    ) -> 'ProgressionGeneraleEncodageNotesDTO':
        periode_soumission = periode_soumission_note_translator.get()
        annee_academique = periode_soumission.annee_concernee
        numero_session = periode_soumission.session_concernee

        notes = _search_notes(
            attribution_translator,
            note_etudiant_repo,
            matricule_fgs_enseignant,
            numero_session,
            annee_academique
        )

        nomas_concernes = [note.noma for note in notes]
        nomas_avec_peps = _get_nomas_avec_peps(nomas_concernes, signaletique_etudiant_translator)

        detail_unite_enseignement_par_code = _get_detail_unite_enseignement_par_code(
            {(note.code_unite_enseignement, note.annee) for note in notes},
            unite_enseignement_translator,
        )

        notes_grouped_by_code_unite_enseignement = group_by(notes, lambda note: note.code_unite_enseignement)

        progressions = [
            cls._compute_progression_pour_notes_de_meme_unite_enseignement(
                notes,
                nomas_avec_peps,
                detail_unite_enseignement_par_code[code_unite_enseignement]
            ) for code_unite_enseignement, notes in notes_grouped_by_code_unite_enseignement.items()
        ]

        return ProgressionGeneraleEncodageNotesDTO(
            annee_academique=annee_academique,
            numero_session=numero_session,
            progression_generale=sorted(progressions, key=lambda progression: progression.code_unite_enseignement),
        )

    @classmethod
    def _compute_progression_pour_notes_de_meme_unite_enseignement(
            cls,
            notes: List['NoteEtudiant'],
            nomas_avec_peps: Set[str],
            detail_unite_enseignement: UniteEnseignementDTO
    ):
        notes_grouped_by_echeance = group_by(notes, lambda note: note.date_limite_de_remise)
        list_tuple_echeance_notes = sorted(
            notes_grouped_by_echeance.items(),
            key=lambda tuple_echeance_notes: tuple_echeance_notes[0]
        )
        return ProgressionEncodageNotesUniteEnseignementDTO(
            code_unite_enseignement=detail_unite_enseignement.code,
            intitule_complet_unite_enseignement=detail_unite_enseignement.intitule_complet,
            dates_echeance=[
                DateEcheanceDTO(
                    jour=echeance.jour,
                    mois=echeance.mois,
                    annee=echeance.annee,
                    quantite_notes_soumises=len([note for note in notes if note.est_soumise]),
                    quantite_total_notes=len(notes),
                ) for echeance, notes in list_tuple_echeance_notes
            ],
            a_etudiants_peps=any(note.noma in nomas_avec_peps for note in notes),
        )


#  TODO to move
def group_by(iterable: Iterable[Any], key_func: Callable) -> Dict:
    result = collections.defaultdict(list)

    for element in iterable:
        result[key_func(element)].append(element)

    return result


def _search_notes(
        attribution_translator: 'IAttributionEnseignantTranslator',
        note_etudiant_repo: 'INoteEtudiantRepository',
        matricule_fgs_enseignant: str,
        session_concerne: int,
        annee_concerne: int
) -> List['NoteEtudiant']:
    attributions = attribution_translator.search_attributions_enseignant_par_matricule(
        annee_concerne,
        matricule_fgs_enseignant
    )
    search_criterias = [(attrib.code_unite_enseignement, annee_concerne, session_concerne) for attrib in attributions]
    return note_etudiant_repo.search_by_code_unite_enseignement_annee_session(criterias=search_criterias)


def _get_nomas_avec_peps(
        nomas_concernes: List[str],
        signaletique_etudiant_translator: 'ISignaletiqueEtudiantTranslator'
) -> Set[str]:
    signaletiques_etds = signaletique_etudiant_translator.search(nomas=nomas_concernes)
    return {signal.noma for signal in signaletiques_etds if bool(signal.peps)}


def _get_detail_unite_enseignement_par_code(
        code_annee_valeurs: Set[Tuple[str, int]],
        unite_enseignement_translator: 'IUniteEnseignementTranslator',
) -> Dict[str, UniteEnseignementDTO]:
    unites_enseignement = unite_enseignement_translator.search(code_annee_valeurs)
    return {ue.code: ue for ue in unites_enseignement}
