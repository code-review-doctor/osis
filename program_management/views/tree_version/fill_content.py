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
import functools
from typing import Dict, Tuple, Optional

from django.views.generic import FormView

from base.views.mixins import AjaxTemplateMixin
from education_group.models.group_year import GroupYear
from osis_role.contrib.views import PermissionRequiredMixin
from program_management.ddd import command
from program_management.ddd.command import GetStandardProgramTreeVersionFromTransitionVersionCommand
from program_management.ddd.domain.exception import ProgramTreeVersionNotFoundException
from program_management.ddd.domain.program_tree_version import ProgramTreeVersion
from program_management.ddd.service.read import get_program_tree_version_from_node_service
from program_management.ddd.service.read.get_standard_program_tree_version_from_transition_version_service import \
    get_standard_program_tree_version_from_transition_version
from program_management.formatter import format_tree_version_acronym
from program_management.forms.tree.fill_content import FillContentForm


class FillContentView(PermissionRequiredMixin, AjaxTemplateMixin, FormView):
    permission_required = 'program_management.change_training_version'
    raise_exception = True
    form_class = FillContentForm

    template_name = "tree_version/fill_content_inner.html"

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["year"] = self.tree_version.get_tree().root_node.academic_year
        context_data["tree_version_name"] = format_tree_version_acronym(self.tree_version)
        return context_data

    def get_form_kwargs(self) -> Dict:
        form_kwargs = super().get_form_kwargs()

        form_kwargs["past_transition_tree"] = self.get_past_tree_version()
        form_kwargs["standard_tree"] = self.get_standard_tree_version()
        form_kwargs["past_standard_tree"] = self.get_past_standard_tree_version()
        return form_kwargs

    def _get_version_transition_choices(self) -> Tuple:
        pass

    @functools.cached_property
    def tree_version(self) -> 'ProgramTreeVersion':
        get_cmd = command.GetProgramTreeVersionFromNodeCommand(
            code=self.kwargs['code'],
            year=self.kwargs['year']
        )
        return get_program_tree_version_from_node_service.get_program_tree_version_from_node(get_cmd)

    @functools.lru_cache()
    def get_past_tree_version(self) -> Optional['ProgramTreeVersion']:
        get_cmd = command.GetProgramTreeVersionFromNodeCommand(
            code=self.kwargs['code'],
            year=int(self.kwargs['year']) - 1
        )
        try:
            return get_program_tree_version_from_node_service.get_program_tree_version_from_node(get_cmd)
        except ProgramTreeVersionNotFoundException:
            return None

    @functools.lru_cache()
    def get_standard_tree_version(self) -> 'ProgramTreeVersion':
        cmd = GetStandardProgramTreeVersionFromTransitionVersionCommand(
            offer_acronym=self.tree_version.entity_id.offer_acronym,
            year=self.tree_version.entity_id.year
        )
        return get_standard_program_tree_version_from_transition_version(cmd)

    @functools.lru_cache()
    def get_past_standard_tree_version(self) -> Optional['ProgramTreeVersion']:
        cmd = GetStandardProgramTreeVersionFromTransitionVersionCommand(
            offer_acronym=self.tree_version.entity_id.offer_acronym,
            year=self.tree_version.entity_id.year - 1
        )
        return get_standard_program_tree_version_from_transition_version(cmd)

    def get_permission_object(self):
        return GroupYear.objects.select_related('management_entity').get(
            partial_acronym=self.kwargs['code'],
            academic_year__year=self.kwargs['year']
        )
