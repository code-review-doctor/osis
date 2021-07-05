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

from base.models.learning_unit_enrollment import LearningUnitEnrollment as LearningUnitEnrollmentDatabase
from ddd.logic.learning_unit.domain.model.effective_class import EffectiveClassIdentity
from ddd.logic.learning_unit.domain.model.learning_unit import LearningUnitIdentity
from ddd.logic.learning_unit.domain.service.i_student_enrollments import \
    IStudentEnrollmentsTranslator


class StudentEnrollmentsTranslator(IStudentEnrollmentsTranslator):

    @classmethod
    def has_enrollments_to_class(cls, class_identity: 'EffectiveClassIdentity') -> bool:
        # TODO :: check the enrollment to the effective class instead of learning unit
        return LearningUnitEnrollmentDatabase.objects.filter(
            learning_unit_year__acronym=class_identity.learning_unit_identity.code,
            learning_unit_year__academic_year__year=class_identity.learning_unit_identity.year
        ).exists()

    @classmethod
    def has_enrollments_to_learning_unit(cls, learning_unit_id: 'LearningUnitIdentity') -> bool:
        return LearningUnitEnrollmentDatabase.objects.filter(
            learning_unit_year__acronym=learning_unit_id.code,
            learning_unit_year__academic_year__year=learning_unit_id.year
        ).exists()
