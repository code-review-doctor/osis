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
from base.ddd.utils import business_validator
from program_management.ddd.business_types import *
from program_management.ddd.domain.exception import InvalidTreeVersionToFillFrom


class CheckValidTreeVersionToFillFrom(business_validator.BusinessValidator):
    def __init__(self, tree_version_to_fill_from: 'ProgramTreeVersion', tree_version_to_fill: 'ProgramTreeVersion'):
        self.tree_version_from = tree_version_to_fill_from
        self.tree_version_to = tree_version_to_fill
        super().__init__()

    def validate(self, *args, **kwargs):
        if self.tree_version_to.is_specific_official:
            return self._validate_for_specific_official()

        elif self.tree_version_to.is_standard_transition:
            return self._validate_for_standard_transition()

        elif self.tree_version_to.is_specific_transition:
            return self._validate_for_specific_transition()

    def _validate_for_specific_official(self):
        if not self.__is_last_year_tree():
            raise InvalidTreeVersionToFillFrom(self.tree_version_from)

    def _validate_for_standard_transition(self):
        if self.__is_last_year_tree():
            return
        elif self.__is_standard_tree():
            return
        elif self.__is_past_standard_tree():
            return

        raise InvalidTreeVersionToFillFrom(self.tree_version_from)

    def _validate_for_specific_transition(self):
        if self.__is_last_year_tree():
            return
        elif self.__is_specific_tree():
            return
        elif self.__is_past_specific_tree():
            return

        raise InvalidTreeVersionToFillFrom(self.tree_version_from)

    def __is_last_year_tree(self) -> bool:
        return self.tree_version_from.entity_id.year + 1 == self.tree_version_to.entity_id.year and \
               self.tree_version_from.get_tree().root_node.code == self.tree_version_to.get_tree().root_node.code

    def __is_standard_tree(self):
        return self.tree_version_from.entity_id.year == self.tree_version_to.entity_id.year and \
               self.tree_version_from.entity_id.offer_acronym == self.tree_version_to.entity_id.offer_acronym and\
               self.tree_version_from.is_standard

    def __is_past_standard_tree(self):
        return self.tree_version_from.entity_id.year + 1 == self.tree_version_to.entity_id.year and \
               self.tree_version_from.entity_id.offer_acronym == self.tree_version_to.entity_id.offer_acronym and \
               self.tree_version_from.is_standard

    def __is_specific_tree(self):
        return self.tree_version_from.entity_id.year == self.tree_version_to.entity_id.year and \
               self.tree_version_from.entity_id.offer_acronym == self.tree_version_to.entity_id.offer_acronym and \
               self.tree_version_from.entity_id.version_name == self.tree_version_to.entity_id.version_name and \
               self.tree_version_from.is_specific_official

    def __is_past_specific_tree(self):
        return self.tree_version_from.entity_id.year + 1 == self.tree_version_to.entity_id.year and \
               self.tree_version_from.entity_id.offer_acronym == self.tree_version_to.entity_id.offer_acronym and \
               self.tree_version_from.entity_id.version_name == self.tree_version_to.entity_id.version_name and \
               self.tree_version_from.is_specific_official
