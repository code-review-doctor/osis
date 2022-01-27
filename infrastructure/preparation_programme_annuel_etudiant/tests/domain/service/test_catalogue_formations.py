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

from django.test import SimpleTestCase

from ddd.logic.preparation_programme_annuel_etudiant.commands import GetFormationCommand


class CatalogueFormationsTranslatorTest(SimpleTestCase):

    def setUp(self) -> None:
        # mock appel service bus => retour GetProgramTreeVersionCommand : ProgramTreeVersionFactory()
        # self.patch_message_bus = mock.patch(
        #     "infrastructure.messages_bus.invoke",
        #     side_effect=self.__mock_message_bus_invoke
        # )
        # self.message_bus_mocked = self.patch_message_bus.start()
        # self.addCleanup(self.patch_message_bus.stop)
        pass

    def __mock_message_bus_invoke(self, cmd):
        if isinstance(cmd, GetFormationCommand):
            # return ProgramTreeVersionFactory(entity_id__version_name="")
            pass

    def test_should_convertir_version_standard(self):
        pass
