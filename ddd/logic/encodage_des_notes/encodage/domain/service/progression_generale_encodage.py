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
from typing import Optional, List

from ddd.logic.encodage_des_notes.encodage.domain.model.gestionnaire_parcours import GestionnaireParcours
from ddd.logic.encodage_des_notes.encodage.repository.note_etudiant import INoteEtudiantRepository
from ddd.logic.encodage_des_notes.shared_kernel.domain.service.i_attribution_enseignant import \
    IAttributionEnseignantTranslator
from ddd.logic.encodage_des_notes.shared_kernel.domain.service.i_inscription_examen import IInscriptionExamenTranslator
from ddd.logic.encodage_des_notes.shared_kernel.domain.service.i_signaletique_etudiant import \
    ISignaletiqueEtudiantTranslator
from ddd.logic.encodage_des_notes.shared_kernel.domain.service.progression_generale import ProgressionGeneral
from ddd.logic.encodage_des_notes.soumission.repository.i_note_etudiant import INoteEtudiantRepository as \
    INoteEtudiantSoumissionRepository
from ddd.logic.encodage_des_notes.shared_kernel.domain.service.i_unite_enseignement import IUniteEnseignementTranslator
from ddd.logic.encodage_des_notes.shared_kernel.dtos import ProgressionGeneraleEncodageNotesDTO, PeriodeEncodageNotesDTO
from ddd.logic.encodage_des_notes.soumission.repository.i_responsable_de_notes import IResponsableDeNotesRepository
from osis_common.ddd import interface


class ProgressionGeneraleEncodage(interface.DomainService):

    @classmethod
    def get(
            cls,
            gestionnaire: GestionnaireParcours,
            periode_encodage: PeriodeEncodageNotesDTO,
            note_etudiant_repo: 'INoteEtudiantRepository',
            note_etudiant_soumission_repo: 'INoteEtudiantSoumissionRepository',
            responsable_notes_repo: 'IResponsableDeNotesRepository',
            signaletique_etudiant_translator: 'ISignaletiqueEtudiantTranslator',
            unite_enseignement_translator: 'IUniteEnseignementTranslator',
            inscription_examen_translator: 'IInscriptionExamenTranslator',
            attribution_translator: 'IAttributionEnseignantTranslator',

            noms_cohortes: Optional[List[str]],
            code_unite_enseignement: Optional[str],
            enseignant: Optional[str],
            seulement_notes_manquantes: bool = False
    ) -> 'ProgressionGeneraleEncodageNotesDTO':
        gestionnaire.verifier_gere_cohortes(set(noms_cohortes))
        notes_identites = note_etudiant_repo.search_notes_identites(
            noms_cohortes=noms_cohortes,
            annee_academique=periode_encodage.annee_concernee,
            numero_session=periode_encodage.session_concernee,
            code_unite_enseignement=code_unite_enseignement,
            note_manquante=seulement_notes_manquantes
        )
        notes_identites = _filtrer_par_enseignant(attribution_translator, enseignant, notes_identites, periode_encodage)

        return ProgressionGeneral().get(
            notes_identites,
            note_etudiant_soumission_repo,
            responsable_notes_repo,
            periode_encodage,
            signaletique_etudiant_translator,
            unite_enseignement_translator,
            inscription_examen_translator=inscription_examen_translator
        )


def _filtrer_par_enseignant(attribution_translator, enseignant, notes_identites, periode_encodage):
    if enseignant:
        attributions = attribution_translator.search_attributions_enseignant_par_nom_prenom_annee(
            annee=periode_encodage.annee_concernee,
            nom_prenom=enseignant,
        )
        codes_unites_enseignement = {attrib.code_unite_enseignement for attrib in attributions}
        return {
            note for note in notes_identites if note.code_unite_enseignement in codes_unites_enseignement
        }
    return notes_identites
