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
from ddd.logic.encodage_des_notes.encodage.builder.gestionnaire_parcours_builder import GestionnaireParcoursBuilder
from ddd.logic.encodage_des_notes.encodage.commands import GetProgressionGeneraleGestionnaireCommand
from ddd.logic.encodage_des_notes.encodage.domain.service.i_cohortes_du_gestionnaire import ICohortesDuGestionnaire
from ddd.logic.encodage_des_notes.encodage.domain.service.progression_generale_encodage import \
    ProgressionGeneraleEncodage
from ddd.logic.encodage_des_notes.encodage.repository.note_etudiant import INoteEtudiantRepository
from ddd.logic.encodage_des_notes.shared_kernel.domain.service.i_attribution_enseignant import \
    IAttributionEnseignantTranslator
from ddd.logic.encodage_des_notes.shared_kernel.domain.service.i_inscription_examen import IInscriptionExamenTranslator
from ddd.logic.encodage_des_notes.shared_kernel.domain.service.i_periode_encodage_notes import \
    IPeriodeEncodageNotesTranslator
from ddd.logic.encodage_des_notes.shared_kernel.domain.service.i_signaletique_etudiant import \
    ISignaletiqueEtudiantTranslator
from ddd.logic.encodage_des_notes.soumission.repository.i_note_etudiant import INoteEtudiantRepository as \
    INoteEtudiantSoumissionRepository
from ddd.logic.encodage_des_notes.shared_kernel.domain.service.periode_encodage_ouverte import PeriodeEncodageOuverte
from ddd.logic.encodage_des_notes.shared_kernel.domain.service.i_unite_enseignement import IUniteEnseignementTranslator
from ddd.logic.encodage_des_notes.shared_kernel.dtos import ProgressionGeneraleEncodageNotesDTO
from ddd.logic.encodage_des_notes.soumission.repository.i_responsable_de_notes import IResponsableDeNotesRepository


def get_progression_generale_gestionnaire(
        cmd: 'GetProgressionGeneraleGestionnaireCommand',
        note_etudiant_repo: 'INoteEtudiantRepository',
        note_etudiant_soumission_repo: 'INoteEtudiantSoumissionRepository',
        responsable_notes_repo: 'IResponsableDeNotesRepository',
        periode_encodage_note_translator: 'IPeriodeEncodageNotesTranslator',
        signaletique_etudiant_translator: 'ISignaletiqueEtudiantTranslator',
        unite_enseignement_translator: 'IUniteEnseignementTranslator',
        cohortes_gestionnaire_translator: 'ICohortesDuGestionnaire',
        inscription_examen_translator: 'IInscriptionExamenTranslator',
        attribution_translator: 'IAttributionEnseignantTranslator',
) -> 'ProgressionGeneraleEncodageNotesDTO':
    # GIVEN
    PeriodeEncodageOuverte().verifier(periode_encodage_note_translator)
    periode_encodage = periode_encodage_note_translator.get()
    gestionnaire = GestionnaireParcoursBuilder().get(
        matricule_gestionnaire=cmd.matricule_fgs_gestionnaire,
        annee_concernee=periode_encodage.annee_concernee,
        cohortes_gestionnaire_translator=cohortes_gestionnaire_translator,
    )

    return ProgressionGeneraleEncodage().get(
        gestionnaire=gestionnaire,
        periode_encodage=periode_encodage,
        note_etudiant_repo=note_etudiant_repo,
        note_etudiant_soumission_repo=note_etudiant_soumission_repo,
        responsable_notes_repo=responsable_notes_repo,
        signaletique_etudiant_translator=signaletique_etudiant_translator,
        unite_enseignement_translator=unite_enseignement_translator,
        inscription_examen_translator=inscription_examen_translator,
        attribution_translator=attribution_translator,

        noms_cohortes=cmd.noms_cohortes,
        code_unite_enseignement=cmd.code_unite_enseignement,
        enseignant=cmd.enseignant,
        seulement_notes_manquantes=cmd.seulement_notes_manquantes
    )
