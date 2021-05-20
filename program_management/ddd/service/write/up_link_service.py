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

from program_management.ddd import command
from program_management.ddd.business_types import *
from program_management.ddd.repositories import load_node, program_tree
from program_management.ddd.service.read import get_program_tree_service


def up_link(command_up: command.OrderUpLinkCommand) -> 'NodeIdentity':
    root_id = int(command_up.path.split("|")[0])
    *_, parent_id, child_id = [int(element_id) for element_id in command_up.path.split("|")]

    parent_node = load_node.load(parent_id)
    child_node = load_node.load(child_id)

    tree = get_program_tree_service.get_program_tree_from_root_element_id(
        command.GetProgramTreeFromRootElementIdCommand(root_element_id=root_id)
    )
    link_to_up = tree.get_link(parent_node, child_node)
    parent_node = link_to_up.parent
    parent_node.up_child(child_node)

    program_tree.ProgramTreeRepository.update(tree)
    return child_node.entity_id
