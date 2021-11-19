##############################################################################
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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from django.views.generic import FormView, TemplateView

from base.business.learning_units.pedagogy import is_pedagogy_data_must_be_postponed, postpone_teaching_materials
from base.forms.learning_unit_pedagogy import TeachingMaterialModelForm
from base.models.learning_unit_year import LearningUnitYear
from base.models.teaching_material import TeachingMaterial
from base.views.common import display_success_messages
from base.views.learning_units.pedagogy import update as update_pedagogy
from osis_role.contrib.views import PermissionRequiredMixin


class CommonTeachingMaterial(LoginRequiredMixin, PermissionRequiredMixin):
    permission_required = 'base.can_edit_learningunit_pedagogy'
    raise_exception = True

    @cached_property
    def learning_unit_year(self):
        return get_object_or_404(LearningUnitYear, pk=self.kwargs['learning_unit_year_id'])

    def get_permission_object(self):
        return self.learning_unit_year

    @cached_property
    def teaching_material(self):
        return get_object_or_404(
            TeachingMaterial,
            pk=self.kwargs['teaching_material_id'],
            learning_unit_year_id=self.kwargs['learning_unit_year_id']
        )


class CreateTeachingMaterial(CommonTeachingMaterial, FormView):
    form_class = TeachingMaterialModelForm
    template_name = "learning_unit/teaching_material/modal_edit.html"

    def form_valid(self, form):
        form.save(learning_unit_year=self.learning_unit_year)
        last_luy_reported = self.learning_unit_year.find_gt_learning_units_year().last()
        display_success_messages(
            self.request,
            update_pedagogy.build_success_message(last_luy_reported, self.learning_unit_year)
        )
        return JsonResponse({})


class UpdateTeachingMaterial(CommonTeachingMaterial, FormView):
    form_class = TeachingMaterialModelForm
    template_name = "learning_unit/teaching_material/modal_edit.html"

    def form_valid(self, form):
        form.save(learning_unit_year=self.learning_unit_year)
        last_luy_reported = self.learning_unit_year.find_gt_learning_units_year().last()
        display_success_messages(
            self.request,
            update_pedagogy.build_success_message(last_luy_reported, self.learning_unit_year)
        )
        return JsonResponse({})

    def get_form_kwargs(self, **kwargs):
        return {
            **super().get_form_kwargs(),
            'instance': self.teaching_material
        }


class DeleteTeachingMaterial(CommonTeachingMaterial, TemplateView):
    template_name = "learning_unit/teaching_material/modal_delete.html"

    def post(self, request, *args, **kwargs):
        last_luy_reported = self.learning_unit_year.find_gt_learning_units_year().last()
        self.teaching_material.delete()
        if is_pedagogy_data_must_be_postponed(self.learning_unit_year):
            postpone_teaching_materials(self.learning_unit_year)
        display_success_messages(
            request,
            update_pedagogy.build_success_message(last_luy_reported, self.learning_unit_year)
        )
        return JsonResponse({})
