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
import re
from typing import Pattern, Tuple, List, Set, Iterable

import attr

from base.models.enums.education_group_types import EducationGroupTypesEnum
from education_group.models.group_year import GroupYear
from osis_common.ddd import interface
from osis_common.decorators.deprecated import deprecated
from program_management.ddd.business_types import *
from program_management.ddd.domain.service.validation_rule import FieldValidationRule

TRANSITION_FIRST_LETTER = "T"

NodeCode = str

REGEX_TRAINING_PARTIAL_ACRONYM = r"^(?P<sigle_ele>[A-Z]{3,5})\d{3}[A-Z]$"
REGEX_COMMON_PARTIAL_ACRONYM = r"^(?P<sigle_ele>common(-\d[a-z]{1,2})?)$"
REGEX_GROUP_PARTIAL_ACRONYM_INITIAL_VALUE = r"^(?P<cnum>\d{3})(?P<subdivision>[A-Z])$"
MAX_CNUM = 999
WIDTH_CNUM = 3


@attr.s
class BGenerateNodeCode(interface.DomainService):
    existing_codes = attr.ib(type=Set[NodeCode], converter=set)

    def generate_transition_code(self, base_code: NodeCode) -> NodeCode:
        transition_base_code = "T" + base_code[1:]
        new_code = self.__generate_node_code(transition_base_code)

        self.existing_codes.add(new_code)
        return new_code

    def __generate_node_code(self, base_code: str) -> str:
        reg_parent_code = re.compile(REGEX_TRAINING_PARTIAL_ACRONYM)
        reg_common_partial_acronym = re.compile(REGEX_COMMON_PARTIAL_ACRONYM)
        reg_child_initial_value = re.compile(REGEX_GROUP_PARTIAL_ACRONYM_INITIAL_VALUE)

        match_result = reg_parent_code.search(base_code) or reg_common_partial_acronym.search(base_code)
        sigle_ele = match_result.group("sigle_ele")
        cnum, subdivision = reg_child_initial_value.search(
            base_code.replace(sigle_ele, "")
        ).group("cnum", "subdivision")

        code_generated = "{}{}{}".format(sigle_ele, cnum, subdivision)
        while code_generated in self.existing_codes:
            cnum = str(int(cnum) + 1)
            code_generated = "{}{}{}".format(sigle_ele, cnum, subdivision)

        return code_generated


#  FIXME:: Deprecated in favour of the above node generator
class GenerateNodeCode(interface.DomainService):

    @classmethod
    def generate_from_parent_node(
            cls,
            parent_node: 'Node',
            child_node_type: EducationGroupTypesEnum,
            duplicate_to_transition: bool
    ) -> NodeCode:
        code = TRANSITION_FIRST_LETTER + parent_node.code[1:] if duplicate_to_transition else parent_node.code
        return cls.__generate_node_code(code=code, child_node_type=child_node_type)

    @classmethod
    def __generate_node_code(cls, code: str, child_node_type: EducationGroupTypesEnum) -> NodeCode:
        reg_parent_code = re.compile(REGEX_TRAINING_PARTIAL_ACRONYM)
        reg_common_partial_acronym = re.compile(REGEX_COMMON_PARTIAL_ACRONYM)
        # FIXME : Sometimes parent does not have a partial acronym, it is a dirty situation. We have to clean the DB.
        if not code:
            return ""
        match_result = reg_parent_code.search(code) or reg_common_partial_acronym.search(code)
        sigle_ele = match_result.group("sigle_ele")

        reg_child_initial_value = re.compile(REGEX_GROUP_PARTIAL_ACRONYM_INITIAL_VALUE)
        cnum, subdivision = _get_cnum_subdivision(child_node_type, reg_child_initial_value)

        partial_acronym = "{}{}{}".format(sigle_ele, cnum, subdivision)
        while GroupYear.objects.filter(partial_acronym=partial_acronym).exists():
            cnum = "{:0{width}d}".format(
                (int(cnum) + 1) % MAX_CNUM,
                width=WIDTH_CNUM
            )
            partial_acronym = "{}{}{}".format(sigle_ele, cnum, subdivision)

        return partial_acronym


def _get_cnum_subdivision(
        child_node_type: EducationGroupTypesEnum,
        reg_child_initial_value: Pattern
) -> Tuple[str, str]:
    child_initial_value = FieldValidationRule.get(child_node_type, 'code').initial_value
    match_result = reg_child_initial_value.search(child_initial_value)
    if match_result:
        cnum, subdivision = match_result.group("cnum", "subdivision")
    else:
        cnum = None
        subdivision = None
    return cnum, subdivision
