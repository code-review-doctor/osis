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
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView

from base.ddd.utils.business_validator import MultipleBusinessExceptions
from base.models.learning_unit_year import LearningUnitYear
from base.views.common import display_success_messages, display_error_messages
from ddd.logic.learning_unit.commands import GetLearningUnitCommand, GetEffectiveClassCommand, \
    CanDeleteEffectiveClassCommand
from ddd.logic.learning_unit.domain.model.effective_class import EffectiveClass
from ddd.logic.learning_unit.domain.model.learning_unit import LearningUnit
from infrastructure.messages_bus import message_bus_instance
from learning_unit.forms.classes.update import DeleteClassForm


class DeleteClassView(PermissionRequiredMixin, FormView):
    form_class = DeleteClassForm
    permission_required = 'learning_unit.change_learningclassyear'
    force_reload = True

    @cached_property
    def year(self) -> int:
        return self.kwargs['learning_unit_year']

    @cached_property
    def learning_unit_code(self) -> int:
        return self.kwargs['learning_unit_code']

    @cached_property
    def class_code(self) -> int:
        return self.kwargs['class_code']

    @cached_property
    def learning_unit(self) -> 'LearningUnit':
        return message_bus_instance.invoke(
            GetLearningUnitCommand(code=self.learning_unit_code, year=self.year)
        )

    @cached_property
    def effective_class(self) -> 'EffectiveClass':
        return message_bus_instance.invoke(
            GetEffectiveClassCommand(
                class_code=self.class_code,
                learning_unit_code=self.learning_unit_code,
                learning_unit_year=self.year
            )
        )

    @cached_property
    def cancel_url(self):
        return reverse(
            'class_identification',
            kwargs={
                'learning_unit_year': self.effective_class.year,
                'learning_unit_code': self.effective_class.learning_unit_code,
                'class_code': self.effective_class.class_code,
            }
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['effective_class'] = self.effective_class
        context['cancel_url'] = self.cancel_url
        return context

    def get_permission_object(self):
        return LearningUnitYear.objects.filter(
            academic_year__year=self.year,
            acronym=self.learning_unit_code
        ).select_related(
            'learning_container_year',
            'academic_year',
        )

    def post(self, request, *args, **kwargs):
        effective_class_to_delete_complete_code = self.effective_class.complete_code

        try:
            message_bus_instance.invoke(
                CanDeleteEffectiveClassCommand(learning_unit_code=self.learning_unit_code, year=self.year, class_code=self.effective_class.class_code)
            )
            form = DeleteClassForm(
                request.POST,
                effective_class=self.effective_class,

            )
            form.save()
            if not form.errors:
                display_success_messages(request, self.get_success_msg(effective_class_to_delete_complete_code), extra_tags='safe')
                return self.redirect_to_learning_unit_identification()

            return render(request, self.template_name, {
                "form": form,
            })
        except MultipleBusinessExceptions as e:
            display_error_messages(request, [exc.message for exc in e.exceptions])
            return self.redirect_to_effective_class_identification()

    def redirect_to_learning_unit_identification(self):
        return HttpResponseRedirect(
            reverse('learning_unit', kwargs={'acronym': self.learning_unit_code, 'year': self.year})
        )

    def get_success_msg(self, effective_class_to_delete_complete_code: str) -> str:
        return _("Class %(effective_class_complete_acronym)s successfully deleted.") % {
            "effective_class_complete_acronym": effective_class_to_delete_complete_code
        }

    def redirect_to_effective_class_identification(self):
        return redirect(
            reverse('class_identification',
                    kwargs={
                        'learning_unit_year': self.year,
                        'learning_unit_code': self.learning_unit_code,
                        'class_code': self.effective_class.entity_id.class_code
                    }
                    )
        )
