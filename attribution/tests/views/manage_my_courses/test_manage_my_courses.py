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
import datetime

import mock
from django.http import HttpResponseForbidden, HttpResponse, HttpResponseNotAllowed
from django.test import TestCase
from django.urls import reverse

from attribution.tests.factories.attribution_charge_new import AttributionChargeNewFactory
from base.models.enums.academic_calendar_type import AcademicCalendarTypes
from base.tests.factories.academic_calendar import OpenAcademicCalendarFactory
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.teaching_material import TeachingMaterialFactory
from base.tests.factories.tutor import TutorFactory


class TestTutorCreateTeachingMaterial(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.tutor = TutorFactory()
        cls.academic_year = AcademicYearFactory(current=True)

        cls.learning_unit_year = LearningUnitYearFactory(academic_year=cls.academic_year, summary_locked=False)
        cls.attribution = AttributionChargeNewFactory(
            attribution__tutor=cls.tutor,
            attribution__learning_container_year=cls.learning_unit_year.learning_container_year,
            learning_component_year__learning_unit_year=cls.learning_unit_year,
        )
        cls.url = reverse("tutor_teaching_material_create", args=[cls.learning_unit_year.id])

    def setUp(self):
        self.calendar_row = OpenAcademicCalendarFactory(
            reference=AcademicCalendarTypes.SUMMARY_COURSE_SUBMISSION.name,
            data_year=self.learning_unit_year.academic_year
        )
        self.client.force_login(self.tutor.person.user)

    def test_user_not_logged(self):
        self.client.logout()
        response = self.client.get(self.url)

        self.assertRedirects(response, '/login/?next={}'.format(self.url))

    def test_user_has_not_permission(self):
        self.client.force_login(PersonFactory().user)
        response = self.client.get(self.url)

        self.assertTemplateUsed(response, "access_denied.html")
        self.assertEqual(response.status_code, HttpResponseForbidden.status_code)

    def test_summary_course_submission_calendar_is_closed(self):
        self.calendar_row.start_date = datetime.date.today() - datetime.timedelta(days=3)
        self.calendar_row.end_date = datetime.date.today() - datetime.timedelta(days=1)
        self.calendar_row.save()

        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "access_denied.html")
        self.assertEqual(response.status_code, HttpResponseForbidden.status_code)

    def test_assert_method_not_allowed(self):
        methods_not_allowed = ['delete', 'put', 'patch']

        for method in methods_not_allowed:
            response = getattr(self.client, method)(self.url)
            self.assertTemplateUsed(response, "method_not_allowed.html")
            self.assertEqual(response.status_code, HttpResponseNotAllowed.status_code)

    @mock.patch('attribution.views.manage_my_courses.manage_my_courses.teaching_material.create_view',
                return_value=HttpResponse())
    def test_assert_get_http_call_teachning_material_create_view(self, mock_teachning_material_create_view):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertTrue(mock_teachning_material_create_view.called)

    @mock.patch('attribution.views.manage_my_courses.manage_my_courses.teaching_material.create_view',
                return_value=HttpResponse())
    def test_assert_post_http_call_teachning_material_create_view(self, mock_teachning_material_create_view):
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertTrue(mock_teachning_material_create_view.called)


