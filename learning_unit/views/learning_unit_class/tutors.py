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

from ddd.logic.attribution.commands import SearchTutorsDistributedToClassCommand
from ddd.logic.attribution.dtos import TutorClassRepartitionDTO
from ddd.logic.learning_unit.commands import GetEffectiveClassCommand
from infrastructure.messages_bus import message_bus_instance
from learning_unit.models.learning_class_year import LearningClassYear
from learning_unit.views.learning_unit_class.common import common_url_tabs


class ClassTutorsView(PermissionRequiredMixin, TemplateView):
    template_name = "class/tutors_tab.html"
    permission_required = 'learning_unit.view_learningclassyear'

    @property
    def class_code(self) -> str:
        return self.kwargs['class_code']

    @property
    def learning_unit_code(self) -> str:
        return self.kwargs['learning_unit_code']

    @property
    def learning_unit_year(self) -> str:
        return self.kwargs['learning_unit_year']

    @cached_property
    def effective_class(self) -> 'EffectiveClass':
        # Mandatory to display the complete_code of effective_class in html page title
        command = GetEffectiveClassCommand(
            class_code=self.kwargs['class_code'],
            learning_unit_code=self.kwargs['learning_unit_code'],
            learning_unit_year=self.kwargs['learning_unit_year']
        )
        return message_bus_instance.invoke(command)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                'effective_class': self.effective_class,
                'tutors': self.tutors,
                'can_delete_attribution': True  #  todo je ne sais pas trop quel droit on doit vérifier ici
            }
        )
        context.update(common_url_tabs(self.learning_unit_code, self.learning_unit_year, self.class_code))
        return context

    def get_permission_object(self):
        return LearningClassYear.objects.filter(
            acronym=self.kwargs['class_code'],
            learning_component_year__learning_unit_year__academic_year__year=self.learning_unit_year,
            learning_component_year__learning_unit_year__acronym=self.learning_unit_code,
        ).select_related(
            'learning_component_year__learning_unit_year',
            'learning_component_year__learning_unit_year__academic_year'
        )

    @cached_property
    def tutors(self) -> List['TutorClassRepartitionDTO']:
        command = SearchTutorsDistributedToClassCommand(
            learning_unit_code=self.learning_unit_code,
            learning_unit_year=self.learning_unit_year,
            class_code=self.class_code,
        )
        return message_bus_instance.invoke(command)
