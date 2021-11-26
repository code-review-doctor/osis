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

from django.conf import settings
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from rest_framework import status
from rest_framework.test import APITestCase

from base.tests.factories.offer_enrollment import OfferEnrollmentFactory
from base.tests.factories.student import StudentFactory
from education_group.tests.factories.first_year_bachelor import FirstYearBachelorFactory
from offer_enrollment.api.views.enrollment import MyOfferEnrollmentsListView, OfferEnrollmentsListView


class MyOfferEnrollmentsListViewTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.offer_enrollment = OfferEnrollmentFactory()
        cls.student = cls.offer_enrollment.student
        cls.url = reverse('offer_enrollment_api_v1:' + MyOfferEnrollmentsListView.name)

    def setUp(self):
        self.client.force_authenticate(user=self.student.person.user)

    def test_get_not_authorized(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_method_not_allowed(self):
        methods_not_allowed = ['post', 'delete', 'put', 'patch']

        for method in methods_not_allowed:
            response = getattr(self.client, method)(self.url)
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_results_assert_key(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.json()['results']
        self.assertEqual(len(results), 1)

        self.assertCountEqual(list(results[0].keys()), ["acronym", "year", "title", "student_registration_id"])

    def test_get_results_assert_acronym_11ba_is_correct(self):
        cohort = FirstYearBachelorFactory()
        offer_enrollment_11ba = OfferEnrollmentFactory(
            cohort_year=cohort,
            education_group_year=cohort.education_group_year
        )
        self.client.force_authenticate(user=offer_enrollment_11ba.student.person.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.json()['results']
        self.assertEqual(len(results), 1)

        self.assertEqual(results[0]['acronym'], cohort.education_group_year.acronym.replace('1', '11'))


class OfferEnrollmentsListViewTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.offer_enrollment = OfferEnrollmentFactory()
        cls.student = cls.offer_enrollment.student
        cls.url = reverse(
            'offer_enrollment_api_v1:' + OfferEnrollmentsListView.name,
            kwargs={'global_id': cls.student.person.global_id}
        )

    def setUp(self):
        self.client.force_authenticate(user=self.student.person.user)

    def test_get_not_authorized(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_method_not_allowed(self):
        methods_not_allowed = ['post', 'delete', 'put', 'patch']

        for method in methods_not_allowed:
            response = getattr(self.client, method)(self.url)
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_results_assert_key(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.json()['results']
        self.assertEqual(len(results), 1)

        self.assertCountEqual(list(results[0].keys()), ["acronym", "year", "title", "student_registration_id"])

    def test_raise_exception_if_double_noma_for_last_valid_offer_enrollments_year(self):
        other_student = StudentFactory(person=self.student.person)
        OfferEnrollmentFactory(
            education_group_year__academic_year=self.offer_enrollment.education_group_year.academic_year,
            student=other_student
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        expected_message = _(
            "A problem was detected with your registration : 2 registration id's are linked to your user.</br> Please "
            "contact <a href=\"{registration_department_url}\" "
            "target=\"_blank\">the Registration department</a>. Thank you."
        ).format(registration_department_url=settings.REGISTRATION_ADMINISTRATION_URL)
        self.assertEqual(response.json()['non_field_errors'][0]['detail'], expected_message)

    def test_get_results_assert_acronym_11ba_is_correct(self):
        cohort = FirstYearBachelorFactory(
            education_group_year__academic_year=self.offer_enrollment.education_group_year.academic_year
        )
        offer_enrollment_11ba = OfferEnrollmentFactory(
            cohort_year=cohort,
            education_group_year=cohort.education_group_year
        )
        url = reverse(
            'offer_enrollment_api_v1:' + OfferEnrollmentsListView.name,
            kwargs={'global_id': offer_enrollment_11ba.student.person.global_id}
        )
        self.client.force_authenticate(user=offer_enrollment_11ba.student.person.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.json()['results']
        self.assertEqual(len(results), 1)

        self.assertCountEqual(list(results[0]['acronym']), cohort.education_group_year.acronym.replace('1', '11'))

    def test_get_404_for_bad_global_id(self):
        url = reverse(
            'offer_enrollment_api_v1:' + OfferEnrollmentsListView.name,
            kwargs={'global_id': self.student.person.global_id + '2'}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