class TestTutorUpdateTeachingMaterial(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.tutor = TutorFactory()
        cls.academic_year = AcademicYearFactory(current=True)

        cls.learning_unit_year = LearningUnitYearFactory(academic_year=cls.academic_year, summary_locked=False)
        cls.teaching_material = TeachingMaterialFactory(learning_unit_year=cls.learning_unit_year)
        cls.attribution = AttributionChargeNewFactory(
            attribution__tutor=cls.tutor,
            attribution__learning_container_year=cls.learning_unit_year.learning_container_year,
            learning_component_year__learning_unit_year=cls.learning_unit_year,
        )
        cls.url = reverse('tutor_teaching_material_edit', kwargs={
            'learning_unit_year_id': cls.learning_unit_year.pk,
            'teaching_material_id': cls.teaching_material.pk
        })

    def setUp(self):
        self.calendar_row = OpenAcademicCalendarFactory(
            reference=AcademicCalendarTypes.SUMMARY_COURSE_SUBMISSION.name,
            data_year=self.learning_unit_year.academic_year
        )
        self.client.force_login(self.tutor.person.user)

    def test_user_not_logged(self):
        self.client.logout()
        response = self.client.get(self.url)

        self.assertRedirects(response, '/login/?next={}'.format(self.url))

    def test_user_has_not_permission(self):
        self.client.force_login(PersonFactory().user)
        response = self.client.get(self.url)

        self.assertTemplateUsed(response, "access_denied.html")
        self.assertEqual(response.status_code, HttpResponseForbidden.status_code)

    def test_summary_course_submission_calendar_is_closed(self):
        self.calendar_row.start_date = datetime.date.today() - datetime.timedelta(days=3)
        self.calendar_row.end_date = datetime.date.today() - datetime.timedelta(days=1)
        self.calendar_row.save()

        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "access_denied.html")
        self.assertEqual(response.status_code, HttpResponseForbidden.status_code)

    def test_assert_method_not_allowed(self):
        methods_not_allowed = ['delete', 'put', 'patch']

        for method in methods_not_allowed:
            response = getattr(self.client, method)(self.url)
            self.assertTemplateUsed(response, "method_not_allowed.html")
            self.assertEqual(response.status_code, HttpResponseNotAllowed.status_code)

    @mock.patch('attribution.views.manage_my_courses.manage_my_courses.teaching_material.update_view',
                return_value=HttpResponse())
    def test_assert_get_http_call_teachning_material_update_view(self, mock_teachning_material_update_view):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertTrue(mock_teachning_material_update_view.called)

    @mock.patch('attribution.views.manage_my_courses.manage_my_courses.teaching_material.update_view',
                return_value=HttpResponse())
    def test_assert_post_http_call_teachning_material_update_view(self, mock_teachning_material_update_view):
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertTrue(mock_teachning_material_update_view.called)


class TestTutorDeleteTeachingMaterial(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.tutor = TutorFactory()
        cls.academic_year = AcademicYearFactory(current=True)

        cls.learning_unit_year = LearningUnitYearFactory(academic_year=cls.academic_year, summary_locked=False)
        cls.teaching_material = TeachingMaterialFactory(learning_unit_year=cls.learning_unit_year)
        cls.attribution = AttributionChargeNewFactory(
            attribution__tutor=cls.tutor,
            attribution__learning_container_year=cls.learning_unit_year.learning_container_year,
            learning_component_year__learning_unit_year=cls.learning_unit_year,
        )
        cls.url = reverse('tutor_teaching_material_delete', kwargs={
            'learning_unit_year_id': cls.learning_unit_year.pk,
            'teaching_material_id': cls.teaching_material.pk
        })

    def setUp(self):
        self.calendar_row = OpenAcademicCalendarFactory(
            reference=AcademicCalendarTypes.SUMMARY_COURSE_SUBMISSION.name,
            data_year=self.learning_unit_year.academic_year
        )
        self.client.force_login(self.tutor.person.user)

    def test_user_not_logged(self):
        self.client.logout()
        response = self.client.get(self.url)

        self.assertRedirects(response, '/login/?next={}'.format(self.url))

    def test_user_has_not_permission(self):
        self.client.force_login(PersonFactory().user)
        response = self.client.get(self.url)

        self.assertTemplateUsed(response, "access_denied.html")
        self.assertEqual(response.status_code, HttpResponseForbidden.status_code)

    def test_summary_course_submission_calendar_is_closed(self):
        self.calendar_row.start_date = datetime.date.today() - datetime.timedelta(days=3)
        self.calendar_row.end_date = datetime.date.today() - datetime.timedelta(days=1)
        self.calendar_row.save()

        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "access_denied.html")
        self.assertEqual(response.status_code, HttpResponseForbidden.status_code)

    def test_assert_method_not_allowed(self):
        methods_not_allowed = ['delete', 'put', 'patch']

        for method in methods_not_allowed:
            response = getattr(self.client, method)(self.url)
            self.assertTemplateUsed(response, "method_not_allowed.html")
            self.assertEqual(response.status_code, HttpResponseNotAllowed.status_code)

    @mock.patch('attribution.views.manage_my_courses.manage_my_courses.teaching_material.delete_view',
                return_value=HttpResponse())
    def test_assert_get_http_call_teachning_material_delete_view(self, mock_teachning_material_delete_view):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertTrue(mock_teachning_material_delete_view.called)

    @mock.patch('attribution.views.manage_my_courses.manage_my_courses.teaching_material.delete_view',
                return_value=HttpResponse())
    def test_assert_post_http_call_teachning_material_delete_view(self, mock_teachning_material_delete_view):
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertTrue(mock_teachning_material_delete_view.called)
