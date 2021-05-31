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
from django.db.models import QuerySet
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView

from base.models.learning_unit_year import LearningUnitYear
from base.views.common import display_success_messages
from ddd.logic.learning_unit.commands import GetLearningUnitCommand
from ddd.logic.learning_unit.domain.model.effective_class import EffectiveClassIdentity
from ddd.logic.learning_unit.domain.model.learning_unit import LearningUnit
from infrastructure.messages_bus import message_bus_instance
from learning_unit.forms.classes.create import ClassForm


class CreateClassView(PermissionRequiredMixin, FormView):
    template_name = "class/creation.html"
    form_class = ClassForm
    permission_required = 'base.can_create_class'

    @cached_property
    def year(self) -> int:
        return self.kwargs['learning_unit_year']

    @cached_property
    def learning_unit_code(self) -> int:
        return self.kwargs['learning_unit_code']

    @cached_property
    def learning_unit(self) -> 'LearningUnit':
        return message_bus_instance.invoke(
            GetLearningUnitCommand(code=self.learning_unit_code, year=self.year)
        )

    # def get(self, request, *args, **kwargs):
    #     if message_bus_instance.invoke():
    #
    #     return super().get(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['learning_unit'] = self.learning_unit
        return kwargs

    def get_permission_object(self):
        return LearningUnitYear.objects.filter(
            academic_year__year=self.year,
            acronym=self.learning_unit_code
        ).select_related(
            'learning_container_year',
            'academic_year',
        )

    def post(self, request, *args, **kwargs):
        form = ClassForm(request.POST, learning_unit=self.learning_unit)
        effective_class_identity = form.save()
        if not form.errors:
            display_success_messages(request, self.get_success_msg(effective_class_identity), extra_tags='safe')
            return redirect(
                reverse('learning_unit', kwargs={'acronym': self.learning_unit_code, 'year': self.year})
            )

        return render(request, self.template_name, {
            "form": form,
        })

    def get_success_msg(self, effective_class_identity: 'EffectiveClassIdentity') -> str:
        return _("Class %(class_identity)s successfully created.") % {
            "class_identity": effective_class_identity,
        }
