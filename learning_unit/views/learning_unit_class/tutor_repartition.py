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
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView

from base.ddd.utils.business_validator import MultipleBusinessExceptions
from base.views.common import display_success_messages, display_error_messages
from ddd.logic.attribution.commands import SearchAttributionCommand, SearchTutorsDistributedToClassCommand
from ddd.logic.attribution.dtos import TutorAttributionToLearningUnitDTO, TutorClassRepartitionDTO
from ddd.logic.learning_unit.commands import GetLearningUnitCommand, GetEffectiveClassCommand
from ddd.logic.learning_unit.domain.model.effective_class import EffectiveClass
from ddd.logic.learning_unit.domain.model.learning_unit import LearningUnit
from infrastructure.messages_bus import message_bus_instance
from learning_unit.forms.classes.tutor_repartition import ClassTutorRepartitionForm, ClassRemoveTutorRepartitionForm, \
    ClassEditTutorRepartitionForm
from learning_unit.models.learning_class_year import LearningClassYear


class TutorRepartitionView(PermissionRequiredMixin, FormView):
    template_name = "class/add_charge_repartition.html"
    permission_required = 'base.can_access_class'
    form_class = ClassTutorRepartitionForm

    @cached_property
    def effective_class(self) -> 'EffectiveClass':
        command = GetEffectiveClassCommand(
            class_code=self.kwargs['class_code'],
            learning_unit_code=self.kwargs['learning_unit_code'],
            learning_unit_year=self.kwargs['learning_unit_year']
        )
        return message_bus_instance.invoke(command)

    @cached_property
    def learning_unit(self) -> 'LearningUnit':
        command = GetLearningUnitCommand(code=self.kwargs['learning_unit_code'], year=self.kwargs['learning_unit_year'])
        return message_bus_instance.invoke(command)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        effective_class = self.effective_class
        learning_unit = self.learning_unit
        context.update(
            {
                'learning_unit': learning_unit,
                'effective_class': effective_class,
                'can_add_charge_repartition': True  # TODO je ne connais pas la condition
            }
        )
        return context

    def get_permission_object(self):
        return LearningClassYear.objects.filter(
            acronym=self.kwargs['class_code'],
            learning_component_year__learning_unit_year__academic_year__year=self.kwargs['learning_unit_year'],
            learning_component_year__learning_unit_year__acronym=self.kwargs['learning_unit_code']
        ).select_related(
            'learning_component_year__learning_unit_year',
            'learning_component_year__learning_unit_year__academic_year'
        )

    @cached_property
    def tutor(self) -> 'TutorAttributionToLearningUnitDTO':
        cmd = SearchAttributionCommand(
            learning_unit_attribution_uuid=self.kwargs['attribution_uuid'],
            learning_unit_year=self.effective_class.entity_id.learning_unit_identity.year,
            learning_unit_code=self.effective_class.entity_id.learning_unit_identity.code

        )
        return message_bus_instance.invoke(cmd)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['effective_class'] = self.effective_class
        kwargs['tutor'] = self.tutor
        kwargs['user'] = self.request.user
        return kwargs

    def post(self, request, *args, **kwargs):
        form = self.form_class(
            request.POST,
            user=request.user,
            tutor=self.tutor,
            effective_class=self.effective_class
        )
        try:
            form.save()
        except MultipleBusinessExceptions as e:
            display_error_messages(request, [exc.message for exc in e.exceptions])

        if not form.errors:
            display_success_messages(request, self.get_success_msg())
        return render(request, self.template_name, {
            "form": form,
        })

    def get_success_msg(self) -> str:
        return _("Repartition added for %(tutor)s (%(function)s)") % {
            'tutor': self.tutor.full_name,
            'function': self.tutor.function_text
        }

    def redirect_to_learning_unit_tutors(self):
        return redirect(
            reverse(
                'learning_unit_tutors',
                kwargs={
                    'learning_unit_code': self.learning_unit.code,
                    'learning_unit_year': self.learning_unit.year,
                    'class_code': self.effective_class.entity_id.class_code
                }
            )
        )


class TutorRepartitionRemoveView(TutorRepartitionView):
    template_name = "class/remove_charge_repartition.html"
    permission_required = 'base.can_access_class'
    form_class = ClassRemoveTutorRepartitionForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tutor'] = self.tutor
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_msg(self) -> str:
        return _("Repartition deleted for %(tutor)s (%(function)s)") % {
            'tutor': self.tutor.full_name,
            'function': self.tutor.function_text
        }


class TutorRepartitionEditView(TutorRepartitionView):
    template_name = "class/add_charge_repartition.html"
    permission_required = 'base.can_access_class'
    form_class = ClassEditTutorRepartitionForm

    @cached_property
    def tutor(self) -> 'TutorClassRepartitionDTO':
        command = SearchTutorsDistributedToClassCommand(
            learning_unit_code=self.learning_unit.code,
            learning_unit_year=self.learning_unit.year,
            class_code=self.effective_class.class_code,
        )
        tutors = message_bus_instance.invoke(command)
        for tutor in tutors:
            if str(tutor.attribution_uuid) == str(self.kwargs['attribution_uuid']):
                return tutor

    def get_success_msg(self) -> str:
        return _("Repartition edited for %(tutor)s (%(function)s)") % {
            'tutor': self.tutor.full_name,
            'function': self.tutor.function_text
        }
