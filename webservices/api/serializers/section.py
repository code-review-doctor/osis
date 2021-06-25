##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2018 Université catholique de Louvain (http://www.uclouvain.be)
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
from rest_framework import serializers

from base.models.admission_condition import AdmissionCondition
from base.models.enums.education_group_types import TrainingType
from webservices.api.serializers.access_requirements import AccessRequirementsSerializer, \
    BachelorAccessRequirementsSerializer, SpecializedMasterAccessRequirementsSerializer, \
    AggregationAccessRequirementsSerializer, MasterAccessRequirementsSerializer, \
    ContinuingEducationTrainingAccessRequirementsSerializer
from webservices.api.serializers.achievement import AchievementsSerializer
from webservices.api.serializers.contacts import ContactsSerializer


class SectionSerializer(serializers.Serializer):
    id = serializers.CharField(source='label', read_only=True)
    label = serializers.CharField(source='translated_label', read_only=True)
    content = serializers.CharField(source='text', read_only=True, allow_null=True)


class AchievementSectionSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    label = serializers.CharField(source='id', read_only=True)
    content = serializers.SerializerMethodField()

    def get_content(self, obj):
        node = self.context.get('root_node')
        return AchievementsSerializer(node, context=self.context).data


class AccessRequirementsSectionSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    label = serializers.CharField(source='id', read_only=True)
    content = serializers.SerializerMethodField()

    def get_content(self, obj):
        # FIXME: Bachelor has no admissioncondition
        access_requirements_serializers = {
            TrainingType.BACHELOR.name: BachelorAccessRequirementsSerializer,
            TrainingType.MASTER_MC.name: SpecializedMasterAccessRequirementsSerializer,
            TrainingType.AGGREGATION.name: AggregationAccessRequirementsSerializer,
            TrainingType.PGRM_MASTER_120.name: MasterAccessRequirementsSerializer,
            TrainingType.PGRM_MASTER_180_240.name: MasterAccessRequirementsSerializer,
            TrainingType.MASTER_M1.name: MasterAccessRequirementsSerializer,
            TrainingType.CERTIFICATE_OF_PARTICIPATION.name: ContinuingEducationTrainingAccessRequirementsSerializer,
            TrainingType.CERTIFICATE_OF_SUCCESS.name: ContinuingEducationTrainingAccessRequirementsSerializer,
            TrainingType.CERTIFICATE_OF_HOLDING_CREDITS.name: ContinuingEducationTrainingAccessRequirementsSerializer,
            TrainingType.UNIVERSITY_FIRST_CYCLE_CERTIFICATE.name:
                ContinuingEducationTrainingAccessRequirementsSerializer,
            TrainingType.UNIVERSITY_SECOND_CYCLE_CERTIFICATE.name:
                ContinuingEducationTrainingAccessRequirementsSerializer,
        }
        root_node = self.context.get('root_node')
        serializer = access_requirements_serializers.get(
            root_node.node_type.name,
            AccessRequirementsSerializer,
        )
        return serializer(self.get_admission_condition(), context=self.context).data

    def get_admission_condition(self):
        offer = self.context.get('offer')
        try:
            return AdmissionCondition.objects.get(education_group_year_id=offer.id)
        except AdmissionCondition.DoesNotExist:
            return AdmissionCondition.objects.create(education_group_year_id=offer.id)


class ContactsSectionSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    label = serializers.CharField(source='id', read_only=True)
    content = serializers.SerializerMethodField()

    def get_content(self, obj):
        root_node = self.context.get('root_node')
        return ContactsSerializer(root_node, context=self.context).data
