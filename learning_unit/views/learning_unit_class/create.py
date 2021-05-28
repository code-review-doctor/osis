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

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import FormView

from base.models.learning_unit_year import get_by_id, LearningUnitYear
from learning_unit.forms.classes.create import ClassForm


class Create(PermissionRequiredMixin, FormView):
    template_name = "class/creation.html"
    form_class = ClassForm
    permission_required = 'base.can_create_class'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                'learning_unit_year': get_by_id(self.kwargs['learning_unit_year_id']),
            }
        )
        return context

    def get_permission_object(self):
        return LearningUnitYear.objects.filter(id=self.kwargs['learning_unit_year_id']).\
            select_related('learning_container_year', 'academic_year')
