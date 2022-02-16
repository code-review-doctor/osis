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
import datetime

from django.test import SimpleTestCase

from base.forms.academic_calendar.update import AcademicCalendarUpdateForm
from base.tests.factories.business.academic_calendar import AcademicEventInMemoryRepository, AcademicEventFactory, \
    AttendanceMarkSession1Factory, ScoreEncodingSession1Factory


class TesAcademicCalendarUpdateForm(SimpleTestCase):
    def setUp(self) -> None:
        self.event = AcademicEventFactory()
        self.score_encoding_event = ScoreEncodingSession1Factory()
        self.attendance_mark_event = AttendanceMarkSession1Factory()

        self.academic_year_repository = AcademicEventInMemoryRepository()
        self.academic_year_repository.events = [self.event, self.score_encoding_event, self.attendance_mark_event]

    def test_end_date_lower_than_start_date_assert_raise_exception(self):
        form = AcademicCalendarUpdateForm(
            academic_event=self.event,
            academic_event_repository=self.academic_year_repository,
            data={
                'start_date': datetime.date.today(),
                'end_date': datetime.date.today() - datetime.timedelta(days=5)
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn('end_date', form.errors)

    def test_start_date_empty_assert_raise_error_because_start_date_mandatory(self):
        form = AcademicCalendarUpdateForm(
            academic_event=self.event,
            academic_event_repository=self.academic_year_repository,
            data={
                'start_date': '',
                'end_date': ''
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn('start_date', form.errors)

    def test_assert_end_date_can_be_empty(self):
        form = AcademicCalendarUpdateForm(
            academic_event=self.event,
            academic_event_repository=self.academic_year_repository,
            data={
                'start_date': datetime.date.today(),
                'end_date': ''
            }
        )
        self.assertTrue(form.is_valid())

    def test_should_raise_validation_error_if_giving_attendance_mark_end_date_greater_than_score_submission(self):
        form = AcademicCalendarUpdateForm(
            academic_event=self.attendance_mark_event,
            academic_event_repository=self.academic_year_repository,
            data={
                'start_date': self.attendance_mark_event.start_date,
                'end_date': self.score_encoding_event.end_date + datetime.timedelta(days=1)
            }
        )
        self.assertFalse(form.is_valid())

    def test_should_raise_validation_error_if_giving_attendance_mark_start_date_lower_than_score_submission(self):
        form = AcademicCalendarUpdateForm(
            academic_event=self.attendance_mark_event,
            academic_event_repository=self.academic_year_repository,
            data={
                'start_date': self.score_encoding_event.start_date - datetime.timedelta(days=1),
                'end_date': self.attendance_mark_event.end_date
            }
        )
        self.assertFalse(form.is_valid())

    def test_should_be_valid_if_attendance_mark_dates_are_comprised_in_score_submission_period(self):
        form = AcademicCalendarUpdateForm(
            academic_event=self.attendance_mark_event,
            academic_event_repository=self.academic_year_repository,
            data={
                'start_date': self.score_encoding_event.start_date + datetime.timedelta(days=1),
                'end_date': self.score_encoding_event.end_date - datetime.timedelta(days=1)
            }
        )
        self.assertTrue(form.is_valid())
