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
from typing import List

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import TemplateView

from attribution.models.enums.function import COORDINATOR
from base.models.learning_unit_year import LearningUnitYear
from ddd.logic.attribution.domain.model._attribution import LearningUnitAttribution, LearningUnitAttributionIdentity
from ddd.logic.attribution.domain.model._class_volume_repartition import ClassVolumeRepartition
from ddd.logic.attribution.domain.model.tutor import Tutor, TutorIdentity
from ddd.logic.learning_unit.commands import GetLearningUnitCommand, GetEffectiveClassCommand
from ddd.logic.learning_unit.domain.model.learning_unit import LearningUnit
from infrastructure.messages_bus import message_bus_instance
from learning_unit.models.learning_class_year import LearningClassYear


class ClassTutorsView(PermissionRequiredMixin, TemplateView):
    template_name = "class/tutors_tab.html"
    permission_required = 'base.can_access_class'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        effective_class = self.get_effective_class()
        learning_unit = self.get_learning_unit()
        context.update(
            {
                'learning_unit_year': self.get_learning_unit_year(),
                'learning_unit': learning_unit,
                'effective_class': effective_class,
                'tutors': self.get_class_tutors(),
            }
        )
        return context

    def get_learning_unit_year(self):
        return LearningUnitYear.objects.get(
            acronym=self.kwargs['learning_unit_code'],
            academic_year__year=self.kwargs['learning_unit_year']
        )

    def get_permission_object(self):
        return LearningClassYear.objects.filter(
            acronym=self.kwargs['class_code'],
            learning_component_year__learning_unit_year__academic_year__year=self.kwargs['learning_unit_year'],
            learning_component_year__learning_unit_year__acronym=self.kwargs['learning_unit_code']
        ).select_related(
            'learning_component_year__learning_unit_year',
            'learning_component_year__learning_unit_year__academic_year'
        )

    def get_learning_unit(self) -> 'LearningUnit':
        command = GetLearningUnitCommand(code=self.kwargs['learning_unit_code'], year=self.kwargs['learning_unit_year'])
        return message_bus_instance.invoke(command)

    def get_effective_class(self) -> 'EffectiveClass':
        command = GetEffectiveClassCommand(
            class_code=self.kwargs['class_code'],
            learning_unit_code=self.kwargs['learning_unit_code'],
            learning_unit_year=self.kwargs['learning_unit_year']
        )
        return message_bus_instance.invoke(command)

    def get_class_tutors(self) -> List['Tutor']:
        # replace with service result
        return [
            Tutor(
                entity_id=TutorIdentity(personal_id_number='id_number'),
                first_name='Toto',
                last_name='Tutu',
                attributions=[
                    LearningUnitAttribution(
                        entity_id=LearningUnitAttributionIdentity(uuid='uuid'),
                        function=COORDINATOR,
                        learning_unit=self.get_learning_unit().entity_id,
                        distributed_effective_classes=[
                            ClassVolumeRepartition(
                                effective_class=self.get_effective_class().entity_id,
                                distributed_volume=10
                            )
                        ]
                    )
                ]
            )
        ]
