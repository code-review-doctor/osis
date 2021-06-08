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
from django.views.generic import TemplateView
from reversion.models import Version

from base.models.learning_unit_year import LearningUnitYear
from ddd.logic.learning_unit.commands import GetLearningUnitCommand
from ddd.logic.learning_unit.domain.model.learning_unit import LearningUnit
from infrastructure.messages_bus import message_bus_instance
from learning_unit.models.learning_class_year import LearningClassYear
from django.utils.translation import gettext_lazy as _


class ClassIdentificationView(PermissionRequiredMixin, TemplateView):
    template_name = "class/identification_tab.html"
    permission_required = 'base.can_access_class'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # effective_class = self.get_effective_class() TODO: after 4270 integration,
        learning_unit = self.get_learning_unit()
        context.update(
            {
                'learning_unit_year': self.get_learning_unit_year(),
                'learning_unit': learning_unit,
                # 'effective_class': None TODO: after 5880,
                'effective_class': {'quadrimester': 'Q1'},
                'show_button': True,
                # 'class_type': self.get_class_type(learning_unit) TODO: after 4270 integration,
                # 'volumes': self.get_volumes(learning_unit) TODO: after 4270 integration
                'history': self.get_related_history(),
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
    # TODO :: uncomment below, after 4270 integration
    # def get_effective_class(self) -> 'EffectiveClass':
    #     command = GetEffectiveClassCommand(
    #         class_code=self.kwargs['class_code'],
    #         learning_unit_code=self.kwargs['learning_unit_code'],
    #         learning_unit_year=self.kwargs['learning_unit_year']
    #     )
    #     return message_bus_instance.invoke(command)

    # TODO :: uncomment below, after 4270 integration
    # def get_class_type(learning_unit):
    #     if learning_unit.has_practical_volume() and not learning_unit.has_lecturing_volume():
    #         return _('Practical exercises')
    #     return _('Lecturing')
    #

    # TODO :: uncomment below, after 4270 integration
    # def get_learning_unit(learning_unit):
    #     if learning_unit.has_practical_volume() and not learning_unit.has_lecturing_volume():
    #         return learning_unit.practical_part.volumes
    #         self.fields['class_type'].initial = _('Practical exercises')
    #     else:
    #         return learning_unit.lecturing_part.volumes
    #         self.fields['class_type'].initial = _('Lecturing')

    def get_related_history(self):
        pass
        # todo :: uncomment below,  when LearningClassYear will be registered in django reversion
        # effective_class = LearningClassYear.objects.get(pk=26) #TODO :: adapter ceci
        # versions = Version.objects.get_for_object(
        #     effective_class
        # ).select_related('revision__user__person')
        #
        # related_models = [
        #     LearningClassYear,
        # ]
        #
        # subversion = Version.objects.none()
        # for model in related_models:
        #     subversion |= Version.objects.get_for_model(model).select_related('revision__user__person')
        #
        # versions |= subversion.filter(
        #     serialized_data__contains="\"learning_class_year\": {}".format(effective_class.pk)
        # )
        #
        # return versions.order_by('-revision__date_created').distinct('revision__date_created')
