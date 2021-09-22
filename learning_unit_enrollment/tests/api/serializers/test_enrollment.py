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
from types import SimpleNamespace

from django.test import TestCase

from base.models.enums.peps_type import PepsTypes
from base.tests.factories.learning_unit_enrollment import LearningUnitEnrollmentFactory
from base.tests.factories.student import StudentFactory
from base.tests.factories.student_specific_profile import StudentSpecificProfileFactory
from learning_unit_enrollment.api.serializers.enrollment import EnrollmentSerializer


class EnrollmentSerializerTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        student = StudentFactory(
            studentspecificprofile=StudentSpecificProfileFactory(
                type=PepsTypes.SPORT.name,
            )
        )
        cls.ue_enrollment = LearningUnitEnrollmentFactory(offer_enrollment__student=student)
        cls.ue_enrollment_ns = SimpleNamespace(
            date_enrollment=cls.ue_enrollment.date_enrollment,
            enrollment_state=cls.ue_enrollment.enrollment_state,
            student_last_name=student.person.last_name,
            student_first_name=student.person.first_name,
            student_email=student.person.email,
            student_registration_id=student.registration_id,
            student=student,  # WTF ?
            program=cls.ue_enrollment.offer_enrollment.education_group_year.acronym,
            learning_unit_acronym=cls.ue_enrollment.learning_unit_year.acronym,
            learning_unit_academic_year=cls.ue_enrollment.learning_unit_year.academic_year.year,
        )

        cls.serializer = EnrollmentSerializer(cls.ue_enrollment_ns)

    def test_contains_expected_fields(self):
        expected_fields = [
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
        ]
        self.assertListEqual(list(self.serializer.data.keys()), expected_fields)
