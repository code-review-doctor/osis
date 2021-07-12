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

from django.utils.functional import cached_property
from django.views.generic import TemplateView

from base.business.learning_unit import get_same_container_year_components
from ddd.logic.learning_unit.commands import GetEffectiveClassVolumesWarningsCommand
from infrastructure.messages_bus import message_bus_instance
from learning_unit.views.learning_unit_class.common import CommonClassView


class ClassComponentsView(CommonClassView, TemplateView):
    template_name = "class/components_tab.html"
    permission_required = 'learning_unit.view_learningclassyear'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        data_components = get_same_container_year_components(self.learning_unit_year)
        context['components'] = data_components.get('components')
        context['REQUIREMENT_ENTITY'] = data_components.get('REQUIREMENT_ENTITY')
        context['ADDITIONAL_REQUIREMENT_ENTITY_1'] = data_components.get('ADDITIONAL_REQUIREMENT_ENTITY_1')
        context['ADDITIONAL_REQUIREMENT_ENTITY_2'] = data_components.get('ADDITIONAL_REQUIREMENT_ENTITY_2')

        context.update(
            {
                'year': self.year,
                'learning_unit_year': self.learning_unit_year,
                'effective_class': self.effective_class,
                'learning_unit': self.learning_unit,
                'no_class_redirection': True,
                'warnings': self.warnings
            }
        )
        context.update(self.common_url_tabs())
        return context

    @cached_property
    def warnings(self) -> List[str]:
        command = GetEffectiveClassVolumesWarningsCommand(
            class_code=self.class_code,
            learning_unit_code=self.learning_unit_code,
            learning_unit_year=self.year
        )
        return message_bus_instance.invoke(command)
