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
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase

from base.models.enums.academic_calendar_type import AcademicCalendarTypes
from base.tests.factories.academic_calendar import OpenAcademicCalendarFactory
from ddd.logic.application.domain.model.application_calendar import ApplicationCalendar
from ddd.logic.shared_kernel.academic_year.domain.model.academic_year import AcademicYearIdentity
from infrastructure.application.repository.application_calendar import ApplicationCalendarRepository


class ApplicationCalendarRepositoryGetCurrentCalendar(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.repository = ApplicationCalendarRepository()

    def test_get_assert_return_not_found(self):
        with self.assertRaises(ObjectDoesNotExist):
            self.repository.get_current_application_calendar()

    def test_get_assert_return_instance(self):
        academic_calendar_db = OpenAcademicCalendarFactory(
            reference=AcademicCalendarTypes.TEACHING_CHARGE_APPLICATION.name
        )

        application_calendar = self.repository.get_current_application_calendar()

        self.assertIsInstance(application_calendar, ApplicationCalendar)
        self.assertEqual(application_calendar.start_date, academic_calendar_db.start_date)
        self.assertEqual(application_calendar.end_date,  academic_calendar_db.end_date)
        self.assertEqual(
            application_calendar.authorized_target_year,
            AcademicYearIdentity(year=academic_calendar_db.data_year.year)
        )
