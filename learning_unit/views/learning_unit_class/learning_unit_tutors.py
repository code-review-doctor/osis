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

from base.models.enums.component_type import LECTURING, PRACTICAL_EXERCISES
from ddd.logic.attribution.commands import SearchAttributionsToLearningUnitCommand
from ddd.logic.attribution.dtos import TutorAttributionToLearningUnitDTO
from ddd.logic.learning_unit.domain.model.effective_class import EffectiveClass, PracticalEffectiveClass
from infrastructure.messages_bus import message_bus_instance
from learning_unit.views.learning_unit_class.common import CommonClassView


class LearningUnitTutorsView(CommonClassView, TemplateView):
    template_name = "class/lu_tutors.html"
    permission_required = 'base.can_access_class'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                'effective_class': self.effective_class,
                'tutors':
                    self.get_ue_tutors(),
                'can_add_charge_repartition': True,  # TODO je ne connais pas la condition,
                'can_delete_attribution': True  # TODO je ne connais pas la condition,
            }
        )
        context.update(self.common_url_tabs())
        return context

    def get_ue_tutors(self) -> List['TutorAttributionToLearningUnitDTO']:
        tutors = message_bus_instance.invoke(
            SearchAttributionsToLearningUnitCommand(
                learning_unit_code=self.effective_class.entity_id.learning_unit_identity.code,
                learning_unit_year=self.effective_class.entity_id.learning_unit_identity.year,
            )
        )

        return _filter_tutors_by_class_type(self.effective_class, tutors)


def _filter_tutors_by_class_type(
        effective_class: 'EffectiveClass',
        tutors: List['TutorAttributionToLearningUnitDTO']
) -> List['TutorAttributionToLearningUnitDTO']:
    effective_class_type = \
        PRACTICAL_EXERCISES if isinstance(effective_class, PracticalEffectiveClass) else LECTURING
    return [tutor for tutor in tutors if effective_class_type == tutor.component_type]
