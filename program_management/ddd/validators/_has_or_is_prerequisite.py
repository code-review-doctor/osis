##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)
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
import copy
from typing import Set

from django.utils.translation import gettext_lazy as _

import osis_common.ddd.interface
from base.ddd.utils import business_validator
from program_management.ddd.business_types import *
from program_management.ddd.domain import program_tree, node
from program_management.ddd.domain.exception import CannotDetachLearningWhoIsPrerequisiteException, \
    CannotDetachChildrenWhoArePrerequisiteException


class IsPrerequisiteValidator(business_validator.BusinessValidator):

    def __init__(self, tree: 'ProgramTree', path_to_parent: 'Path', node_to_detach: 'Node'):
        super(IsPrerequisiteValidator, self).__init__()
        self.node_to_detach = node_to_detach
        self.tree = tree
        self.path_to_parent = path_to_parent

    def validate(self):
        nodes_that_are_prerequisites = self._get_nodes_that_are_prerequisite()
        if nodes_that_are_prerequisites:
            codes_that_are_prerequisite = [node.code for node in nodes_that_are_prerequisites]
            if self.node_to_detach.is_learning_unit():
                raise CannotDetachLearningWhoIsPrerequisiteException(self.node_to_detach)
            else:
                raise CannotDetachChildrenWhoArePrerequisiteException(
                    self.tree.root_node,
                    self.node_to_detach,
                    codes_that_are_prerequisite
                )

    def _get_nodes_that_are_prerequisite(self):
        remaining_children_after_detach = self._get_all_remaining_children_after_detach()

        learning_unit_children_removed_after_detach = self.node_to_detach.get_all_children_as_learning_unit_nodes()
        if self.node_to_detach.is_learning_unit():
            learning_unit_children_removed_after_detach.append(self.node_to_detach)

        nodes_that_are_prerequisites = [
            n for n in learning_unit_children_removed_after_detach
            if n.is_prerequisite and n not in remaining_children_after_detach
        ]
        return sorted(nodes_that_are_prerequisites, key=lambda n: n.code)

    def _get_all_remaining_children_after_detach(self) -> Set['Node']:
        pruned_tree = copy.copy(self.tree)
        node.Node.descendents.fget.cache_clear()  # Invalidate cache so as recompute value for copy
        pruned_tree.get_node(self.path_to_parent).detach_child(self.node_to_detach)
        return pruned_tree.get_all_nodes()


class HasPrerequisiteValidator(business_validator.BusinessValidator):

    def __init__(self, tree: 'ProgramTree', path_of_node_to_detach: 'Path'):
        super(HasPrerequisiteValidator, self).__init__()
        self.node_to_detach = tree.get_node(path_of_node_to_detach)
        self.path_to_parent, *__ = path_of_node_to_detach.rsplit(program_tree.PATH_SEPARATOR, 1)
        self.tree = tree

    def validate(self):
        nodes_detached_that_have_prerequisites = self._get_nodes_detached_that_have_prerequisite()
        learning_unit_nodes_remaining = self._get_learning_unit_nodes_remaining_if_node_is_detached()

        nodes_that_have_prerequisite_and_not_anymore_present_in_tree = nodes_detached_that_have_prerequisites - \
            learning_unit_nodes_remaining
        if nodes_that_have_prerequisite_and_not_anymore_present_in_tree:
            codes_that_have_prerequisites = [node.code
                                             for node in nodes_that_have_prerequisite_and_not_anymore_present_in_tree]
            raise osis_common.ddd.interface.BusinessExceptions([
                _("The prerequisites for the following learning units contained in education group year "
                  "%(acronym)s will we deleted: %(learning_units)s") % {
                    "acronym": self.tree.root_node.title,
                    "learning_units": ", ".join(codes_that_have_prerequisites)
                }
            ])

    def _get_nodes_detached_that_have_prerequisite(self) -> Set['Node']:
        search_under_node = self.node_to_detach
        learning_unit_nodes = search_under_node.get_all_children_as_learning_unit_nodes()

        if search_under_node.is_learning_unit():
            learning_unit_nodes.append(search_under_node)

        return {node for node in learning_unit_nodes if node.has_prerequisite}

    def _get_learning_unit_nodes_remaining_if_node_is_detached(self) -> Set['Node']:
        pruned_tree = copy.copy(self.tree)
        pruned_tree.get_node(self.path_to_parent).detach_child(self.node_to_detach)
        return set(pruned_tree.root_node.get_all_children_as_learning_unit_nodes())
