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
import datetime
from unittest import mock

import attr
from django.test import SimpleTestCase

from base.models.enums.peps_type import PepsTypes
from ddd.logic.encodage_des_notes.encodage.commands import GetFeuilleDeNotesGestionnaireCommand
from ddd.logic.encodage_des_notes.soumission.domain.validator.exceptions import PeriodeSoumissionNotesFermeeException, \
    PasGestionnaireParcoursExceptionException
from ddd.logic.encodage_des_notes.soumission.dtos import DateDTO, PeriodeSoumissionNotesDTO
from infrastructure.encodage_de_notes.encodage.domain.service.in_memory.cohortes_du_gestionnaire import \
    CohortesDuGestionnaireInMemory
from infrastructure.encodage_de_notes.encodage.domain.service.in_memory.feuille_de_notes_enseignant import \
    FeuilleDeNotesEnseignantTranslatorInMemory
from infrastructure.encodage_de_notes.common_domain.service.in_memory.attribution_enseignant import \
    AttributionEnseignantTranslatorInMemory
from infrastructure.encodage_de_notes.common_domain.service.in_memory.periode_encodage_notes import \
    PeriodeEncodageNotesTranslatorInMemory
from infrastructure.messages_bus import message_bus_instance


class GetFeuilleDeNotesGestionnaireTest(SimpleTestCase):

    def setUp(self) -> None:
        self.annee = 2020
        self.numero_session = 2
        self.matricule_enseignant = '00321234'
        self.matricule_gestionnaire = '22220000'
        self.code_unite_enseignement = 'LDROI1001'
        self.noma = '11111111'
        self.nom_cohorte = 'DROI1BA'

        self.cmd = GetFeuilleDeNotesGestionnaireCommand(
            code_unite_enseignement=self.code_unite_enseignement,
            matricule_fgs_gestionnaire=self.matricule_gestionnaire,
        )

        self.periode_soumission_translator = PeriodeEncodageNotesTranslatorInMemory()
        self.attribution_translator = AttributionEnseignantTranslatorInMemory()
        self.cohortes_gestionnaire_translator = CohortesDuGestionnaireInMemory()
        self.feuille_notes_enseignant_translator = FeuilleDeNotesEnseignantTranslatorInMemory()
        self.__mock_service_bus()

    def __mock_service_bus(self):
        message_bus_patcher = mock.patch.multiple(
            'infrastructure.messages_bus',
            PeriodeEncodageNotesTranslator=lambda: self.periode_soumission_translator,
            AttributionEnseignantTranslator=lambda: self.attribution_translator,
            FeuilleDeNotesEnseignantTranslator=lambda: self.feuille_notes_enseignant_translator,
            CohortesDuGestionnaire=lambda: self.cohortes_gestionnaire_translator,
        )
        message_bus_patcher.start()
        self.addCleanup(message_bus_patcher.stop)

        self.message_bus = message_bus_instance

    @mock.patch("infrastructure.messages_bus.PeriodeEncodageNotesTranslator")
    def test_should_empecher_si_periode_fermee_depuis_hier(self, mock_periode_translator):
        hier = datetime.date.today() - datetime.timedelta(days=1)
        date_dans_le_passe = DateDTO(jour=hier.day, mois=hier.month, annee=hier.year)
        periode_fermee = PeriodeSoumissionNotesDTO(
            annee_concernee=self.annee,
            session_concernee=self.numero_session,
            debut_periode_soumission=date_dans_le_passe,
            fin_periode_soumission=date_dans_le_passe,
        )
        periode_soumission_translator = PeriodeEncodageNotesTranslatorInMemory()
        periode_soumission_translator.get = lambda *args: periode_fermee
        mock_periode_translator.return_value = periode_soumission_translator

        with self.assertRaises(PeriodeSoumissionNotesFermeeException):
            self.message_bus.invoke(self.cmd)

    def test_should_empecher_si_utilisateur_pas_gestionnaire(self):
        matricule_nongestionnaire = self.matricule_enseignant
        cmd = attr.evolve(self.cmd, matricule_fgs_gestionnaire=matricule_nongestionnaire)
        with self.assertRaises(PasGestionnaireParcoursExceptionException):
            self.message_bus.invoke(cmd)

    def test_should_renvoyer_responsable_de_notes(self):
        result = self.message_bus.invoke(self.cmd)
        self.assertEqual(result.responsable_note.nom, 'Chileng')
        self.assertEqual(result.responsable_note.prenom, 'Jean-Michel')

    def test_should_renvoyer_unite_enseignement(self):
        result = self.message_bus.invoke(self.cmd)
        self.assertEqual(result.code_unite_enseignement, self.code_unite_enseignement)
        self.assertEqual(result.intitule_complet_unite_enseignement, "Intitule complet unite enseignement")

    def test_should_renvoyer_signaletique_etudiant(self):
        result = self.message_bus.invoke(self.cmd)
        note_etudiant = result.notes_etudiants[0]
        self.assertEqual(note_etudiant.noma, self.noma)
        self.assertEqual(note_etudiant.nom, "NomEtudiant1")
        self.assertEqual(note_etudiant.prenom, "PrenomEtudiant1")
        self.assertEqual(note_etudiant.peps.type_peps, PepsTypes.ARRANGEMENT_JURY.name)
        self.assertEqual(note_etudiant.peps.tiers_temps, True)
        self.assertEqual(note_etudiant.peps.copie_adaptee, True)
        self.assertEqual(note_etudiant.peps.local_specifique, True)
        self.assertEqual(note_etudiant.peps.autre_amenagement, True)
        self.assertEqual(note_etudiant.peps.details_autre_amenagement, "Details autre aménagement")
        self.assertEqual(note_etudiant.peps.accompagnateur, "Accompagnateur")

    def test_should_renvoyer_numero_de_session_et_annee(self):
        result = self.message_bus.invoke(self.cmd)
        self.assertEqual(result.annee_academique, self.annee)
        self.assertEqual(result.numero_session, self.numero_session)

    def test_should_renvoyer_inscrit_tardivement(self):
        result = message_bus_instance.invoke(self.cmd)
        note_etudiant = result.notes_etudiants[0]
        self.assertTrue(note_etudiant.inscrit_tardivement)

    def test_should_renvoyer_desinscrit_tardivement(self):
        result = message_bus_instance.invoke(self.cmd)
        note_etudiant = result.notes_etudiants[1]
        self.assertTrue(note_etudiant.desinscrit_tardivement)

    def test_should_renvoyer_note_est_soumise(self):
        result = message_bus_instance.invoke(self.cmd)
        note_etudiant = result.notes_etudiants[0]
        self.assertFalse(note_etudiant.est_soumise)

    def test_should_renvoyer_valeur_note(self):
        result = self.message_bus.invoke(self.cmd)
        note_etudiant = result.notes_etudiants[0]
        expected_result = ""
        self.assertEqual(expected_result, note_etudiant.note)

    def test_should_renvoyer_echeance_enseignant(self):
        result = self.message_bus.invoke(self.cmd)
        note_etudiant = result.notes_etudiants[0]
        expected_result = DateDTO(jour=5, mois=6, annee=2020)
        self.assertEqual(expected_result, note_etudiant.echeance_enseignant)
