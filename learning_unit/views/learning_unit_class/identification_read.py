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
from typing import List, Dict

from django.utils.functional import cached_property
from django.views.generic import TemplateView
from reversion.models import Version

from base.models.enums.component_type import LECTURING, PRACTICAL_EXERCISES, COMPONENT_TYPES, DEFAULT_ACRONYM_COMPONENT
from base.models.learning_unit_year import LearningUnitYear
from ddd.logic.learning_unit.commands import GetEffectiveClassWarningsCommand
from ddd.logic.learning_unit.domain.model._volumes_repartition import Volumes
from ddd.logic.learning_unit.domain.model.effective_class import EffectiveClass
from ddd.logic.learning_unit.domain.model.learning_unit import LearningUnit
from ddd.logic.shared_kernel.campus.commands import GetCampusCommand
from ddd.logic.shared_kernel.campus.domain.model.uclouvain_campus import UclouvainCampus, UclouvainCampusIdentity
from ddd.logic.shared_kernel.language.commands import GetLanguageCommand
from ddd.logic.shared_kernel.language.domain.model.language import Language
from infrastructure.messages_bus import message_bus_instance
from learning_unit.forms.classes.update import DeleteClassForm
from learning_unit.models.learning_class_year import LearningClassYear
from learning_unit.views.learning_unit_class.common import CommonClassView


class ClassIdentificationView(CommonClassView, TemplateView):
    template_name = "class/identification_tab.html"
    permission_required = 'learning_unit.view_learningclassyear'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                'learning_unit_year': self.learning_unit_year,
                'learning_unit': self.learning_unit,
                'effective_class': self.effective_class,
                'show_button': True,
                'class_type': get_class_type(self.learning_unit),
                'volumes': self.learning_unit.volumes,
                'history': get_related_history(self.learning_unit_year, self.effective_class),
                'language':
                    message_bus_instance.invoke(
                        GetLanguageCommand(code_iso=self.learning_unit.language_id.code_iso)
                    ),  # type: Language
                'teaching_place': get_teaching_place(self.effective_class.teaching_place),
                'form_delete': DeleteClassForm(effective_class=self.effective_class),
                'warnings': self.warnings,
                'learning_class_year': self.get_permission_object()
            }
        )
        context.update(self.common_url_tabs())
        return context

    @cached_property
    def warnings(self) -> List[str]:
        command = GetEffectiveClassWarningsCommand(
            class_code=self.class_code,
            learning_unit_code=self.learning_unit_code,
            learning_unit_year=self.year
        )
        return message_bus_instance.invoke(command)


def get_class_type(learning_unit: 'LearningUnit') -> Dict[str, str]:
    class_type = LECTURING
    if learning_unit.has_practical_volume() and not learning_unit.has_lecturing_volume():
        class_type = PRACTICAL_EXERCISES
    return {
        'type_title': dict(COMPONENT_TYPES).get(class_type),
        'acronym': DEFAULT_ACRONYM_COMPONENT[class_type]
    }


def get_related_history(
        learning_unit_year: LearningUnitYear,
        effective_class: 'EffectiveClass'
) -> List[Version]:
    # TODO :: Integration in DDD
    effective_class = LearningClassYear.objects.get(
        learning_component_year__learning_unit_year=learning_unit_year,
        acronym=effective_class.entity_id.class_code)
    versions = Version.objects.get_for_object(
        effective_class
    ).select_related('revision__user__person')

    related_models = [
        LearningClassYear,
    ]

    subversion = Version.objects.none()
    for model in related_models:
        subversion |= Version.objects.get_for_model(model).select_related('revision__user__person')

    versions |= subversion.filter(
        serialized_data__contains="\"learning_class_year\": {}".format(effective_class.pk)
    )

    return versions.order_by('-revision__date_created').distinct('revision__date_created')


def get_teaching_place(teaching_place: 'UclouvainCampusIdentity') -> 'UclouvainCampus':
    return message_bus_instance.invoke(
        GetCampusCommand(uuid=teaching_place.uuid)
    )  # type: UclouvainCampus
