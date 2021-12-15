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

from django.test import TestCase

from base.models.learning_unit_year import LearningUnitYear
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.external_learning_unit_year import ExternalLearningUnitYearFactory
from base.tests.factories.learning_unit_year import LearningUnitYearWithComponentsFactory
from learning_unit.postponement.postpone_learning_units import PostponeLearningUnits


class TestPostponeLearningUnits(TestCase):
    @classmethod
    def setUpTestData(cls):
        AcademicYearFactory.produce(number_past=1, number_future=8)
        cls.current_academic_year = AcademicYearFactory(current=True)

    def setUp(self) -> None:
        self.luy = LearningUnitYearWithComponentsFactory(academic_year__current=True)

    def test_should_exclude_mobility_from_postponement(self):
        external_luy = ExternalLearningUnitYearFactory(
            learning_unit_year__academic_year__current=True,
            mobility=True
        ).learning_unit_year

        PostponeLearningUnits().postpone()

        self.assertQuerysetEqual(
            LearningUnitYear.objects.filter(acronym=external_luy.acronym),
            [external_luy.academic_year.year],
            transform=lambda luy: luy.academic_year.year
        )

    def test_should_postpone_until_learning_unit_end_year_if_less_than_postponement_max_year(self):
        self.luy.learning_unit.end_year = AcademicYearFactory(year=self.current_academic_year.year + 2)
        self.luy.learning_unit.save()

        PostponeLearningUnits().postpone()

        self.assertQuerysetEqual(
            LearningUnitYear.objects.filter(acronym=self.luy.acronym),
            list(range(self.current_academic_year.year, self.current_academic_year.year + 3)),
            transform=lambda luy: luy.academic_year.year
        )

    def test_should_postpone_luy_until_n_plus_6(self):
        PostponeLearningUnits().postpone()

        self.assertQuerysetEqual(
            LearningUnitYear.objects.filter(acronym=self.luy.acronym),
            list(range(self.current_academic_year.year, self.current_academic_year.year + 7)),
            transform=lambda luy: luy.academic_year.year
        )
