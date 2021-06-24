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
from rest_framework import views
from rest_framework.response import Response

from attribution.api.serializers.vacant_course import VacantCourseFilterSerializer, VacantCourseGetSerializer
from base.models.enums.vacant_declaration_type import VacantDeclarationType
from ddd.logic.application.commands import SearchVacantCoursesCommand
from infrastructure.messages_bus import message_bus_instance


class VacantCourseListView(views.APIView):
    """
       Return vacant courses available filtered by criteria
    """
    name = 'vacantcourses_list'

    def get(self, request, *args, **kwargs):
        serializer = VacantCourseFilterSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        cmd = SearchVacantCoursesCommand(
            code=serializer.validated_data['code'],
            allocation_entity_code=serializer.validated_data['allocation_faculty'],
            vacant_declaration_types=[
                VacantDeclarationType.OPEN_FOR_EXTERNS.name, VacantDeclarationType.RESEVED_FOR_INTERNS.name
            ],
        )
        vacant_courses = message_bus_instance.invoke(cmd)

        serializer = VacantCourseGetSerializer(vacant_courses, many=True)
        # FIXME: Integrate pagination with command
        return Response({
            "count": len(serializer.data),
            "results": serializer.data,
            "next": None,
            "previous": None
        })
