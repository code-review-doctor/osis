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
from base.models.education_group_year import EducationGroupYear
from base.models.enums.education_group_types import EducationGroupTypesEnum, GroupType
from osis_common.ddd import interface
from program_management.ddd.business_types import *
from program_management.ddd.domain.service.validation_rule import FieldValidationRule

DEFAULT_SPECIFIC_TITLES = {
    GroupType.MINOR_LIST_CHOICE: 'Liste au choix mineures',
    GroupType.OPTION_LIST_CHOICE: 'Liste au choix options'
}


class GenerateNodeAbbreviatedTitle(interface.DomainService):

    @classmethod
    def generate(cls, parent_node: 'Node', child_node_type: EducationGroupTypesEnum) -> str:
        default_abbreviated_title = FieldValidationRule.get(child_node_type, 'abbreviated_title').initial_value
        default_title = cls._get_default_title(child_node_type)
        default_value = default_abbreviated_title or default_title
        return "{child_title}{parent_abbreviated_title}".format(
            child_title=default_value.replace(" ", "").upper(),
            parent_abbreviated_title=parent_node.title
        )[:EducationGroupYear._meta.get_field("acronym").max_length]

    @classmethod
    def _get_default_title(cls, child_node_type):
        return DEFAULT_SPECIFIC_TITLES.get(child_node_type) or \
               FieldValidationRule.get(child_node_type, 'title_fr').initial_value
