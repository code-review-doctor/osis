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
import itertools
from typing import List, Dict, Set, Tuple

from ddd.logic.encodage_des_notes.soumission.builder.feuille_de_notes_identity_builder import \
    FeuilleDeNotesIdentityBuilder
from ddd.logic.encodage_des_notes.soumission.domain.model.feuille_de_notes import FeuilleDeNotes
from ddd.logic.encodage_des_notes.soumission.domain.service.i_attribution_enseignant import \
    IAttributionEnseignantTranslator
from ddd.logic.encodage_des_notes.soumission.domain.service.i_periode_soumission_notes import \
    IPeriodeSoumissionNotesTranslator
from ddd.logic.encodage_des_notes.soumission.domain.service.i_signaletique_etudiant import \
    ISignaletiqueEtudiantTranslator
from ddd.logic.encodage_des_notes.soumission.domain.service.i_unite_enseignement import IUniteEnseignementTranslator
from ddd.logic.encodage_des_notes.soumission.dtos import ProgressionGeneraleEncodageNotesDTO, \
    ProgressionEncodageNotesUniteEnseignementDTO, DateEcheanceDTO, UniteEnseignementDTO
from ddd.logic.encodage_des_notes.soumission.repository.i_feuille_de_notes import IFeuilleDeNotesRepository
from osis_common.ddd import interface


class ProgressionGeneraleEncodage(interface.DomainService):

    @classmethod
    def get(
            cls,
            matricule_fgs_enseignant: str,
            feuille_de_note_repo: 'IFeuilleDeNotesRepository',
            attribution_translator: 'IAttributionEnseignantTranslator',
            periode_soumission_note_translator: 'IPeriodeSoumissionNotesTranslator',
            signaletique_etudiant_translator: 'ISignaletiqueEtudiantTranslator',
            unite_enseignement_translator: 'IUniteEnseignementTranslator',
    ) -> 'ProgressionGeneraleEncodageNotesDTO':
        periode_soumission = periode_soumission_note_translator.get()
        annee_academique = periode_soumission.annee_concernee
        numero_session = periode_soumission.session_concernee

        feuilles_de_notes = _search_feuille_de_notes(
            attribution_translator,
            feuille_de_note_repo,
            matricule_fgs_enseignant,
            numero_session,
            annee_academique
        )

        nomas_concernes = itertools.chain.from_iterable((feuille.get_all_nomas() for feuille in feuilles_de_notes))
        nomas_avec_peps = _get_nomas_avec_peps(list(nomas_concernes), signaletique_etudiant_translator)

        codes_concernes = {f.code_unite_enseignement for f in feuilles_de_notes}
        detail_unite_enseignement_par_code = _get_detail_unite_enseignement_par_code(
            {(code, annee_academique) for code in codes_concernes},
            unite_enseignement_translator,
        )

        progressions = [
            cls._compute_progression_pour_feuille_de_notes(
                feuille_de_note,
                nomas_avec_peps,
                detail_unite_enseignement_par_code
            ) for feuille_de_note in sorted(feuilles_de_notes, key=lambda f: f.code_unite_enseignement)
        ]

        return ProgressionGeneraleEncodageNotesDTO(
            annee_academique=annee_academique,
            numero_session=numero_session,
            progression_generale=progressions,
        )

    @classmethod
    def _compute_progression_pour_feuille_de_notes(
            cls,
            feuille_de_notes: 'FeuilleDeNotes',
            nomas_avec_peps: Set[str],
            detail_unite_enseignement_par_code: Dict[str, UniteEnseignementDTO]
    ):
        detail_unite_enseignement = detail_unite_enseignement_par_code[feuille_de_notes.code_unite_enseignement]
        nombre_total_notes_par_echeance_trie_par_echeance = sorted(
            feuille_de_notes.get_nombre_total_notes_par_echeance().items(),
            key=lambda tuple_echeance_nombre_total_notes: tuple_echeance_nombre_total_notes[0]
        )
        return ProgressionEncodageNotesUniteEnseignementDTO(
            code_unite_enseignement=feuille_de_notes.code_unite_enseignement,
            intitule_complet_unite_enseignement=detail_unite_enseignement.intitule_complet,
            dates_echeance=[
                DateEcheanceDTO(
                    jour=echeance.day,
                    mois=echeance.month,
                    annee=echeance.year,
                    quantite_notes_soumises=feuille_de_notes.get_nombre_notes_soumises_par_echeance().get(echeance, 0),
                    quantite_total_notes=total_notes,
                ) for echeance, total_notes in nombre_total_notes_par_echeance_trie_par_echeance
            ],
            a_etudiants_peps=any(note.noma in nomas_avec_peps for note in feuille_de_notes.notes),
        )


def _search_feuille_de_notes(
        attribution_translator: 'IAttributionEnseignantTranslator',
        feuille_de_note_repo: 'IFeuilleDeNotesRepository',
        matricule_fgs_enseignant: str,
        session_concerne: int,
        annee_concerne: int
        ):
    attributions = attribution_translator.search_attributions_enseignant_par_matricule(matricule_fgs_enseignant)
    identities = [
        FeuilleDeNotesIdentityBuilder.build_from_session_and_unit_enseignement_datas(
            numero_session=session_concerne,
            code_unite_enseignement=attrib.code_unite_enseignement,
            annee_academique=annee_concerne,
        ) for attrib in attributions
    ]
    return feuille_de_note_repo.search(entity_ids=identities)


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
