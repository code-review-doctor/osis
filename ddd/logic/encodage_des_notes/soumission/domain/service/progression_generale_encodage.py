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
from collections import Counter, OrderedDict
from typing import List, Dict, Set

from ddd.logic.encodage_des_notes.soumission.builder.feuille_de_notes_identity_builder import \
    FeuilleDeNotesIdentityBuilder
from ddd.logic.encodage_des_notes.soumission.domain.service.i_attribution_enseignant import \
    IAttributionEnseignantTranslator
from ddd.logic.encodage_des_notes.soumission.domain.service.i_periode_soumission_notes import \
    IPeriodeSoumissionNotesTranslator
from ddd.logic.encodage_des_notes.soumission.domain.service.i_signaletique_etudiant import \
    ISignaletiqueEtudiantTranslator
from ddd.logic.encodage_des_notes.soumission.domain.service.i_unite_enseignement import IUniteEnseignementTranslator
from ddd.logic.encodage_des_notes.soumission.dtos import ProgressionGeneraleEncodageNotesDTO, \
    ProgressionEncodageNotesUniteEnseignementDTO, DateEcheanceDTO, SignaletiqueEtudiantDTO, UniteEnseignementDTO
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
        # TODO :: unit tests
        # TODO :: découpage en fonctions
        periode_soumission = periode_soumission_note_translator.get()
        attributions = attribution_translator.search_attributions_enseignant_par_matricule(matricule_fgs_enseignant)
        identities = [
            FeuilleDeNotesIdentityBuilder.build_from_session_and_unit_enseignement_datas(
                numero_session=periode_soumission.session_concernee,
                code_unite_enseignement=attrib.code_unite_enseignement,
                annee_academique=periode_soumission.annee_concernee,
            ) for attrib in attributions
        ]

        feuilles_de_notes = feuille_de_note_repo.search(entity_ids=identities)

        annee_academique = feuilles_de_notes[0].annee
        numero_session = feuilles_de_notes[0].numero_session

        nomas_concernes = [note.noma for feuille_de_notes in feuilles_de_notes for note in feuille_de_notes.notes]
        signaletique_par_noma = _get_signaletique_etudiant_par_noma(nomas_concernes, signaletique_etudiant_translator)

        codes_concernes = {f.code_unite_enseignement for f in feuilles_de_notes}
        unite_enseignement_par_code = _get_detail_unite_enseignement_par_code(
            codes_concernes,
            annee_academique,
            unite_enseignement_translator,
        )

        progressions = []

        for feuille_de_notes in feuilles_de_notes:
            notes_soumises = [
                note.date_limite_de_remise for note in feuille_de_notes.notes
                if note.est_soumise
            ]
            total_notes = [
                note.date_limite_de_remise for note in feuille_de_notes.notes
            ]

            notes_soumises_par_echeance = dict(Counter(notes_soumises))
            total_notes_par_echeance = OrderedDict(sorted(Counter(total_notes).items()))

            detail_unite_enseignement = unite_enseignement_par_code[feuille_de_notes.code_unite_enseignement]
            progression = ProgressionEncodageNotesUniteEnseignementDTO(
                code_unite_enseignement=feuille_de_notes.code_unite_enseignement,
                intitule_complet_unite_enseignement=detail_unite_enseignement.intitule_complet,
                dates_echeance=[
                    DateEcheanceDTO(
                        jour=echeance.day,
                        mois=echeance.month,
                        annee=echeance.year,
                        quantite_notes_soumises=notes_soumises_par_echeance[echeance],
                        quantite_total_notes=total_notes,
                    ) for echeance, total_notes in total_notes_par_echeance.items()
                ],
                a_etudiants_peps=any(signaletique_par_noma.get(note.noma) for note in feuille_de_notes.notes),
            )
            progressions.append(progression)

        return ProgressionGeneraleEncodageNotesDTO(
            annee_academique=annee_academique,
            numero_session=numero_session,
            progression_generale=progressions,
        )


def _get_signaletique_etudiant_par_noma(
        nomas_concernes: List[str],
        signaletique_etudiant_translator: 'ISignaletiqueEtudiantTranslator'
) -> Dict[str, 'SignaletiqueEtudiantDTO']:
    signaletiques_etds = signaletique_etudiant_translator.search(nomas=nomas_concernes)
    return {signal.noma: signal for signal in signaletiques_etds}


def _get_detail_unite_enseignement_par_code(
        codes: Set[str],
        annee: int,
        unite_enseignement_translator: 'IUniteEnseignementTranslator',
) -> Dict[str, UniteEnseignementDTO]:
    unites_enseignement = unite_enseignement_translator.search_by_codes(codes, annee)
    return {
        ue.code: ue for ue in unites_enseignement
    }
