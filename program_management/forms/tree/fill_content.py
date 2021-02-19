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
from typing import Tuple, Optional

from django import forms
from django.utils.translation import gettext_lazy as _

from program_management.ddd.domain.program_tree_version import ProgramTreeVersion
from program_management.formatter import format_tree_version_acronym


class FillContentForm(forms.Form):
    strategy = forms.ChoiceField(
        widget=forms.RadioSelect,
    )

    def __init__(
            self,
            past_transition_tree: Optional['ProgramTreeVersion'],
            standard_tree: 'ProgramTreeVersion',
            past_standard_tree: Optional['ProgramTreeVersion'],
            *args,
            **kwargs
    ):
        self.past_transition_tree = past_transition_tree
        self.standard_tree = standard_tree
        self.past_standard_tree = past_standard_tree
        super(FillContentForm, self).__init__(*args, **kwargs)
        self.fields["strategy"].choices = self.__define_choices()

    def __define_choices(self) -> Tuple:
        choices = []
        if self.past_transition_tree:
            choices.append(
                (
                    "1",
                    _("Copy from transition version from past year: %(program_name)s in %(year)s") % {
                        "program_name": format_tree_version_acronym(self.past_transition_tree),
                        "year": self.past_transition_tree.get_tree().root_node.academic_year
                    }
                )
            )
        if self.past_standard_tree:
            choices.append(
                (
                    "2",
                    _("Copy from standard version from past year: %(program_name)s in %(year)s") % {
                        "program_name": format_tree_version_acronym(self.past_standard_tree),
                        "year": self.past_standard_tree.get_tree().root_node.academic_year
                    }
                )
            )
        if self.standard_tree:
            choices.append(
                (
                    "3",
                    _("Copy from standard version from this year: %(program_name)s in %(year)s") % {
                        "program_name": format_tree_version_acronym(self.standard_tree),
                        "year": self.standard_tree.get_tree().root_node.academic_year
                    }
                )
            )

        return tuple(choices)
