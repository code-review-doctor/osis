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
import uuid
from enum import Enum
from typing import Optional, Tuple

from django import forms
from django.utils.translation import gettext_lazy as _

from base.ddd.utils.business_validator import MultipleBusinessExceptions
from base.forms.exceptions import InvalidFormException
from program_management.ddd.command import FillProgramTreeVersionContentFromProgramTreeVersionCommand
from program_management.ddd.domain.program_tree_version import ProgramTreeVersion
from program_management.ddd.service.write import fill_program_tree_version_content_from_program_tree_version_service


class ValidSourceChoices(Enum):
    LAST_YEAR_TRANSITION_TREE = "last_year"
    SAME_VERSION = "same_version"
    LAST_YEAR_SAME_VERSION_TREE = "last_year_same_version"


class FillTransitionContentForm(forms.Form):

    source_choices = forms.ChoiceField(required=True, widget=forms.RadioSelect())

    def __init__(
            self,
            transition_tree: 'ProgramTreeVersion',
            last_year_transition_tree: Optional['ProgramTreeVersion'],
            same_version_tree: 'ProgramTreeVersion',
            last_year_same_version_tree: Optional['ProgramTreeVersion'],
            *args,
            **kwargs
    ):
        self.transition_tree = transition_tree
        self.last_year_transition_tree = last_year_transition_tree
        self.same_version_tree = same_version_tree
        self.last_year_same_version_tree = last_year_same_version_tree

        super().__init__(*args, **kwargs)

        self.set_source_choices()

    def save(self) -> uuid.UUID:
        if self.is_valid():
            try:
                cmd = self.generate_cmd()
                fill_program_tree_version_content_from_program_tree_version_service. \
                    fill_program_tree_version_content_from_program_tree_version(cmd)
                return cmd.transaction_id
            except MultipleBusinessExceptions as multiple_exceptions:
                for exception in multiple_exceptions.exceptions:
                    self.add_error(None, exception.message)
        raise InvalidFormException()

    def generate_cmd(self) -> 'FillProgramTreeVersionContentFromProgramTreeVersionCommand':
        tree_to_fill_from = self._get_tree_to_fill_from()
        return FillProgramTreeVersionContentFromProgramTreeVersionCommand(
            from_year=tree_to_fill_from.entity_id.year,
            from_offer_acronym=tree_to_fill_from.entity_id.offer_acronym,
            from_version_name=tree_to_fill_from.version_name,
            from_transition_name=tree_to_fill_from.transition_name,
            to_year=self.transition_tree.entity_id.year,
            to_offer_acronym=self.transition_tree.entity_id.offer_acronym,
            to_version_name=self.transition_tree.version_name,
            to_transition_name=self.transition_tree.transition_name
        )

    def _get_tree_to_fill_from(self) -> 'ProgramTreeVersion':
        map_choice_tree_version = {
            ValidSourceChoices.LAST_YEAR_TRANSITION_TREE.value: self.last_year_transition_tree,
            ValidSourceChoices.SAME_VERSION.value: self.same_version_tree,
            ValidSourceChoices.LAST_YEAR_SAME_VERSION_TREE.value: self.last_year_same_version_tree
        }
        source_choice = self.cleaned_data["source_choices"]

        return map_choice_tree_version[source_choice]

    def set_source_choices(self) -> None:
        self.fields["source_choices"].choices = self.__generate_choices()

    def __generate_choices(self) -> Tuple[Tuple[str, str]]:
        choices = []

        if self.last_year_transition_tree:
            choices.append(
                (
                    ValidSourceChoices.LAST_YEAR_TRANSITION_TREE.value,
                    self.__get_last_year_transition_tree_option_human_readable()
                )
            )
        if self.last_year_same_version_tree:
            choices.append(
                (
                    ValidSourceChoices.LAST_YEAR_SAME_VERSION_TREE.value,
                    self.__get_last_year_same_version_tree_option_human_readable()
                )
            )

        if self.same_version_tree:
            choices.append(
                (ValidSourceChoices.SAME_VERSION.value, self.__get_same_version_tree_option_human_readable())
            )

        return tuple(choices)

    def __get_last_year_transition_tree_option_human_readable(self) -> str:
        return _("Fill from transition version of last year: %(title)s in %(year)s") % {
            "title": self.last_year_transition_tree.official_name,
            "year": self.last_year_transition_tree.academic_year
        }

    def __get_same_version_tree_option_human_readable(self) -> str:
        text = _("Fill from standard version of this year: %(title)s in %(year)s")
        if self.same_version_tree.is_specific_official:
            text = _("Fill from specific official of this year: %(title)s in %(year)s")
        return text % {
            "title": self.same_version_tree.official_name,
            "year": self.same_version_tree.academic_year
        }

    def __get_last_year_same_version_tree_option_human_readable(self) -> str:
        text = _("Fill from standard version of last year: %(title)s in %(year)s")
        if self.last_year_same_version_tree.is_specific_official:
            text = _("Fill from specific official of last year: %(title)s in %(year)s")
        return text % {
            "title": self.last_year_same_version_tree.official_name,
            "year": self.last_year_same_version_tree.academic_year
        }
