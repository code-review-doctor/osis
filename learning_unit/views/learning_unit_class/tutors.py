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
from django.utils.functional import cached_property
from django.views.generic import TemplateView

from ddd.logic.attribution.commands import SearchTutorAttributedToLearningUnitCommand
from ddd.logic.attribution.domain.model.tutor import Tutor
from ddd.logic.learning_unit.commands import GetLearningUnitCommand, GetEffectiveClassCommand
from ddd.logic.learning_unit.domain.model.learning_unit import LearningUnit
from infrastructure.messages_bus import message_bus_instance
from learning_unit.models.learning_class_year import LearningClassYear


class ClassTutorsView(PermissionRequiredMixin, TemplateView):
    template_name = "class/tutors_tab.html"
    permission_required = 'learning_unit.view_learningclassyear'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                'learning_unit': self.learning_unit,
                'effective_class': self.effective_class,
                'tutors': self.tutors,
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
    def learning_unit(self) -> 'LearningUnit':
        command = GetLearningUnitCommand(code=self.kwargs['learning_unit_code'], year=self.kwargs['learning_unit_year'])
        return message_bus_instance.invoke(command)

    @cached_property
    def effective_class(self) -> 'EffectiveClass':
        command = GetEffectiveClassCommand(
            class_code=self.kwargs['class_code'],
            learning_unit_code=self.kwargs['learning_unit_code'],
            learning_unit_year=self.kwargs['learning_unit_year']
        )
        return message_bus_instance.invoke(command)

    @cached_property
    def tutors(self) -> List['Tutor']:
        command = SearchTutorAttributedToLearningUnitCommand(
            learning_unit_code=self.kwargs['learning_unit_code'],
            learning_unit_year=self.kwargs['learning_unit_year']
        )
        return message_bus_instance.invoke(command)
