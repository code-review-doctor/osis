##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2018 Université catholique de Louvain (http://www.uclouvain.be)
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
import datetime

from django.db.models import QuerySet, Q

from base.auth.roles import program_manager
from base.auth.roles.entity_manager import EntityManager
from base.business.entity_version import load_main_entity_structure
from base.models.person import Person
from osis_common.utils.datetime import get_tzinfo
from osis_role.contrib.helper import EntityRoleHelper


def filter_learning_unit_year_according_person(queryset: QuerySet, person: Person) -> QuerySet:
    """
    This function will filter the learning unit year queryset according to permission of person.
       * As Entity Manager, we will filter on linked entities
       * As Program Manager, we will filter on learning unit year which are contained in the program
         that the person manage but not a borrow learning unit year

    :param queryset: LearningUnitYear queryset
    :param person: Person object
    :return: queryset
    """
    entities_with_descendants = EntityRoleHelper.get_all_entities(person, {EntityManager.group_name})

    learning_units_of_prgm_mngr = program_manager.get_learning_unit_years_attached_to_program_managers(
        person.programmanager_set.all(),
        load_main_entity_structure()
    )

    queryset = queryset.filter(
        Q(learning_container_year__requirement_entity_id__in=entities_with_descendants) |
        Q(id__in=learning_units_of_prgm_mngr)
    )
    return queryset
