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
from django.conf import settings
from rest_framework import serializers

from base.models.admission_condition import AdmissionCondition
from webservices.api.serializers.access_requirements_line import AccessRequirementsTextsSerializer, \
    AccessRequirementsLineSerializer
from webservices.api.serializers.utils import DynamicLanguageFieldsModelSerializer
from webservices.business import ACCESS_REQUIREMENTS_FIELDS, ACCESS_REQUIREMENTS_LINE_FIELDS


class AccessRequirementsSerializer(DynamicLanguageFieldsModelSerializer):
    free_text = serializers.CharField(read_only=True, required=False)
    alert_message = serializers.CharField(read_only=True)

    def __init__(self, *args, **kwargs):
        super(AccessRequirementsSerializer, self).__init__(*args, **kwargs)
        if not self.instance.common_admission_condition:
            self.fields.pop('alert_message')

    class Meta:
        model = AdmissionCondition

        fields = (
            'free_text',
            'alert_message',
        )


class BachelorAccessRequirementsSerializer(AccessRequirementsSerializer):
    ca_bacs_cond_generales = serializers.CharField(read_only=True)
    ca_bacs_cond_particulieres = serializers.CharField(read_only=True)
    ca_bacs_examen_langue = serializers.CharField(read_only=True)
    ca_bacs_cond_speciales = serializers.CharField(read_only=True)

    class Meta:
        model = AdmissionCondition

        fields = (
            'alert_message',
            'ca_bacs_cond_generales',
            'ca_bacs_cond_particulieres',
            'ca_bacs_examen_langue',
            'ca_bacs_cond_speciales'
        )


class SpecializedMasterAccessRequirementsSerializer(AccessRequirementsSerializer):
    ca_cond_generales = serializers.CharField(read_only=True)

    class Meta:
        model = AdmissionCondition

        fields = (
            'free_text',
            'alert_message',
            'ca_cond_generales',
        )


class AggregationAccessRequirementsSerializer(SpecializedMasterAccessRequirementsSerializer):
    ca_maitrise_fr = serializers.CharField(read_only=True)
    ca_allegement = serializers.CharField(read_only=True)
    ca_ouv_adultes = serializers.CharField(read_only=True)
    admission_enrollment_procedures = serializers.CharField(read_only=True)

    class Meta:
        model = AdmissionCondition

        fields = (
            'free_text',
            'alert_message',
            'ca_cond_generales',
            'ca_maitrise_fr',
            'ca_allegement',
            'ca_ouv_adultes',
            'admission_enrollment_procedures'
        )


class MasterAccessRequirementsSerializer(AccessRequirementsSerializer):
    sections = serializers.SerializerMethodField()

    class Meta:
        model = AdmissionCondition

        fields = (
            'free_text',
            'alert_message',
            'sections',
        )

    def get_sections(self, obj):
        sections = {
            field: AccessRequirementsTextsSerializer(
                obj,
                context={**self.context, 'section': field}
            ).data
            for field in ACCESS_REQUIREMENTS_FIELDS
        }
        sections_line = {
            field: {
                'text': self._get_appropriate_text(field, obj),
                'records': {
                    diploma_type: AccessRequirementsLineSerializer(
                        obj.admissionconditionline_set.filter(section=diploma_type),
                        many=True,
                        context=self.context
                    ).data
                    for diploma_type in diploma_types
                }
            } for field, diploma_types in ACCESS_REQUIREMENTS_LINE_FIELDS
        }
        sections.update(sections_line)
        return sections

    def _get_appropriate_text(self, field, ac):
        language = self.context.get('language')
        lang = '' if language == settings.LANGUAGE_CODE_FR else '_' + language
        text = getattr(ac, 'text_' + field + lang)
        return text if text else None


class ContinuingEducationTrainingAccessRequirementsSerializer(AccessRequirementsSerializer):
    class Meta:
        model = AdmissionCondition

        fields = (
            'alert_message',
            'free_text',
        )
