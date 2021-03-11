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
from typing import Optional

from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from django.views.generic import FormView

from base.models.enums import education_group_categories
from base.views.mixins import AjaxTemplateMixin
from education_group.models.group_year import GroupYear
from osis_role.contrib.views import PermissionRequiredMixin
from program_management.ddd import command
from program_management.ddd.domain.program_tree_version import ProgramTreeVersion
from program_management.ddd.service.read import get_program_tree_version_service, \
    get_program_tree_version_origin_service
from program_management.forms.fill_content import FillContentForm


class FillTransitionVersionContentView(PermissionRequiredMixin, AjaxTemplateMixin, FormView):
    template_name = "tree_version/fill_content_inner.html"
    form_class = FillContentForm

    @functools.lru_cache()
    def get_permission_object(self) -> GroupYear:
        return get_object_or_404(
            GroupYear,
            academic_year__year=self.kwargs['year'],
            partial_acronym=self.kwargs['code'],
        )

    @cached_property
    def transition_tree(self) -> 'ProgramTreeVersion':
        return get_program_tree_version_service.get_program_tree_version(
            command.GetProgramTreeVersionCommand(code=self.kwargs['code'], year=self.kwargs['year'])
        )

    @cached_property
    def last_year_transition_tree(self) -> Optional['ProgramTreeVersion']:
        return get_program_tree_version_service.get_program_tree_version(
            command.GetProgramTreeVersionCommand(code=self.kwargs['code'], year=int(self.kwargs['year']) - 1)
        )

    @cached_property
    def version_tree(self) -> 'ProgramTreeVersion':
        return get_program_tree_version_origin_service.get_program_tree_version_origin(
            command.GetProgramTreeVersionOriginCommand(
                year=self.kwargs['year'],
                offer_acronym=self.transition_tree.entity_id.offer_acronym,
                transition_name=self.transition_tree.entity_id.transition_name,
                version_name=self.transition_tree.entity_id.version_name
            )
        )

    @cached_property
    def last_year_version_tree(self) -> 'ProgramTreeVersion':
        return get_program_tree_version_service.get_program_tree_version(
            command.GetProgramTreeVersionCommand(
                year=self.kwargs['year'],
                code=self.version_tree.program_tree_identity.code
            )
        )

    def get_permission_required(self):
        if self.get_permission_object().education_group_type.category == education_group_categories.TRAINING:
            return ("base.fill_training_version",)
        return ("base.fill_minitraining_version",)
