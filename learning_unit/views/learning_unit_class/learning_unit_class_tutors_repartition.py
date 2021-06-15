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
from django.views.generic import TemplateView

from attribution.models.enums.function import Functions
from base.models.enums.learning_component_year_type import LECTURING, PRACTICAL_EXERCISES
from base.views.common import display_success_messages
from ddd.logic.attribution.domain.model._attribution import LearningUnitAttribution, LearningUnitAttributionIdentity
from ddd.logic.attribution.domain.model._class_volume_repartition import ClassVolumeRepartition
from ddd.logic.attribution.domain.model.tutor import Tutor, TutorIdentity
from ddd.logic.learning_unit.commands import GetLearningUnitCommand, GetEffectiveClassCommand
from ddd.logic.learning_unit.domain.model.learning_unit import LearningUnit
from infrastructure.messages_bus import message_bus_instance
from learning_unit.forms.classes.tutor_repartition import ClassTutorRepartitionForm
from learning_unit.models.learning_class_year import LearningClassYear


class LearningUnitClassRepartitionTutorsView(PermissionRequiredMixin, TemplateView):
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
                'class_type': get_class_type(learning_unit),
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

    def get_tutor(self) -> 'Tutor':
        # TODo remplacer par get tutor cmd
        return Tutor(
            entity_id=TutorIdentity(personal_id_number='id_number'),
            first_name='Toto',
            last_name='Tutu',
            attributions=[
                LearningUnitAttribution(
                    entity_id=LearningUnitAttributionIdentity(uuid='uuid'),
                    function=Functions['COORDINATOR'],
                    learning_unit=self.learning_unit.entity_id,
                    distributed_effective_classes=[
                        ClassVolumeRepartition(
                            effective_class=self.effective_class.entity_id,
                            distributed_volume=10
                        )
                    ]
                )
            ]
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['learning_unit_attribution'] = self.learning_unit_attribution
        kwargs['effective_class'] = self.effective_class
        kwargs['tutor'] = None
        kwargs['user'] = self.request.user
        return kwargs

    def post(self, request, *args, **kwargs):
        form = ClassTutorRepartitionForm(
            request.POST,
            user=request.user,
            learning_unit_attribution=self.get_learning_unit_attribution('777'),
            tutor=self.get_tutor(),
            effective_class=self.effective_class
        )
        repartition_identity = form.save()
        if not form.errors:
            display_success_messages(request, self.get_success_msg(repartition_identity), extra_tags='safe')
            return self.redirect_to_learning_unit_identification()

        return render(request, self.template_name, {
            "form": form,
        })

    def get(self, request, *args, **kwargs):
        attribution_uuid = self.kwargs['attribution_uuid']

        form = ClassTutorRepartitionForm(
            user=self.request.user,
            tutor=self.get_tutor(),
            effective_class=self.effective_class,
            learning_unit_attribution=self.get_learning_unit_attribution(attribution_uuid)
        )
        context = self.get_context_data()
        context.update({'form': form})
        return render(request, self.template_name, context)

    def get_learning_unit_attribution(self, attribution_uuid):
        # TODO : remplacer par cmd et message_bus
        return LearningUnitAttribution(
                            entity_id=LearningUnitAttributionIdentity(uuid='uuid'),
                            function=Functions['COORDINATOR'],
                            learning_unit=self.learning_unit.entity_id,
                            distributed_effective_classes=[
                                ClassVolumeRepartition(
                                    effective_class=self.effective_class.entity_id,
                                    distributed_volume=10
                                )
                            ]
                        )

    def redirect_to_learning_unit_identification(self):
        return redirect(
            reverse(
                'lu_class_tutors',
                kwargs={
                    'learning_unit_year': self.learning_unit.code,
                    'learning_unit_year': self.learning_unit.year,
                    'class_code': self.effective_class.entity_id.class_code
                }
            )
        )


def get_class_type(learning_unit: 'LearningUnit') -> str:
    if learning_unit.has_practical_volume() and not learning_unit.has_lecturing_volume():
        return PRACTICAL_EXERCISES
    return LECTURING
