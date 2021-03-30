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
from typing import Set, Optional

from base.ddd.utils import business_validator
from program_management.ddd.business_types import *
from program_management.ddd.domain.exception import FinalitiesHaveNoCorrespondingTransitionVersionException
from program_management.ddd.domain import program_tree


class FinalitiesHaveCorrespondingTransitionValidator(business_validator.BusinessValidator):
    def __init__(self, from_tree: 'ProgramTree', to_tree: 'ProgramTree', existing_nodes: Set['Node']):
        self.from_tree = from_tree
        self.to_tree = to_tree
        self.existing_nodes = existing_nodes
        super().__init__()

    def validate(self, *args, **kwargs):
        finalities = self.from_tree.get_all_finalities()
        if not finalities:
            return

        for finality in finalities:
            if self._has_transition_node(
                    self.existing_nodes,
                    finality,
                    self.to_tree.root_node.transition_name,
                    self.to_tree.root_node.year
            ):
                return
        raise FinalitiesHaveNoCorrespondingTransitionVersionException(finalities, self.to_tree)

    def _has_transition_node(
            self,
            existing_nodes: Set['Node'],
            finality_node: 'Node',
            transition_name: str,
            year: int
    ) -> bool:
        return any(
            (
                node for node in existing_nodes
                if program_tree.is_transition_node_equivalent(node, finality_node, transition_name, year)
            )
        )
