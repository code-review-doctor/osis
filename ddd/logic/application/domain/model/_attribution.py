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
from decimal import Decimal

import attr

from attribution.models.enums.function import Functions
from ddd.logic.learning_unit.domain.model.learning_unit import LearningUnitIdentity
from ddd.logic.shared_kernel.academic_year.domain.model.academic_year import AcademicYearIdentity
from osis_common.ddd import interface


@attr.s(frozen=True, slots=True)
class Attribution(interface.ValueObject):
    course_id = attr.ib(type=LearningUnitIdentity)
    course_title = attr.ib(type=str)
    course_type = attr.ib(type=str)
    course_is_in_suppression_proposal = attr.ib(type=bool)
    function = attr.ib(type=Functions)
    end_year = attr.ib(type=AcademicYearIdentity)
    start_year = attr.ib(type=AcademicYearIdentity)
    lecturing_volume = attr.ib(type=Decimal)
    practical_volume = attr.ib(type=Decimal)
    is_substitute = attr.ib(type=bool)
