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

from django.test import SimpleTestCase

from ddd.logic.shared_kernel.language.commands import GetLanguageCommand
from ddd.logic.shared_kernel.language.tests.factory.language import FRLanguageFactory
from ddd.logic.shared_kernel.language.use_case.read import get_language_service
from infrastructure.shared_kernel.language.repository.in_memory.language import LanguageRepository


class TestGetLanguageService(SimpleTestCase):

    def setUp(self):
        self.language_repository = LanguageRepository()
        self.language = FRLanguageFactory()
        self.language_repository.save(self.language)
        self.command = GetLanguageCommand(code_iso=self.language.entity_id.code_iso)

    def test_should_return_french_language(self):
        language = get_language_service.get_language(
            self.command,
            self.language_repository,
        )
        self.assertEqual(language, self.language)
        self.assertEqual(language.entity_id, self.language.entity_id)
        self.assertEqual(language.name, self.language.name)
