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
from django.test import TestCase
from django.urls import reverse

from assessments.forms.score_file import ScoreFileForm
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.session_exam_calendar import SessionExamCalendarFactory
from base.tests.factories.tutor import TutorFactory


class ScoreSheetXLSImportViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.tutor = TutorFactory(person__global_id="123456789")
        cls.academic_year = AcademicYearFactory()

        cls.url = reverse('score_sheet_xls_import', kwargs={
            'learning_unit_code': 'LEPL1509'
        })

    def setUp(self) -> None:
        self.client.force_login(self.tutor.person.user)
        self.session_exam_calendar = SessionExamCalendarFactory.create_academic_event(self.academic_year)

    def test_case_user_not_logged(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, '/login/?next={}'.format(self.url))

    def test_case_period_closed_assert_redirect_to_outside_period_view(self):
        self.session_exam_calendar.academic_calendar.delete()
        self.session_exam_calendar.delete()

        response = self.client.get(self.url)

        expected_redirect_url = reverse('outside_scores_encodings_period')
        self.assertRedirects(response, expected_redirect_url)

    def test_assert_template_used(self):
        response = self.client.get(self.url)

        self.assertTemplateUsed(response, "assessments/common/xls_import_modal_inner.html")

    def test_assert_contexts(self):
        response = self.client.get(self.url)
        self.assertIsInstance(response.context['form'], ScoreFileForm)
