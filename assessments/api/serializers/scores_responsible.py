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
from django.urls import reverse
from rest_framework import serializers


class ScoresResponsibleListSerializer(serializers.Serializer):
    pk = serializers.IntegerField()
    acronym = serializers.CharField()
    learning_unit_title = serializers.CharField(source='full_title')
    requirement_entity = serializers.CharField()
    attributions = serializers.SerializerMethodField()
    select_url = serializers.SerializerMethodField()

    def get_attributions(self, obj):
        try:
            score_responsible = list(obj.scoreresponsible_set.all())[0].tutor
        except IndexError:
            score_responsible = None

        tutors = {
            attribution_charge.attribution.tutor
            for component in obj.learningcomponentyear_set.all()
            for attribution_charge in component.attributionchargenew_set.all()
        }

        result = [{"tutor": str(tutor), "score_responsible": tutor == score_responsible} for tutor in tutors]
        return sorted(result, key=lambda item: (not item["score_responsible"], item["tutor"]))

    def get_select_url(self, obj):
        return reverse(
            "score_responsible_select",
            kwargs={'code': obj.acronym}
        )