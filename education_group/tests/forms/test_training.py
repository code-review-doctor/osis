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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.test import TestCase

from base.models.enums.academic_calendar_type import AcademicCalendarTypes
from base.models.enums.education_group_types import TrainingType
from base.tests.factories.academic_calendar import OpenAcademicCalendarFactory, CloseAcademicCalendarFactory
from education_group.forms.training import CreateTrainingForm
from education_group.tests.factories.auth.central_manager import CentralManagerFactory
from education_group.tests.factories.auth.faculty_manager import FacultyManagerFactory
from reference.tests.factories.language import FrenchLanguageFactory


class TestCreateTrainingForm(TestCase):
    def setUp(self) -> None:
        for year in range(2020, 2025):
            OpenAcademicCalendarFactory(
                data_year__year=year,
                reference=AcademicCalendarTypes.EDUCATION_GROUP_EXTENDED_DAILY_MANAGEMENT.name
            )
        CloseAcademicCalendarFactory(
            data_year__year=2026,
            reference=AcademicCalendarTypes.EDUCATION_GROUP_EXTENDED_DAILY_MANAGEMENT.name
        )

        OpenAcademicCalendarFactory(data_year__year=2021, reference=AcademicCalendarTypes.EDUCATION_GROUP_EDITION.name)
        CloseAcademicCalendarFactory(data_year__year=2022, reference=AcademicCalendarTypes.EDUCATION_GROUP_EDITION.name)

        FrenchLanguageFactory()

    def test_assert_academic_years_available_for_faculty_manager(self):
        faculty_manager = FacultyManagerFactory()
        form = CreateTrainingForm(
            user=faculty_manager.person.user,
            training_type=TrainingType.BACHELOR.name,
            attach_path=None,
            training=None
        )

        self.assertQuerysetEqual(
            form.fields['academic_year'].queryset,
            [2021],
            transform=lambda obj: obj.year
        )

    def test_assert_academic_years_available_for_central_manager(self):
        central_manager = CentralManagerFactory()
        form = CreateTrainingForm(
            user=central_manager.person.user,
            training_type=TrainingType.BACHELOR.name,
            attach_path=None,
            training=None
        )

        self.assertQuerysetEqual(
            form.fields['academic_year'].queryset,
            [2024, 2023, 2022, 2021, 2020],
            transform=lambda obj: obj.year
        )
