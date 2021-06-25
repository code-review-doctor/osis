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

from ddd.logic.attribution.commands import SearchAttributionsToLearningUnitCommand
from ddd.logic.attribution.domain.model.tutor import Tutor
from ddd.logic.learning_unit.commands import GetEffectiveClassCommand
from ddd.logic.learning_unit.domain.model.effective_class import EffectiveClass
from infrastructure.messages_bus import message_bus_instance
from learning_unit.models.learning_class_year import LearningClassYear
from learning_unit.views.learning_unit_class.common import common_url_tabs


class LearningUnitTutorsView(PermissionRequiredMixin, TemplateView):
    template_name = "class/lu_tutors.html"
    permission_required = 'base.can_access_class'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        effective_class = self.get_effective_class()
        context.update(
            {
                'effective_class': effective_class,
                'tutors':
                    self.get_ue_tutors(),
                'can_add_charge_repartition': True  # TODO je ne connais pas la condition
            }
        )
        context.update(
            common_url_tabs(
                effective_class.entity_id.learning_unit_identity.code,
                effective_class.entity_id.learning_unit_identity.year,
                effective_class.entity_id.class_code)
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

    def get_effective_class(self) -> 'EffectiveClass':
        command = GetEffectiveClassCommand(
            class_code=self.kwargs['class_code'],
            learning_unit_code=self.kwargs['learning_unit_code'],
            learning_unit_year=self.kwargs['learning_unit_year']
        )
        return message_bus_instance.invoke(command)

    def get_ue_tutors(self) -> List['Tutor']:
        # TODO : ici on a le double d'attribution on devrait filtrer par type (PP ou PM) à discuter
        return message_bus_instance.invoke(
            SearchAttributionsToLearningUnitCommand(
                learning_unit_code=self.get_effective_class().entity_id.learning_unit_identity.code,
                learning_unit_year=self.get_effective_class().entity_id.learning_unit_identity.year,
            )
        )
