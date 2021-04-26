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
from typing import List

from django.db import transaction

from program_management.ddd.command import BulkUpdateLinkCommand
from program_management.ddd.business_types import *
from base.ddd.utils.business_validator import MultipleBusinessExceptions
from program_management.ddd.domain.program_tree import ProgramTreeIdentity


@transaction.atomic()
def bulk_update_links(cmd: BulkUpdateLinkCommand, repository: 'ProgramTreeRepository') -> List['Link']:
    tree_id = ProgramTreeIdentity(code=cmd.parent_node_code, year=cmd.parent_node_year)
    tree = repository.get(tree_id)
    links_updated = []
    exceptions = dict()
    for update_cmd in cmd.update_link_cmds:
        # TODO : create DomainService to check all commands has same parent ? Or add "context tree" in List['UpdateLinkCommand'] (remplacer BulkUpdateLinkCommand)?
        try:
            link_updated = tree.update_link(update_cmd)
            links_updated.append(link_updated)
        except MultipleBusinessExceptions as e:
            exceptions[update_cmd] = e
    if exceptions:
        raise MultipleBusinessExceptions(exceptions=exceptions)
    repository.update(tree)
    return links_updated
