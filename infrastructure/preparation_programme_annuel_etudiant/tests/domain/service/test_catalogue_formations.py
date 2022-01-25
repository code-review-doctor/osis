##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2022 Université catholique de Louvain (http://www.uclouvain.be)
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
from unittest import mock

from django.test import SimpleTestCase

from ddd.logic.preparation_programme_annuel_etudiant.commands import GetFormationCommand
from infrastructure.preparation_programme_annuel_etudiant.domain.service.catalogue_formations import \
    CatalogueFormationsTranslator
from infrastructure.preparation_programme_annuel_etudiant.domain.service.in_memory.catalogue_formations import \
    CatalogueFormationsTranslatorInMemory


class CatalogueFormationsTranslatorTest(SimpleTestCase):

    def setUp(self) -> None:
        self.translator = CatalogueFormationsTranslator()
        self.patch_message_bus = mock.patch(
            "infrastructure.utils.MessageBus.invoke",
            side_effect=self.__mock_message_bus_invoke
        )
        self.message_bus_mocked = self.patch_message_bus.start()
        self.addCleanup(self.patch_message_bus.stop)
        self.ECGE1BA_dto = CatalogueFormationsTranslatorInMemory.dtos[0]

    def __mock_message_bus_invoke(self, cmd):
        if isinstance(cmd, GetFormationCommand):
            return self.ECGE1BA_dto

    def test_should_convertir_version_standard(self):
        formation_dto = self.translator.get_formation(
            sigle=self.ECGE1BA_dto.sigle,
            annee=self.ECGE1BA_dto.annee,
            version=self.ECGE1BA_dto.version,
            transition_name=''
        )
        self.assertEqual(formation_dto, self.ECGE1BA_dto)
