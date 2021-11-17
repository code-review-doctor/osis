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
from typing import List

from ddd.logic.encodage_des_notes.encodage.builder.gestionnaire_parcours_builder import GestionnaireParcoursBuilder
from ddd.logic.encodage_des_notes.encodage.commands import EncoderNotesCommand
from ddd.logic.encodage_des_notes.encodage.domain.model.note_etudiant import IdentiteNoteEtudiant
from ddd.logic.encodage_des_notes.encodage.domain.service.cohorte_non_complete import CohorteAvecEncodageIncomplet
from ddd.logic.encodage_des_notes.encodage.domain.service.encoder_notes_en_lot import EncoderNotesEnLot
from ddd.logic.encodage_des_notes.encodage.domain.service.i_cohortes_du_gestionnaire import ICohortesDuGestionnaire
from ddd.logic.encodage_des_notes.encodage.domain.service.i_historiser_notes import IHistoriserEncodageNotesService
from ddd.logic.encodage_des_notes.encodage.domain.service.i_notifier_encodage_notes import INotifierEncodageNotes
from ddd.logic.encodage_des_notes.encodage.repository.note_etudiant import INoteEtudiantRepository
from ddd.logic.encodage_des_notes.shared_kernel.domain.builder.encoder_notes_rapport_builder import \
    EncoderNotesRapportBuilder
from ddd.logic.encodage_des_notes.shared_kernel.domain.service.i_attribution_enseignant import \
    IAttributionEnseignantTranslator
from ddd.logic.encodage_des_notes.shared_kernel.domain.service.i_inscription_examen import IInscriptionExamenTranslator
from ddd.logic.encodage_des_notes.shared_kernel.domain.service.i_periode_encodage_notes import \
    IPeriodeEncodageNotesTranslator
from ddd.logic.encodage_des_notes.shared_kernel.domain.service.i_signaletique_etudiant import \
    ISignaletiqueEtudiantTranslator
from ddd.logic.encodage_des_notes.shared_kernel.domain.service.i_signaletique_personne import \
    ISignaletiquePersonneTranslator
from ddd.logic.encodage_des_notes.shared_kernel.domain.service.periode_encodage_ouverte import PeriodeEncodageOuverte
from ddd.logic.encodage_des_notes.shared_kernel.repository.i_encoder_notes_rapport import IEncoderNotesRapportRepository
from ddd.logic.encodage_des_notes.soumission.repository.i_adresse_feuille_de_notes import \
    IAdresseFeuilleDeNotesRepository

NouvelleNote = str
EmailEtudiant = str


def encoder_notes(
        cmd: 'EncoderNotesCommand',
        note_etudiant_repo: 'INoteEtudiantRepository',
        periode_encodage_note_translator: 'IPeriodeEncodageNotesTranslator',
        cohortes_gestionnaire_translator: 'ICohortesDuGestionnaire',
        notification_encodage: 'INotifierEncodageNotes',
        attribution_enseignant_translator: 'IAttributionEnseignantTranslator',
        signaletique_personne_repo: 'ISignaletiquePersonneTranslator',
        signaletique_etudiant_repo: 'ISignaletiqueEtudiantTranslator',
        adresse_feuille_de_notes_repo: 'IAdresseFeuilleDeNotesRepository',
        historiser_note_service: 'IHistoriserEncodageNotesService',
        inscription_examen_translator: 'IInscriptionExamenTranslator',
        rapport_repository: 'IEncoderNotesRapportRepository'
) -> List['IdentiteNoteEtudiant']:
    # Given
    PeriodeEncodageOuverte().verifier(periode_encodage_note_translator)
    gestionnaire_parcours = GestionnaireParcoursBuilder().get(
        matricule_gestionnaire=cmd.matricule_fgs_gestionnaire,
        cohortes_gestionnaire_translator=cohortes_gestionnaire_translator,
    )
    periode_ouverte = periode_encodage_note_translator.get()

    cohortes_non_completes = CohorteAvecEncodageIncomplet().search(
        [cmd_note.code_unite_enseignement for cmd_note in cmd.notes_encodees],
        periode_ouverte.annee_concernee,
        periode_ouverte.session_concernee,
        note_etudiant_repo,
        inscription_examen_translator,
    )

    # WHEN
    rapport = EncoderNotesRapportBuilder.build_from_command(cmd)
    notes = EncoderNotesEnLot().execute(
        cmd.notes_encodees,
        gestionnaire_parcours,
        note_etudiant_repo,
        periode_ouverte,
        historiser_note_service,
        inscription_examen_translator,
        rapport,
        rapport_repository
    )

    # THEN
    notification_encodage.notifier(
        notes,
        cohortes_non_completes,
        gestionnaire_parcours,
        note_etudiant_repo,
        attribution_enseignant_translator,
        signaletique_personne_repo,
        signaletique_etudiant_repo,
        adresse_feuille_de_notes_repo,
        inscription_examen_translator,
    )

    return notes
