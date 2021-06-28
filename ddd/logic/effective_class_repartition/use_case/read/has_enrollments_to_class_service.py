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
from typing import Optional

from ddd.logic.learning_unit.builder.learning_unit_identity_builder import LearningUnitIdentityBuilder
from ddd.logic.learning_unit.commands import HasEnrollmentsToClassCommand
from infrastructure.learning_unit.domain.service.student_enrollments_to_effective_class import \
    StudentEnrollmentsToEffectiveClass


def has_enrollments_to_class_service(
        cmd: 'HasEnrollmentsToClassCommand'
) -> Optional[str]:
    learning_unit_identity = LearningUnitIdentityBuilder.build_from_code_and_year(
        code=cmd.learning_unit_code,
        year=cmd.year
    )
    return StudentEnrollmentsToEffectiveClass.has_enrollments_to_class(
        learning_unit_identity
    )

