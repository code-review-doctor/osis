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
from base.ddd.utils.business_validator import MultipleBusinessExceptions
from ddd.logic.learning_unit.domain.validator.exceptions import EffectiveClassHasTutorAssignedException, \
    LearningUnitOfEffectiveClassHasEnrollmentException
from osis_common.ddd import interface


class EffectiveClassCanBeDeleted(interface.DomainService):

    @classmethod
    def verify(
            cls,
            effective_class: 'EffectiveClass',
            learning_unit: 'LearningUnit',
            learning_unit_repository: 'LearningUnitRepository',
            effective_class_repository: 'EffectiveClassRepository'
    ):
        exceptions = set()  # type Set[BusinessException]
        if learning_unit_repository.has_enrollments(learning_unit):
            exceptions.add(LearningUnitOfEffectiveClassHasEnrollmentException())

        tutor_assign_to_class = effective_class_repository.get_tutor_assign_to_class(effective_class)
        if tutor_assign_to_class:
            exceptions.add(EffectiveClassHasTutorAssignedException(effective_class=effective_class,
                                                                   tutor_full_name=tutor_assign_to_class))

        if exceptions:
            raise MultipleBusinessExceptions(exceptions=exceptions)
