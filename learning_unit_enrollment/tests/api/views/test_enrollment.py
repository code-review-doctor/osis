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
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from base.models.enums import offer_enrollment_state, learning_container_year_types, learning_unit_year_subtypes
from base.models.enums.learning_component_year_type import LECTURING
from base.models.learning_unit_enrollment import LearningUnitEnrollment
from base.tests.factories.academic_year import AcademicYearFactory, create_current_academic_year
from base.tests.factories.learning_container_year import LearningContainerYearFactory
from base.tests.factories.learning_unit import LearningUnitFactory
from base.tests.factories.learning_unit_enrollment import LearningUnitEnrollmentFactory
from base.tests.factories.learning_unit_year import LearningUnitYearPartimFactory, LearningUnitYearFactory, \
    LearningUnitYearFullFactory
from base.tests.factories.offer_enrollment import OfferEnrollmentFactory
from base.tests.factories.user import UserFactory
from education_group.tests.factories.first_year_bachelor import FirstYearBachelorFactory
from learning_unit.tests.factories.learning_class_year import LearningClassYearFactory
from learning_unit_enrollment.api.views.enrollment import LearningUnitEnrollmentsListView, \
    MyLearningUnitEnrollmentsListView


class LearningUnitEnrollmentsListViewTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.ue_enrollment = LearningUnitEnrollmentFactory()
        cls.url = reverse('learning_unit_enrollment_api_v1:' + LearningUnitEnrollmentsListView.name, args=[
            cls.ue_enrollment.learning_unit_year.acronym, cls.ue_enrollment.learning_unit_year.academic_year.year
        ])
        cls.user = UserFactory()

    def setUp(self):
        self.client.force_authenticate(self.user)

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

        self.assertCountEqual(list(results[0].keys()), [
            'date_enrollment',
            'enrollment_state',
            'student_last_name',
            'student_first_name',
            'student_email',
            'student_registration_id',
            'specific_profile',
            'program',
            'learning_unit_acronym',
            'learning_unit_year',
        ])

    def test_get_results_assert_acronym_class_is_correct(self):
        class_year = LearningClassYearFactory(learning_component_year__type=LECTURING)
        ue_enrollment_class = LearningUnitEnrollmentFactory(
            learning_class_year=class_year,
            learning_unit_year=class_year.learning_component_year.learning_unit_year
        )
        url = reverse('learning_unit_enrollment_api_v1:' + LearningUnitEnrollmentsListView.name, args=[
            ue_enrollment_class.learning_unit_year.acronym + class_year.acronym,
            ue_enrollment_class.learning_unit_year.academic_year.year
        ])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.json()['results']
        self.assertEqual(len(results), 1)

        self.assertEqual(
            results[0]['learning_unit_acronym'],
            "{}-{}".format(ue_enrollment_class.learning_unit_year.acronym, class_year.acronym)
        )

    def test_should_get_no_results_when_offer_enrollment_state_not_valid(self):
        offer_enrollment = OfferEnrollmentFactory(enrollment_state=offer_enrollment_state.TERMINATION)
        LearningUnitEnrollmentFactory(
            learning_unit_year__academic_year__year=offer_enrollment.education_group_year.academic_year.year,
            offer_enrollment=offer_enrollment
        )
        url = reverse('learning_unit_enrollment_api_v1:' + LearningUnitEnrollmentsListView.name, args=[
            offer_enrollment.education_group_year.acronym,
            offer_enrollment.education_group_year.academic_year.year
        ])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.json()['results']
        self.assertEqual(len(results), 0)

    def test_should_get_results_for_partim_only(self):

        learning_unit_year_full, learning_unit_year_partim1 = self._create_ue_with_partims()

        LearningUnitEnrollmentFactory(learning_unit_year=learning_unit_year_partim1)

        LearningUnitEnrollmentFactory(learning_unit_year=learning_unit_year_full)

        url = reverse('learning_unit_enrollment_api_v1:' + LearningUnitEnrollmentsListView.name, args=[
            learning_unit_year_partim1.acronym,
            learning_unit_year_partim1.academic_year.year
        ])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.json()['results']
        self.assertEqual(len(results), 1)

        self.assertEqual(
            results[0]['learning_unit_acronym'],
            "{}".format(learning_unit_year_partim1.acronym)
        )

    def test_should_get_results_for_partim_and_ue(self):
        learning_unit_year_full, learning_unit_year_partim1 = self._create_ue_with_partims()

        LearningUnitEnrollmentFactory(learning_unit_year=learning_unit_year_partim1)

        LearningUnitEnrollmentFactory(learning_unit_year=learning_unit_year_full)

        url = reverse('learning_unit_enrollment_api_v1:' + LearningUnitEnrollmentsListView.name, args=[
            learning_unit_year_full.acronym,
            learning_unit_year_full.academic_year.year
        ])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.json()['results']
        self.assertEqual(len(results), 2)

        self.assertEqual(
            results[0]['learning_unit_acronym'],
            "{}".format(learning_unit_year_full.acronym)
        )
        self.assertEqual(
            results[1]['learning_unit_acronym'],
            "{}".format(learning_unit_year_partim1.acronym)
        )

    def _create_ue_with_partims(self):
        current_academic_year = create_current_academic_year()
        learning_container_year = LearningContainerYearFactory(
            academic_year=current_academic_year,
            container_type=learning_container_year_types.COURSE
        )
        learning_unit_year_full = LearningUnitYearFactory(
            learning_container_year=learning_container_year,
            acronym="LBRT2101",
            academic_year=current_academic_year,
            subtype=learning_unit_year_subtypes.FULL,
        )
        learning_unit_year_partim1 = LearningUnitYearPartimFactory(
            learning_container_year=learning_container_year,
            acronym="LBRT2101A",
            academic_year=current_academic_year,

        )
        return learning_unit_year_full, learning_unit_year_partim1


class MyLearningUnitEnrollmentsListViewTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.offer_enrollment = OfferEnrollmentFactory()
        cls.ue_enrollment = LearningUnitEnrollmentFactory(
            learning_unit_year__academic_year__year=cls.offer_enrollment.education_group_year.academic_year.year,
            offer_enrollment=cls.offer_enrollment
        )
        cls.student = cls.offer_enrollment.student
        cls.url = reverse('learning_unit_enrollment_api_v1:' + MyLearningUnitEnrollmentsListView.name, args=[
            cls.offer_enrollment.education_group_year.acronym,
            cls.offer_enrollment.education_group_year.academic_year.year
        ])

    def setUp(self):
        self.client.force_authenticate(self.student.person.user)

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

        self.assertCountEqual(list(results[0].keys()), [
            'date_enrollment',
            'enrollment_state',
            'student_last_name',
            'student_first_name',
            'student_email',
            'student_registration_id',
            'specific_profile',
            'program',
            'learning_unit_acronym',
            'learning_unit_year',
        ])

    def test_get_results_if_enrolled_to_11ba(self):
        cohort = FirstYearBachelorFactory(education_group_year__acronym='FSA1BA')
        offer_enrollment_11ba = OfferEnrollmentFactory(
            cohort_year=cohort,
            education_group_year=cohort.education_group_year
        )
        LearningUnitEnrollmentFactory(
            learning_unit_year__academic_year__year=offer_enrollment_11ba.education_group_year.academic_year.year,
            offer_enrollment=offer_enrollment_11ba
        )
        self.client.force_authenticate(user=offer_enrollment_11ba.student.person.user)
        url = reverse('learning_unit_enrollment_api_v1:' + MyLearningUnitEnrollmentsListView.name, args=[
            offer_enrollment_11ba.education_group_year.acronym.replace('1', '11'),
            offer_enrollment_11ba.education_group_year.academic_year.year
        ])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.json()['results']
        self.assertEqual(len(results), 1)

        self.assertEqual(
            results[0]['program'],
            offer_enrollment_11ba.education_group_year.acronym.replace('1', '11')
        )
