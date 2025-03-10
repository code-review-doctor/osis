# ############################################################################
#  OSIS stands for Open Student Information System. It's an application
#  designed to manage the core business of higher education institutions,
#  such as universities, faculties, institutes and professional schools.
#  The core business involves the administration of students, teachers,
#  courses, programs and so on.
#
#  Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  A copy of this license - GNU General Public License - is available
#  at the root of the source code of this program.  If not,
#  see http://www.gnu.org/licenses/.
# ############################################################################
import random

from base.models import person, learning_unit_year
from base.models.academic_year import current_academic_year
from base.models.entity_version import EntityVersion
from base.models.enums.education_group_types import GroupType
from base.models.learning_unit_year import LearningUnitYear
from program_management.ddd import command
from program_management.ddd.service.read import get_program_tree_service


def get_random_learning_unit() -> learning_unit_year.LearningUnitYear:
    return LearningUnitYear.objects.filter(
        academic_year__year=current_academic_year().year
    ).order_by("?")[0]


def get_random_element_from_tree(
        tree_node_id: int
) -> str:
    tree = get_program_tree_service.get_program_tree_from_root_element_id(
        command.GetProgramTreeFromRootElementIdCommand(root_element_id=tree_node_id)
    )
    nodes = tree.get_all_nodes(types={GroupType.COMMON_CORE})
    return random.choice(list(nodes)).code
