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

from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase
from django.test.utils import override_settings

from base.models import academic_year
from base.models import session_exam_calendar
from base.models.enums import number_session
from base.models.enums.academic_calendar_type import AcademicCalendarTypes
from base.models.session_exam_calendar import get_number_session_by_academic_calendar
from base.tests.factories.academic_calendar import AcademicCalendarFactory
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.offer_year_calendar import OfferYearCalendarFactory
from base.tests.factories.session_exam_calendar import SessionExamCalendarFactory


class SessionExamCalendarTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        AcademicYearFactory.produce_in_past()

        cls.current_academic_yr = academic_year.current_academic_year()
        next_year = cls.current_academic_yr.year + 1
        cls.academic_calendar_2 = AcademicCalendarFactory(title="Submission of score encoding - 2",
                                                          start_date=datetime.date(next_year, 3, 15),
                                                          end_date=datetime.date(next_year, 6, 28),
                                                          data_year=cls.current_academic_yr,
                                                          reference=AcademicCalendarTypes.SCORES_EXAM_SUBMISSION.name)
        cls.academic_calendar_3 = AcademicCalendarFactory(title="Submission of score encoding - 3",
                                                          start_date=datetime.date(next_year, 8, 1),
                                                          end_date=datetime.date(next_year, 9, 29),
                                                          data_year=cls.current_academic_yr,
                                                          reference=AcademicCalendarTypes.SCORES_EXAM_SUBMISSION.name)
        cls.academic_calendar_4 = AcademicCalendarFactory(title="Deliberation session 1",
                                                          start_date=datetime.date(next_year, 1, 1),
                                                          end_date=datetime.date(next_year, 1, 2),
                                                          data_year=cls.current_academic_yr,
                                                          reference=AcademicCalendarTypes.DELIBERATION.name)

    def setUp(self):
        self.academic_calendar_1 = AcademicCalendarFactory(title="Submission of score encoding - 1",
                                                           start_date=datetime.date(self.current_academic_yr.year, 10,
                                                                                    15),
                                                           end_date=datetime.date(self.current_academic_yr.year + 1, 1,
                                                                                  1),
                                                           data_year=self.current_academic_yr,
                                                           reference=AcademicCalendarTypes.SCORES_EXAM_SUBMISSION.name)

    def test_number_exam_session_out_of_range(self):
        session_exam_calendar = SessionExamCalendarFactory.build(academic_calendar=self.academic_calendar_1,
                                                                 number_session=5)
        with self.assertRaises(ValidationError):
            session_exam_calendar.full_clean()

    def test_valid_number_exam_session(self):
        session_exam_calendar = SessionExamCalendarFactory.build(academic_calendar=self.academic_calendar_1,
                                                                 number_session=number_session.ONE)
        session_exam_calendar.full_clean()
        session_exam_calendar.save()

    def test_duplicate_exam_session(self):
        SessionExamCalendarFactory(academic_calendar=self.academic_calendar_1, number_session=number_session.ONE)
        with self.assertRaises(IntegrityError):
            SessionExamCalendarFactory(academic_calendar=self.academic_calendar_1, number_session=number_session.ONE)

    def test_get_latest_session_exam(self):
        #
        first = SessionExamCalendarFactory(academic_calendar=self.academic_calendar_1,
                                           number_session=number_session.ONE)
        second = SessionExamCalendarFactory(academic_calendar=self.academic_calendar_2,
                                            number_session=number_session.TWO)
        third = SessionExamCalendarFactory(academic_calendar=self.academic_calendar_3,
                                           number_session=number_session.THREE)

        self.assertIsNone(
            session_exam_calendar.get_latest_session_exam(date=datetime.date(self.current_academic_yr.year, 11, 15)))

        result = session_exam_calendar.get_latest_session_exam(
            date=datetime.date(self.current_academic_yr.year + 1, 2, 10)
        )
        self.assertEqual(first.academic_calendar.start_date, result.start_date)
        self.assertEqual(first.academic_calendar.end_date, result.end_date)
        self.assertEqual(first.number_session, result.session)

        result = session_exam_calendar.get_latest_session_exam(
            date=datetime.date(self.current_academic_yr.year + 1, 8, 15)
        )
        self.assertEqual(second.academic_calendar.start_date, result.start_date)
        self.assertEqual(second.academic_calendar.end_date, result.end_date)
        self.assertEqual(second.number_session, result.session)

        result = session_exam_calendar.get_latest_session_exam(
            date=datetime.date(self.current_academic_yr.year + 2, 2, 2)
        )
        self.assertEqual(third.academic_calendar.start_date, result.start_date)
        self.assertEqual(third.academic_calendar.end_date, result.end_date)
        self.assertEqual(third.number_session, result.session)

    def test_get_closest_new_session_exam(self):
        first = SessionExamCalendarFactory(academic_calendar=self.academic_calendar_1,
                                           number_session=number_session.ONE)
        second = SessionExamCalendarFactory(academic_calendar=self.academic_calendar_2,
                                            number_session=number_session.TWO)
        third = SessionExamCalendarFactory(academic_calendar=self.academic_calendar_3,
                                           number_session=number_session.THREE)

        self.assertIsNone(session_exam_calendar.get_closest_new_session_exam(
            date=datetime.date(self.current_academic_yr.year + 1, 10, 16)))

        result = session_exam_calendar.get_closest_new_session_exam(
            date=datetime.date(self.current_academic_yr.year, 9, 15)
        )
        self.assertEqual(first.academic_calendar.start_date, result.start_date)
        self.assertEqual(first.academic_calendar.end_date, result.end_date)
        self.assertEqual(first.number_session, result.session)

        result = session_exam_calendar.get_closest_new_session_exam(
            date=datetime.date(self.current_academic_yr.year + 1, 3, 14)
        )
        self.assertEqual(second.academic_calendar.start_date, result.start_date)
        self.assertEqual(second.academic_calendar.end_date, result.end_date)
        self.assertEqual(second.number_session, result.session)

        result = session_exam_calendar.get_closest_new_session_exam(
            date=datetime.date(self.current_academic_yr.year + 1, 7, 30)
        )
        self.assertEqual(third.academic_calendar.start_date, result.start_date)
        self.assertEqual(third.academic_calendar.end_date, result.end_date)
        self.assertEqual(third.number_session, result.session)

    def test_get_number_session_by_academic_calendar_empty(self):
        number = get_number_session_by_academic_calendar(self.academic_calendar_1)
        self.assertEqual(number, None)

    def test_get_number_session_by_academic_calendar(self):
        SessionExamCalendarFactory(academic_calendar=self.academic_calendar_1,
                                   number_session=number_session.ONE)
        number = get_number_session_by_academic_calendar(self.academic_calendar_1)
        self.assertEqual(number, number_session.ONE)
