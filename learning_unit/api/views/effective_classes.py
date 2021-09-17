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
from types import SimpleNamespace
from typing import List

from django.utils.functional import cached_property
from rest_framework import generics
from rest_framework.response import Response

from backoffice.settings.rest_framework.common_views import LanguageContextSerializerMixin
from ddd.logic.learning_unit.commands import GetClassesEffectivesDepuisUniteDEnseignementCommand
from ddd.logic.learning_unit.dtos import EffectiveClassDTO
from ddd.logic.shared_kernel.campus.commands import GetCampusCommand
from ddd.logic.shared_kernel.campus.domain.model.uclouvain_campus import UclouvainCampus
from infrastructure.messages_bus import message_bus_instance
from learning_unit.api.serializers.effective_class import EffectiveClassSerializer


class EffectiveClassesList(LanguageContextSerializerMixin, generics.ListAPIView):
    """
       Return a list of all the classes of a specific learning unit.
    """
    name = 'classes_list'

    def list(self, request, *args, **kwargs):
        serializer = EffectiveClassSerializer(
            self.classes,
            many=True,
            context=self.get_serializer_context()
        )
        return Response(serializer.data)

    @cached_property
    def classes(self) -> List[SimpleNamespace]:
        classes = message_bus_instance.invoke(
            GetClassesEffectivesDepuisUniteDEnseignementCommand(
                learning_unit_code=self.kwargs['acronym'].upper(),
                learning_unit_year=self.kwargs['year']
            )
        )  # type: List[EffectiveClassDTO]
        return self._add_campus_info_to_classes(classes)

    def _add_campus_info_to_classes(self, classes: List['EffectiveClassDTO']) -> List[SimpleNamespace]:
        to_return = []
        for effective_class in classes:
            campus = self._get_campus(effective_class)
            to_return.append(
                SimpleNamespace(
                    class_code=effective_class.class_code,
                    title_fr=effective_class.title_fr,
                    title_en=effective_class.title_en,
                    teaching_place_uuid=effective_class.teaching_place_uuid,
                    derogation_quadrimester=effective_class.derogation_quadrimester,
                    session_derogation=effective_class.session_derogation,
                    volume_q1=effective_class.volume_q1,
                    volume_q2=effective_class.volume_q2,
                    class_type=effective_class.class_type,
                    campus_name=campus.name,
                    organization_name=campus.organization_name
                )
            )
        return to_return

    @staticmethod
    def _get_campus(effective_class: 'EffectiveClassDTO') -> 'UclouvainCampus':
        return message_bus_instance.invoke(
            GetCampusCommand(effective_class.teaching_place_uuid)
        )
