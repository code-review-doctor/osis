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

from django.views.generic import TemplateView

from ddd.logic.effective_class_repartition.commands import SearchAttributionsToLearningUnitCommand, \
    SearchTutorsDistributedToClassCommand
from ddd.logic.effective_class_repartition.dtos import TutorAttributionToLearningUnitDTO
from infrastructure.messages_bus import message_bus_instance
from learning_unit.views.learning_unit_class.common import CommonClassView

PersonalIdNumber = str


class LearningUnitTutorsView(CommonClassView, TemplateView):
    template_name = "class/lu_tutors.html"
    permission_required = 'attribution.can_change_class_repartition'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                'effective_class': self.effective_class,
                'learning_unit_attributions': self.get_learning_unit_attributions(),
                'learning_unit': self.learning_unit,
                'learning_unit_year': self.learning_unit_year,
                'attributions_uuid_already_assigned': self.get_attribution_uuids_assigned_to_class(),
                'can_add_charge_repartition': self.request.user.has_perm(
                    "attribution.can_change_class_repartition", self.get_permission_object()
                )
            }
        )
        context.update(self.common_url_tabs())
        return context

    def get_learning_unit_attributions(self) -> List['TutorAttributionToLearningUnitDTO']:
        return message_bus_instance.invoke(
            SearchAttributionsToLearningUnitCommand(
                learning_unit_code=self.effective_class.entity_id.learning_unit_identity.code,
                learning_unit_year=self.effective_class.entity_id.learning_unit_identity.year
            )
        )

    def get_attribution_uuids_assigned_to_class(self) -> List[str]:
        tutor_dtos = message_bus_instance.invoke(
            SearchTutorsDistributedToClassCommand(
                learning_unit_code=self.effective_class.entity_id.learning_unit_identity.code,
                learning_unit_year=self.effective_class.entity_id.learning_unit_identity.year,
                class_code=self.effective_class.class_code,
            )
        )
        return [tutor.attribution_uuid for tutor in tutor_dtos]
