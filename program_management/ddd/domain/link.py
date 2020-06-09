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

from base.models.enums.link_type import LinkTypes
from base.models.enums.quadrimesters import DerogationQuadrimester
from program_management.ddd.business_types import *
from program_management.models.enums.node_type import NodeType


class Link:

    def __init__(
        self,
        parent: 'Node',
        child: 'Node',
        pk: int = None,
        relative_credits: int = None,
        min_credits: int = None,
        max_credits: int = None,
        is_mandatory: bool = False,
        block: str = None,
        access_condition: bool = False,
        comment: str = None,
        comment_english: str = None,
        own_comment: str = None,
        quadrimester_derogation: DerogationQuadrimester = None,
        link_type: LinkTypes = None,
        order: int = None
    ):
        self.pk = pk
        self.parent = parent
        self.child = child
        self.relative_credits = relative_credits
        self.min_credits = min_credits
        self.max_credits = max_credits
        self.is_mandatory = is_mandatory
        self.block = block
        self.access_condition = access_condition
        self.comment = comment
        self.comment_english = comment_english
        self.own_comment = own_comment
        self.quadrimester_derogation = quadrimester_derogation
        self.link_type = link_type
        self.order = order
        self._has_changed = False

    @property
    def has_changed(self):
        return self._has_changed

    def __str__(self):
        return "%(parent)s - %(child)s" % {'parent': self.parent, 'child': self.child}

    def is_reference(self):
        return self.link_type == LinkTypes.REFERENCE

    @property
    def block_repr(self) -> FieldValueRepresentation:
        if self.block:
            block_in_array = [i for i in str(self.block)]
            return " ; ".join(
                block_in_array
            )
        return ''

    @property
    def block_max_value(self) -> int:
        return int(str(self.block)[-1]) if self.block else 0

    @property
    def relative_credits_repr(self) -> FieldValueRepresentation:
        return "{} / {:f}".format(self.relative_credits, self.child.credits.to_integral_value())

    def is_link_with_learning_unit(self):
        return self.child.is_learning_unit()

    def is_link_with_group(self):
        return self.child.is_group_or_mini_or_training()

    def order_up(self):
        self.order -= 1
        self._has_changed = True

    def order_down(self):
        self.order += 1
        self._has_changed = True


class LinkWithChildLeaf(Link):
    def __init__(self, *args, **kwargs):
        super(LinkWithChildLeaf, self).__init__(*args, **kwargs)


class LinkWithChildBranch(Link):
    def __init__(self, *args, **kwargs):
        super(LinkWithChildBranch, self).__init__(*args, **kwargs)


class LinkFactory:

    def get_link(self, parent: 'Node', child: 'Node', **kwargs) -> Link:
        if parent and parent.node_type == NodeType.LEARNING_UNIT.name:
            return LinkWithChildLeaf(parent, child, **kwargs)
        else:
            return LinkWithChildBranch(parent, child, **kwargs)

    def deepcopy_link_without_copy_children_recursively(original_link: 'Link'):
        original_child = original_link.child
        original_link.child = None  # To avoid recursive deep copy of all children behind
        new_link = copy.deepcopy(original_link)
        original_link.child = original_child
        return new_link


factory = LinkFactory()
