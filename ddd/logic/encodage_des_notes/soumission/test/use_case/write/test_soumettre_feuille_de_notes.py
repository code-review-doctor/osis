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

from ddd.logic.encodage_des_notes.soumission.commands import SoumettreFeuilleDeNotesCommand
from ddd.logic.encodage_des_notes.soumission.domain.validator.exceptions import PeriodeSoumissionNotesFermeeException, \
    PasResponsableDeNotesException
from ddd.logic.encodage_des_notes.soumission.dtos import PeriodeSoumissionNotesDTO, DateDTO
from ddd.logic.encodage_des_notes.tests.factory.feuille_de_notes import FeuilleDeNotesAvecNotesEncodees, \
    FeuilleDeNotesAvecNotesManquantes
from ddd.logic.encodage_des_notes.tests.factory.responsable_de_notes import \
    ResponsableDeNotesLDROI1001Annee2020Factory
from infrastructure.encodage_de_notes.shared_kernel.service.in_memory.periode_encodage_notes import \
    PeriodeEncodageNotesTranslatorInMemory
from infrastructure.encodage_de_notes.shared_kernel.service.periode_encodage_notes import \
    PeriodeEncodageNotesTranslator
from infrastructure.encodage_de_notes.soumission.repository.in_memory.feuille_de_notes import \
    FeuilleDeNotesInMemoryRepository
from infrastructure.encodage_de_notes.soumission.repository.in_memory.responsable_de_notes import \
    ResponsableDeNotesInMemoryRepository
from infrastructure.messages_bus import message_bus_instance


class SoumettreFeuilleDeNotesTest(SimpleTestCase):

    def setUp(self) -> None:
        self.responsable_notes = ResponsableDeNotesLDROI1001Annee2020Factory()
        self.responsables_notes_repo = ResponsableDeNotesInMemoryRepository()
        self.responsables_notes_repo.save(self.responsable_notes)
        self.matricule_enseignant = self.responsable_notes.matricule_fgs_enseignant

        self.feuille_de_notes = FeuilleDeNotesAvecNotesEncodees(
            entity_id__code_unite_enseignement='LDROI1001',
        )
        self.feuille_notes_repo = FeuilleDeNotesInMemoryRepository()
        self.feuille_notes_repo.entities.clear()
        self.feuille_notes_repo.save(self.feuille_de_notes)

        self.cmd = SoumettreFeuilleDeNotesCommand(
            code_unite_enseignement=self.feuille_de_notes.code_unite_enseignement,
            annee_unite_enseignement=self.feuille_de_notes.annee,
            numero_session=self.feuille_de_notes.numero_session,
            matricule_fgs_enseignant=self.matricule_enseignant,
        )
        self.__mock_service_bus()

    def __mock_service_bus(self):
        message_bus_patcher = mock.patch.multiple(
            'infrastructure.messages_bus',
            FeuilleDeNotesRepository=lambda: self.feuille_notes_repo,
            ResponsableDeNotesRepository=lambda: self.responsables_notes_repo,
            PeriodeEncodageNotesTranslator=lambda: PeriodeEncodageNotesTranslatorInMemory(),
        )
        message_bus_patcher.start()
        self.addCleanup(message_bus_patcher.stop)
        self.message_bus = message_bus_instance

    def test_should_pas_soumettre_si_note_manquante(self):
        feuille_notes_repo = FeuilleDeNotesInMemoryRepository()
        feuille_de_notes = FeuilleDeNotesAvecNotesManquantes(
            entity_id__code_unite_enseignement='LDROI1001',
        )
        feuille_notes_repo.get = lambda *args, **kwargs: feuille_de_notes
        cmd = SoumettreFeuilleDeNotesCommand(
            code_unite_enseignement=feuille_de_notes.code_unite_enseignement,
            annee_unite_enseignement=feuille_de_notes.annee,
            numero_session=feuille_de_notes.numero_session,
            matricule_fgs_enseignant=self.matricule_enseignant,
        )
        self.message_bus.invoke(cmd)
        feuille_de_notes_apres_soumettre = feuille_notes_repo.get(feuille_de_notes.entity_id)
        for note in feuille_de_notes_apres_soumettre.notes:
            self.assertFalse(note.est_soumise)

    @mock.patch("infrastructure.messages_bus.PeriodeEncodageNotesTranslator")
    def test_should_empecher_si_periode_soumission_fermee(self, mock_periode_translator):
        hier = datetime.date.today() - datetime.timedelta(days=1)
        date_dans_le_passe = DateDTO(jour=hier.day, mois=hier.month, annee=hier.year)
        periode_fermee = PeriodeSoumissionNotesDTO(
            annee_concernee=self.feuille_de_notes.annee,
            session_concernee=self.feuille_de_notes.numero_session,
            debut_periode_soumission=date_dans_le_passe,
            fin_periode_soumission=date_dans_le_passe,
        )
        periode_soumission_translator = PeriodeEncodageNotesTranslatorInMemory()
        periode_soumission_translator.get = lambda *args: periode_fermee
        mock_periode_translator.return_value = periode_soumission_translator
        with self.assertRaises(PeriodeSoumissionNotesFermeeException):
            self.message_bus.invoke(self.cmd)

    @mock.patch("infrastructure.messages_bus.PeriodeEncodageNotesTranslator")
    def test_should_empecher_si_acune_periode_soumission_trouvee(self, mock_periode_translator):
        aucune_periode_trouvee = None
        periode_soumission_translator = PeriodeEncodageNotesTranslator()
        periode_soumission_translator.get = lambda *args: aucune_periode_trouvee
        mock_periode_translator.return_value = periode_soumission_translator
        with self.assertRaises(PeriodeSoumissionNotesFermeeException):
            self.message_bus.invoke(self.cmd)

    def test_should_empecher_si_responsable_de_notes_aucune_unite_enseignement(self):
        matricule_non_responsable = "99999999"
        cmd = attr.evolve(self.cmd, matricule_fgs_enseignant=matricule_non_responsable)
        with self.assertRaises(PasResponsableDeNotesException):
            self.message_bus.invoke(cmd)

    def test_should_empecher_si_pas_responsable_de_notes_unite_enseignement(self):
        feuille_de_notes_sans_responsable = FeuilleDeNotesAvecNotesEncodees()
        cmd = SoumettreFeuilleDeNotesCommand(
            code_unite_enseignement=feuille_de_notes_sans_responsable.code_unite_enseignement,
            annee_unite_enseignement=feuille_de_notes_sans_responsable.annee,
            numero_session=feuille_de_notes_sans_responsable.numero_session,
            matricule_fgs_enseignant="124889",
        )
        with self.assertRaises(PasResponsableDeNotesException):
            self.message_bus.invoke(cmd)

    def test_should_soumettre_plusieurs_notes(self):
        entity_id = self.message_bus.invoke(self.cmd)
        feuille_de_notes_apres_soumettre = self.feuille_notes_repo.get(entity_id)
        for note in feuille_de_notes_apres_soumettre.notes:
            self.assertTrue(note.est_soumise)
