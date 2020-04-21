##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.test import TestCase

from base.business.education_groups.perms import check_permission
from base.models.academic_calendar import get_academic_calendar_by_date_and_reference_and_data_year
from base.models.enums import academic_calendar_type
from base.tests.factories.academic_calendar import AcademicCalendarFactory
from base.tests.factories.academic_year import create_current_academic_year
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.person import PersonFactory, PersonWithPermissionsFactory

from django.utils.functional import cached_property

class TestPerms(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.current_academic_year = create_current_academic_year()
        cls.education_group_year = EducationGroupYearFactory(academic_year=cls.current_academic_year)

    def test_has_person_the_right_to_add_education_group(self):
        person_without_right = PersonFactory()
        self.assertFalse(check_permission(person_without_right, "base.add_educationgroup"))

        person_with_right = PersonWithPermissionsFactory("add_educationgroup")
        self.assertTrue(check_permission(person_with_right, "base.add_educationgroup"))

    def test_is_education_group_edit_period_opened_case_period_closed(self):
        today = datetime.date.today()

        AcademicCalendarFactory(
            start_date=today + datetime.timedelta(days=1),
            end_date=today + datetime.timedelta(days=3),
            academic_year=self.current_academic_year,
            data_year=self.current_academic_year,
            reference=academic_calendar_type.EDUCATION_GROUP_EDITION,
        )
        self.assertIsNone(get_academic_calendar_by_date_and_reference_and_data_year(
                self.education_group_year.academic_year, academic_calendar_type.EDUCATION_GROUP_EDITION))

    def test_is_education_group_edit_period_opened_case_period_opened(self):
        today = datetime.date.today()

        aca_calendar = AcademicCalendarFactory(
            start_date=today - datetime.timedelta(days=1),
            end_date=today + datetime.timedelta(days=3),
            academic_year=self.current_academic_year,
            data_year=self.current_academic_year,
            reference=academic_calendar_type.EDUCATION_GROUP_EDITION,
        )
        self.assertEqual(aca_calendar, get_academic_calendar_by_date_and_reference_and_data_year(
            self.education_group_year.academic_year, academic_calendar_type.EDUCATION_GROUP_EDITION))

    def test_is_education_group_edit_period_opened_case_period_opened_but_not_same_academic_year(self):
        today = datetime.date.today()
        EducationGroupYearFactory(academic_year__year=self.current_academic_year.year + 1)

        AcademicCalendarFactory(
            start_date=today - datetime.timedelta(days=1),
            end_date=today + datetime.timedelta(days=3),
            academic_year=self.current_academic_year,
            data_year__year=self.current_academic_year.year+1,
            reference=academic_calendar_type.EDUCATION_GROUP_EDITION,
        )
        self.assertIsNone(get_academic_calendar_by_date_and_reference_and_data_year(
            self.education_group_year.academic_year, academic_calendar_type.EDUCATION_GROUP_EDITION))
