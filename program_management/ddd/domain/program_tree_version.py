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

from program_management.ddd.business_types import *
from base.models.education_group_year import EducationGroupYear
from education_group.models.group_year import GroupYear

STANDARD = ""


class ProgramTreeVersionBuilder:

    _tree_version = None

    def build_from(self, from_tree: 'ProgramTreeVersion', **tree_version_attrs) -> 'ProgramTreeVersion':
        assert isinstance(from_tree, ProgramTreeVersion)
        assert from_tree.is_standard, "Forbidden to copy from a non Standard version"
        if from_tree.is_transition:
            self._tree_version = self._build_from_transition(from_tree.tree, **tree_version_attrs)
        else:
            self._tree_version = self._build_from_standard(from_tree.tree, **tree_version_attrs)
        return self.program_tree_version

    @property
    def program_tree_version(self):
        return self._tree_version

    def _build_from_transition(self, from_tree: 'ProgramTree', **tree_version_attrs) -> 'ProgramTreeVersion':
        raise NotImplementedError()

    def _build_from_standard(self, from_tree: 'ProgramTree', **tree_version_attrs) -> 'ProgramTreeVersion':
        raise NotImplementedError()


class ProgramTreeVersion:

    def __init__(
            self,
            tree: 'ProgramTree',
            version_name: str = STANDARD,
            is_transition: bool = False,
            offer: int = None,
            title_fr: str = None,
            title_en: str = None,
            root_group = None
    ):
        self.tree = tree
        self.is_transition = is_transition
        self.version_name = version_name
        self.offer = offer
        self.title_fr = title_fr
        self.title_en = title_en
        self.root_group = root_group

    @property
    def is_standard(self):
        return self.version_name == STANDARD

    @property
    def version_label(self):
        if self.is_standard:
            return 'Transition' if self.is_transition else ''
        else:
            return '{}-Transition'.format(self.version_name) if self.is_transition else self.version_name
