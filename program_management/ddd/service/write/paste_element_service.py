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
from django.db import transaction

from program_management.ddd import command
from program_management.ddd.business_types import *
from program_management.ddd.domain.program_tree import PATH_SEPARATOR, ProgramTreeIdentity
from program_management.ddd.repositories import load_tree, program_tree, \
    program_tree_version


@transaction.atomic()
def paste_element(paste_command: command.PasteElementCommand) -> 'LinkIdentity':
    path_to_detach = paste_command.path_where_to_detach

    # FIXME should take tree only from parent code and parent year and not from path
    if paste_command.parent_code and paste_command.parent_year:
        tree = program_tree.ProgramTreeRepository.get(
            ProgramTreeIdentity(code=paste_command.parent_code, year=paste_command.parent_year)
        )
    else:
        root_id = int(paste_command.path_where_to_paste.split("|")[0])
        tree = load_tree.load(root_id)

    node_to_attach = program_tree.ProgramTreeRepository.get(
        ProgramTreeIdentity(code=paste_command.node_to_paste_code, year=paste_command.node_to_paste_year)
    ).root_node

    link_created = tree.paste_node(
        node_to_attach,
        paste_command,
        program_tree.ProgramTreeRepository(),
        program_tree_version.ProgramTreeVersionRepository()
    )

    if path_to_detach:
        root_tree_to_detach = int(path_to_detach.split(PATH_SEPARATOR)[0])
        tree_to_detach = tree if root_tree_to_detach == root_id else load_tree.load(root_tree_to_detach)
        tree_to_detach.detach_node(path_to_detach, program_tree.ProgramTreeRepository())

    program_tree.ProgramTreeRepository().update(tree)

    return link_created.entity_id
