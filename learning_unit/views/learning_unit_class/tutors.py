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

from attribution.views.attribution import _get_classes_charge_repartition_warning_messages
from ddd.logic.effective_class_repartition.commands import SearchTutorsDistributedToClassCommand
from ddd.logic.effective_class_repartition.dtos import TutorClassRepartitionDTO
from infrastructure.messages_bus import message_bus_instance
from learning_unit.views.learning_unit_class.common import CommonClassView


class ClassTutorsView(CommonClassView, TemplateView):
    template_name = "class/tutors_tab.html"
    permission_required = 'learning_unit.view_learningclassyear'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                'year': self.year,
                'learning_unit_year': self.learning_unit_year,
                'effective_class': self.effective_class,
                'learning_unit': self.learning_unit,
                'tutors': self.tutors,
                'can_delete_attribution': self.request.user.has_perm(
                    "attribution.can_delete_class_repartition", self.get_permission_object()
                ),
                'can_change_attribution': self.request.user.has_perm(
                    "attribution.can_change_class_repartition", self.get_permission_object()
                ),
                'warnings': self.get_warning_messages()
            }
        )
        context.update(self.common_url_tabs())
        return context

    @cached_property
    def tutors(self) -> List['TutorClassRepartitionDTO']:
        command = SearchTutorsDistributedToClassCommand(
            learning_unit_code=self.learning_unit_code,
            learning_unit_year=self.year,
            class_code=self.class_code,
        )
        return message_bus_instance.invoke(command)

    def get_warning_messages(self):
        return _get_classes_charge_repartition_warning_messages(self.learning_unit_year)
