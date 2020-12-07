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
from django.core.exceptions import PermissionDenied
from django.test import TestCase
from django.utils.translation import gettext_lazy as _

from base.models.enums import academic_calendar_type
from base.tests.factories.academic_calendar import OpenAcademicCalendarFactory
from base.tests.factories.academic_year import create_current_academic_year
from education_group.calendar.education_group_edition_process_calendar import EducationGroupEditionCalendar


class TestEventPermGroupYearEditionPerms(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.current_academic_year = create_current_academic_year()
        OpenAcademicCalendarFactory(reference=academic_calendar_type.EDUCATION_GROUP_EDITION,
                                    academic_year=cls.current_academic_year,
                                    data_year=cls.current_academic_year)
        OpenAcademicCalendarFactory(reference=academic_calendar_type.EDUCATION_GROUP_EDITION,
                                    academic_year__year=cls.current_academic_year.year + 1,
                                    data_year__year=cls.current_academic_year.year + 1)

    def test_is_open_for_spec_egy(self):
        self.assertTrue(
            EducationGroupEditionCalendar().is_open(target_year=self.current_academic_year.year)
        )

    def test_is_open_other_rules(self):
        self.assertTrue(
            EducationGroupEditionCalendar().is_open()
        )


class TestEventPermGroupYearEditionPermsNotOpen(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.current_academic_year = create_current_academic_year()

    def test_is_not_open_for_spec_egy_without_exception_raise(self):
        self.assertFalse(
            EducationGroupEditionCalendar(raise_exception=False).is_open(target_year=self.current_academic_year.year)
        )

    def test_is_not_open_for_spec_egy_with_exception_raise(self):
        expected_exception_message = str(_("This education group is not editable during this period."))
        with self.assertRaisesMessage(PermissionDenied, expected_exception_message):
            EducationGroupEditionCalendar(raise_exception=True).is_open(target_year=self.current_academic_year.year)

    def test_is_not_open_other_rules(self):
        self.assertFalse(EducationGroupEditionCalendar(raise_exception=False).is_open())
