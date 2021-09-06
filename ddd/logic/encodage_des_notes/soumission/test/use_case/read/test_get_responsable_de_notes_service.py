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
import attr
import mock
from django.test import SimpleTestCase

from ddd.logic.encodage_des_notes.soumission.commands import GetResponsableDeNotesCommand
from ddd.logic.encodage_des_notes.soumission.dtos import ResponsableDeNotesDTO
from ddd.logic.encodage_des_notes.soumission.test.factory.responsable_de_notes import \
    ResponsableDeNotesLDROI1001Annee2020Factory
from infrastructure.encodage_de_notes.soumission.repository.in_memory.responsable_de_notes import \
    ResponsableDeNotesInMemoryRepository
from infrastructure.messages_bus import message_bus_instance


class GetResponsableDeNotesTest(SimpleTestCase):
    def setUp(self) -> None:
        self.matricule_responsable_de_notes = "123456789"
        self.resp_notes_repository = ResponsableDeNotesInMemoryRepository()
        self.resp_notes_repository.entities.clear()
        self.responsable_notes = ResponsableDeNotesLDROI1001Annee2020Factory(
            entity_id__matricule_fgs_enseignant=self.matricule_responsable_de_notes
        )
        self.resp_notes_repository.save(self.responsable_notes)

        message_bus_patcher = mock.patch.multiple(
            'infrastructure.messages_bus',
            ResponsableDeNotesRepository=lambda: self.resp_notes_repository,
        )
        message_bus_patcher.start()
        self.addCleanup(message_bus_patcher.stop)

        self.cmd = GetResponsableDeNotesCommand(code_unite_enseignement='LDROI1001', annee_unite_enseignement=2020)
        self.message_bus = message_bus_instance

    def test_should_return_responsable_note_dto(self):
        result = self.message_bus.invoke(self.cmd)

        self.assertEqual(
            result,
            ResponsableDeNotesDTO(
                nom='Chileng',
                prenom='Jean-Michel',
                matricule=self.matricule_responsable_de_notes,
                code_unite_enseignement='LDROI1001',
                annee_unite_enseignement=2020,
            )
        )

    def test_should_return_none_si_pas_trouve(self):
        cmd = attr.evolve(self.cmd, code_unite_enseignement='LAGRO1200')
        self.assertIsNone(self.message_bus.invoke(cmd))
