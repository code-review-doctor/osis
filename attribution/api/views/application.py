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
from django.utils.functional import cached_property
from rest_framework import status, views
from rest_framework.response import Response

from attribution.api.serializers.application import ApplicationGetSerializer, ApplicationPostSerializer, \
    ApplicationPutSerializer, AttributionsAboutToExpireGetSerializer, RenewAttributionAboutToExpirePostSerializer
from backoffice.settings.rest_framework.common_views import DisplayExceptionsByFieldNameAPIMixin
from base.models.person import Person
from ddd.logic.application.commands import SearchApplicationByApplicantCommand, ApplyOnVacantCourseCommand, \
    UpdateApplicationCommand, DeleteApplicationCommand, GetAttributionsAboutToExpireCommand, \
    RenewMultipleAttributionsCommand, SendApplicationsSummaryCommand, SearchVacantCoursesCommand
from ddd.logic.application.domain.validator.exceptions import VolumesAskedShouldBeLowerOrEqualToVolumeAvailable, \
    LecturingAndPracticalChargeNotFilledException
from infrastructure.messages_bus import message_bus_instance


class ApplicationListCreateView(DisplayExceptionsByFieldNameAPIMixin, views.APIView):
    """
        POST: Create an application on the current application period
        GET: Return all applications of connected user of the current application period
    """
    name = 'application_list_create'
    field_name_by_exception = {
        VolumesAskedShouldBeLowerOrEqualToVolumeAvailable: ['lecturing_volume', 'practical_volume'],
        LecturingAndPracticalChargeNotFilledException: ['lecturing_volume', 'practical_volume']
    }

    @cached_property
    def person(self) -> Person:
        return self.request.user.person

    def post(self, request, *args, **kwargs):
        serializer = ApplicationPostSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cmd = ApplyOnVacantCourseCommand(
            code=serializer.validated_data['code'],
            global_id=self.person.global_id,
            lecturing_volume=serializer.validated_data['lecturing_volume'],
            practical_volume=serializer.validated_data['practical_volume'],
            course_summary=serializer.validated_data['course_summary'],
            remark=serializer.validated_data['remark'],
        )
        message_bus_instance.invoke(cmd)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        cmd = SearchApplicationByApplicantCommand(global_id=self.person.global_id)
        applications = message_bus_instance.invoke(cmd)

        serializer = ApplicationGetSerializer(applications, many=True)
        return Response({
            "results": serializer.data,
            "count": len(serializer.data)
        })


class ApplicationUpdateDeleteView(DisplayExceptionsByFieldNameAPIMixin, views.APIView):
    """
        PUT:  Update an application on the current application period
        DELETE: Delete an application on the current application period
    """
    name = 'application_update_delete'
    field_name_by_exception = {
        VolumesAskedShouldBeLowerOrEqualToVolumeAvailable: ['lecturing_volume', 'practical_volume'],
        LecturingAndPracticalChargeNotFilledException: ['lecturing_volume', 'practical_volume']
    }

    @cached_property
    def person(self) -> Person:
        return self.request.user.person

    def put(self, request, *args, **kwargs):
        serializer = ApplicationPutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cmd = UpdateApplicationCommand(
            application_uuid=self.kwargs['application_uuid'],
            global_id=self.person.global_id,
            lecturing_volume=serializer.validated_data['lecturing_volume'],
            practical_volume=serializer.validated_data['practical_volume'],
            course_summary=serializer.validated_data['course_summary'],
            remark=serializer.validated_data['remark']
        )
        message_bus_instance.invoke(cmd)
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        cmd = DeleteApplicationCommand(
            application_uuid=self.kwargs['application_uuid'],
            global_id=self.person.global_id,
        )
        message_bus_instance.invoke(cmd)
        return Response(status=status.HTTP_204_NO_CONTENT)


class RenewAttributionsAboutToExpire(views.APIView):
    """
        GET:   Get all attributions about to expire during current application period
        POST:  Renew multiple attributions about to expire application during current application period
    """
    name = 'renew_attributions_about_to_expire'

    @cached_property
    def person(self) -> Person:
        return self.request.user.person

    def post(self, request, *args, **kwargs):
        serializer = RenewAttributionAboutToExpirePostSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cmd = RenewMultipleAttributionsCommand(
            global_id=self.person.global_id,
            renew_codes=serializer.validated_data['codes']
        )
        message_bus_instance.invoke(cmd)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        cmd = GetAttributionsAboutToExpireCommand(global_id=self.person.global_id)
        attribution_about_to_expires = message_bus_instance.invoke(cmd)

        serializer = AttributionsAboutToExpireGetSerializer(attribution_about_to_expires, many=True)
        return Response({
            "count": len(serializer.data),
            "results": serializer.data
        })


class SendApplicationsSummary(views.APIView):
    """
        POST:  Send applications summary
    """
    name = 'send_applications_summary'

    @cached_property
    def person(self) -> Person:
        return self.request.user.person

    def post(self, request, *args, **kwargs):
        cmd = SendApplicationsSummaryCommand(global_id=self.person.global_id)
        message_bus_instance.invoke(cmd)
        return Response(status=status.HTTP_204_NO_CONTENT)
