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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from typing import List, Dict

import attr

from osis_common.ddd import interface
from program_management.ddd.business_types import *


class GetNextYearNode(interface.DomainService):
    def search_for_learning_unit_years(
            self,
            nodes: List['NodeLearningUnitYear'],
            node_repo: 'NodeRepository'
    ) -> Dict['NodeIdentity', 'Node']:
        next_year_nodes = node_repo.search(
            entity_ids=[attr.evolve(node.entity_id, year=node.entity_id.year+1) for node in nodes]
        )
        mapping = {attr.evolve(node.entity_id, year=node.entity_id.year-1): node for node in next_year_nodes}
        mapping.update(
            {node.entity_id: node_repo.get_next_learning_unit_year_node(node.entity_id)
             for node in nodes if node.entity_id not in mapping}
        )
        return mapping
