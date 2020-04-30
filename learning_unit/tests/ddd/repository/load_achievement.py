##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)
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

from django.test import TestCase

from base.tests.factories.learning_achievement import LearningAchievementFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from learning_unit.ddd.repository.load_achievement import load_achievements
from reference.tests.factories.language import EnglishLanguageFactory


class TestLoadAchievement(TestCase):

    @classmethod
    def setUpTestData(cls):

        cls.l_unit_1 = LearningUnitYearFactory()
        cls.en_language = EnglishLanguageFactory()
        cls.achievements = [LearningAchievementFactory(language=cls.en_language,
                                                       code_name="A_{}".format(idx),
                                                       learning_unit_year=cls.l_unit_1) for idx in range(5)]

    def test_load_achievements(self):
        results = load_achievements(self.l_unit_1.acronym, self.l_unit_1.academic_year.year, self.en_language.code)
        self.assertEqual(len(results), 5)

    def test_load_achievements_check_order(self):
        results = load_achievements(self.l_unit_1.acronym, self.l_unit_1.academic_year.year, self.en_language.code)
        for idx in range(5):
            self.assertEqual(results[idx].code_name, "A_{}".format(idx))
