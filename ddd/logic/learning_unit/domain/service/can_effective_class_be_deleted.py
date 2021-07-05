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
from ddd.logic.learning_unit.commands import HasClassRepartitionCommand, HasEnrollmentsToClassCommand
from ddd.logic.learning_unit.domain.model.effective_class import EffectiveClass
from ddd.logic.learning_unit.domain.validator.exceptions import EffectiveClassHasTutorAssignedException, \
    LearningUnitOfEffectiveClassHasEnrollmentException
from osis_common.ddd import interface


class CanEffectiveClassBeDeleted(interface.DomainService):

    @classmethod
    def verify(
            cls,
            effective_class: 'EffectiveClass'
    ):
        exceptions = set()  # type Set[BusinessException]
        from infrastructure.messages_bus import message_bus_instance
        learning_unit_has_enrollments = message_bus_instance.invoke(
            HasEnrollmentsToClassCommand(
                learning_unit_code=effective_class.entity_id.learning_unit_identity.code,
                year=effective_class.entity_id.learning_unit_identity.year
            )
        )
        if learning_unit_has_enrollments:
            exceptions.add(LearningUnitOfEffectiveClassHasEnrollmentException())

        tutor_assign_to_class = message_bus_instance.invoke(
            HasClassRepartitionCommand(
                class_code=effective_class.class_code,
                learning_unit_code=effective_class.entity_id.learning_unit_identity.code,
                year=effective_class.entity_id.learning_unit_identity.year
            )
        )

        if tutor_assign_to_class:
            exceptions.add(
                EffectiveClassHasTutorAssignedException(
                    effective_class_complete_code=effective_class.complete_acronym,
                    tutor_full_name=tutor_assign_to_class,
                    learning_unit_year=effective_class.entity_id.learning_unit_identity.year
                )
            )

        if exceptions:
            raise MultipleBusinessExceptions(exceptions=exceptions)
