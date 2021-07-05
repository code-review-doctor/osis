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

from ddd.logic.learning_unit.builder.learning_unit_identity_builder import LearningUnitIdentityBuilder
from ddd.logic.learning_unit.commands import CanCreateEffectiveClassCommand
from ddd.logic.learning_unit.domain.service.can_save_effective_class import CanCreateEffectiveClass
from ddd.logic.learning_unit.domain.service.i_student_enrollments import IStudentEnrollments
from ddd.logic.learning_unit.repository.i_learning_unit import ILearningUnitRepository


def check_can_create_effective_class(
        cmd: 'CanCreateEffectiveClassCommand',
        learning_unit_repository: 'ILearningUnitRepository',
        has_enrollments_service: 'IStudentEnrollments',
) -> None:
    learning_unit_identity = LearningUnitIdentityBuilder.build_from_code_and_year(
        code=cmd.learning_unit_code,
        year=cmd.learning_unit_year
    )
    learning_unit = learning_unit_repository.get(learning_unit_identity)
    CanCreateEffectiveClass().verify(
        learning_unit=learning_unit,
        learning_unit_repository=learning_unit_repository,
        has_enrollments_service=has_enrollments_service,
    )
