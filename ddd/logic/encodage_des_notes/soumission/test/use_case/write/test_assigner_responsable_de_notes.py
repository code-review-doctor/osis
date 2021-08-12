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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
import attr
import mock
from django.test import SimpleTestCase

from ddd.logic.encodage_des_notes.soumission.commands import AssignerResponsableDeNotesCommand
from ddd.logic.encodage_des_notes.soumission.domain.validator.exceptions import \
    EnseignantNonAttribueUniteEnseignementException
from ddd.logic.encodage_des_notes.tests.factory.responsable_de_notes import \
    ResponsableDeNotesPourUneUniteEnseignement, \
    ResponsableDeNotesPourMultipleUniteEnseignements
from infrastructure.encodage_de_notes.shared_kernel.service.in_memory.attribution_enseignant import \
    AttributionEnseignantTranslatorInMemory
from infrastructure.encodage_de_notes.soumission.repository.in_memory.responsable_de_notes import \
    ResponsableDeNotesInMemoryRepository
from infrastructure.messages_bus import message_bus_instance


class TestAssignerResponsableDeNotes(SimpleTestCase):

    def setUp(self) -> None:
        self.responsable = ResponsableDeNotesPourUneUniteEnseignement()

        self.repo = ResponsableDeNotesInMemoryRepository()
        self.repo.save(self.responsable)

        self.cmd = AssignerResponsableDeNotesCommand(
            code_unite_enseignement="LDROI1001",
            annee_unite_enseignement=2020,
            matricule_fgs_enseignant="00321234"
        )

        self.attribution_translator = AttributionEnseignantTranslatorInMemory()

        self.addCleanup(lambda *args, **kwargs: self.repo.entities.clear())
        self.__mock_service_bus()

    def __mock_service_bus(self):
        message_bus_patcher = mock.patch.multiple(
            'infrastructure.messages_bus',
            ResponsableDeNotesRepository=lambda: self.repo,
            AttributionEnseignantTranslator=lambda: self.attribution_translator,
        )
        message_bus_patcher.start()
        self.addCleanup(message_bus_patcher.stop)

        self.message_bus = message_bus_instance

    def test_cannot_assigner_enseignant_en_tant_que_responsable_de_notes_pour_unite_enseignement_non_attribuee(self):
        cmd = attr.evolve(self.cmd, code_unite_enseignement='LOSIS7896')

        with self.assertRaises(EnseignantNonAttribueUniteEnseignementException):
            self.message_bus.invoke(cmd)

    def test_should_desassigner_responsable_de_notes_actuelle_de_unite_enseignement(self):
        self.message_bus.invoke(self.cmd)

        self.assertSetEqual(self.responsable.unites_enseignements, set())

    def test_should_assigner_responsable_de_notes_pour_enseignant_non_encore_responsable_de_notes(self):
        entity_id = self.message_bus.invoke(self.cmd)

        responsable_retrieved = self.repo.get(entity_id)
        self.assertTrue(
            responsable_retrieved.is_responsable_unite_enseignement(
                self.cmd.code_unite_enseignement,
                self.cmd.annee_unite_enseignement
            )
        )

    def test_should_assigner_responsable_de_notes_pour_enseignant_deja_responsable_de_notes(self):
        responsable = ResponsableDeNotesPourMultipleUniteEnseignements()
        self.repo.save(responsable)
        cmd = attr.evolve(self.cmd, matricule_fgs_enseignant=responsable.matricule_fgs_enseignant)

        entity_id = self.message_bus.invoke(cmd)

        responsable_retrieved = self.repo.get(entity_id)
        self.assertTrue(responsable, responsable_retrieved)
        self.assertTrue(
            responsable_retrieved.is_responsable_unite_enseignement(
                self.cmd.code_unite_enseignement,
                self.cmd.annee_unite_enseignement
            )
        )
