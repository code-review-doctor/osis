#############################################################################
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

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from assessments.api.views.assessments import CurrentSessionExamView
from base.models.enums import number_session
from base.tests.factories.academic_calendar import AcademicCalendarExamSubmissionFactory
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.session_exam_calendar import SessionExamCalendarFactory
from base.tests.factories.tutor import TutorFactory
from django.utils.translation import gettext_lazy as _


class CurrentSessionAPIViewTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.tutor = TutorFactory()
        cls.academic_year = AcademicYearFactory(current=True)
        cls.academic_calendar = AcademicCalendarExamSubmissionFactory(title="Submission of score encoding - 1",
                                                                      data_year=cls.academic_year)
        cls.session_exam = SessionExamCalendarFactory(academic_calendar=cls.academic_calendar, number_session=number_session.ONE)

        cls.url = reverse('assessments_api_v1:' + CurrentSessionExamView.name)

    def setUp(self):
        self.client.force_authenticate(user=self.tutor.person.user)

    def test_get_not_authorized(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_response(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('application/json', response['content-type'])

        result = response.json()
        self.assertEqual(result.get('month_session_name'), _('January'))
        self.assertEqual(result.get('year'), self.academic_year.year)
        formatted_date = datetime.datetime.strptime(result.get('start_date'), "%Y-%m-%d").date()
        self.assertEqual(formatted_date, self.academic_calendar.start_date)
        formatted_date = datetime.datetime.strptime(result.get('end_date'), "%Y-%m-%d").date()
        self.assertEqual(formatted_date, self.academic_calendar.end_date)
