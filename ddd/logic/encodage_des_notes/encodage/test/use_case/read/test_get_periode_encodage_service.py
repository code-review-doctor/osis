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
from unittest import mock

from django.test import SimpleTestCase

from ddd.logic.encodage_des_notes.encodage.commands import GetPeriodeEncodageCommand
from ddd.logic.encodage_des_notes.shared_kernel.domain.service.i_periode_encodage_notes import \
    IPeriodeEncodageNotesTranslator
from infrastructure.messages_bus import message_bus_instance


class GetPeriodeEncodageTest(SimpleTestCase):

    def setUp(self) -> None:
        self.cmd = GetPeriodeEncodageCommand()

        self.translator_mocked = mock.Mock(spec=IPeriodeEncodageNotesTranslator)
        message_bus_patcher = mock.patch.multiple(
            'infrastructure.messages_bus',
            PeriodeEncodageNotesTranslator=self.translator_mocked
        )
        message_bus_patcher.start()
        self.addCleanup(message_bus_patcher.stop)
        self.message_bus = message_bus_instance

    def test_should_call_get_method_translator(self):
        self.message_bus.invoke(self.cmd)
        self.assertTrue(self.translator_mocked.return_value.get.called)
