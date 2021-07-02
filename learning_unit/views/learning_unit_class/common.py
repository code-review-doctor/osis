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

from typing import Dict

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse
from django.utils.functional import cached_property

from base.models.learning_unit_year import LearningUnitYear
from ddd.logic.learning_unit.commands import GetLearningUnitCommand, GetEffectiveClassCommand
from ddd.logic.learning_unit.domain.model.effective_class import EffectiveClass
from ddd.logic.learning_unit.domain.model.learning_unit import LearningUnit
from infrastructure.messages_bus import message_bus_instance
from learning_unit.models.learning_class_year import LearningClassYear


class CommonClassView(PermissionRequiredMixin):
    @property
    def class_code(self) -> str:
        return self.kwargs['class_code']

    @property
    def learning_unit_code(self) -> str:
        return self.kwargs['learning_unit_code']

    @property
    def year(self) -> str:
        return self.kwargs['learning_unit_year']

    @cached_property
    def learning_unit(self) -> 'LearningUnit':
        command = GetLearningUnitCommand(code=self.learning_unit_code, year=self.year)
        return message_bus_instance.invoke(command)

    @cached_property
    def effective_class(self) -> 'EffectiveClass':
        # Mandatory to display the complete_code of effective_class in html page title
        command = GetEffectiveClassCommand(
            class_code=self.class_code,
            learning_unit_code=self.learning_unit_code,
            learning_unit_year=self.year
        )
        return message_bus_instance.invoke(command)

    @cached_property
    def learning_unit_year(self):
        return LearningUnitYear.objects.get(
            acronym=self.learning_unit_code,
            academic_year__year=self.year
        )

    def get_permission_object(self):
        return LearningClassYear.objects.filter(
            acronym=self.class_code,
            learning_component_year__learning_unit_year__academic_year__year=self.year,
            learning_component_year__learning_unit_year__acronym=self.learning_unit_code,
        ).select_related(
            'learning_component_year__learning_unit_year',
            'learning_component_year__learning_unit_year__academic_year'
        )

    def common_url_tabs(self) -> Dict[str, str]:
        url_kwargs = {
            'learning_unit_year': self.year,
            'learning_unit_code': self.learning_unit_code,
            'class_code': self.class_code
        }
        return {
            'url_class_tutors': reverse("class_tutors", kwargs=url_kwargs),
            'url_class_identification': reverse("class_identification", kwargs=url_kwargs),
            'url_lu_tutors': reverse("learning_unit_tutors", kwargs=url_kwargs),
        }
