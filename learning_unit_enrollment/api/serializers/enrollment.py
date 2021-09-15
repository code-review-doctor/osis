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
from rest_framework import serializers

from base.models.learning_unit_enrollment import LearningUnitEnrollment
from base.models.student_specific_profile import StudentSpecificProfile
from learning_unit_enrollment.api.serializers.specific_profile import StudentSpecificProfileSerializer


class EnrollmentSerializer(serializers.Serializer):
    date_enrollment = serializers.CharField()
    enrollment_state = serializers.CharField()
    student_last_name = serializers.CharField(source="student.person.last_name")
    student_first_name = serializers.CharField(source="student.person.first_name")
    student_email = serializers.CharField(source="student.person.email")
    student_registration_id = serializers.CharField(source="student.registration_id")
    specific_profile = StudentSpecificProfileSerializer(read_only=True, source="student.studentspecificprofile")
    program = serializers.CharField(source="offer.acronym")
    learning_unit_acronym = serializers.CharField(source="learning_unit_year.acronym")
