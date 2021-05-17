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
from typing import List

import attr

from base.models.enums.internship_subtypes import InternshipSubtype
from base.models.enums.learning_container_year_types import LearningContainerYearType
from base.models.enums.learning_unit_year_periodicity import PeriodicityEnum
from ddd.logic.learning_unit.domain.model._partim import Partim, PartimBuilder
from ddd.logic.learning_unit.domain.model._titles import Titles
from ddd.logic.learning_unit.domain.model.responsible_entity import UCLEntityIdentity
from ddd.logic.shared_kernel.academic_year.domain.model.academic_year import AcademicYearIdentity
from ddd.logic.shared_kernel.language.domain.model.language import LanguageIdentity
from education_group.ddd.domain._entity import Entity
from osis_common.ddd import interface
from ddd.logic.learning_unit.commands import CreatePartimCommand
from ddd.logic.learning_unit.domain.model._remarks import Remarks


@attr.s(frozen=True, slots=True)
class FirstYearBachelorIdentity(interface.EntityIdentity):
    acronym = "11BA"


@attr.s(slots=True, hash=False, eq=False)
class FirstYearBachelor(interface.Entity):
    entity_id = attr.ib(type=FirstYearBachelorIdentity)
    administration_entity = attr.ib(type=Entity)
