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

from django.shortcuts import get_object_or_404
from django.views.generic import FormView

from base.models.enums import education_group_categories
from base.views.mixins import AjaxTemplateMixin
from education_group.models.group_year import GroupYear
from osis_role.contrib.views import PermissionRequiredMixin
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

    def get_permission_required(self):
        if self.get_permission_object().education_group_type.category == education_group_categories.TRAINING:
            return ("base.fill_training_version",)
        return ("base.fill_minitraining_version",)
