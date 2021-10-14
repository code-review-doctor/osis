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

from django.db.models import F, Value, Case, When, CharField
from django.db.models.functions import Concat
from rest_framework import generics
from rest_framework.response import Response

from assessments.api.serializers.scores_responsible import ScoreResponsiblePersonListSerializer
from assessments.models.score_responsible import ScoreResponsible
from backoffice.settings.rest_framework.common_views import LanguageContextSerializerMixin
from base.models.enums.learning_component_year_type import LECTURING, PRACTICAL_EXERCISES


class ScoreResponsibleList(LanguageContextSerializerMixin, generics.ListAPIView):
    """
       Return a list of score responsibles for several learning units.
    """
    name = 'score_responsible_list'

    serializer_class = ScoreResponsiblePersonListSerializer

    def list(self, request, *args, **kwargs):
        codes_unites_enseignement = self.request.GET.getlist('learning_unit_codes')
        queryset = ScoreResponsible.objects.all().select_related('learning_unit_year', 'tutor') \
            .annotate(
            learning_unit_full_acronym=Case(
                When(
                    learning_class_year__learning_component_year__type=LECTURING,
                    then=Concat(
                        'learning_unit_year__acronym',
                        Value('-'),
                        'learning_class_year__acronym',
                        output_field=CharField()
                    )
                ),
                When(
                    learning_class_year__learning_component_year__type=PRACTICAL_EXERCISES,
                    then=Concat(
                        'learning_unit_year__acronym',
                        Value('_'),
                        'learning_class_year__acronym',
                        output_field=CharField()
                    )
                ),
                default=F('learning_unit_year__acronym'),
                output_field=CharField()
            ),
        ) \
            .annotate(full_name=Concat(F('tutor__person__last_name'), Value(' '), F('tutor__person__first_name'))) \
            .annotate(year=F('learning_unit_year__academic_year__year')) \
            .annotate(global_id=F('tutor__person__global_id')) \
            .filter(year=self.request.GET['year']) \
            .filter(learning_unit_year__acronym__in=codes_unites_enseignement)
        serializer = ScoreResponsiblePersonListSerializer(list(queryset), many=True)
        return Response(serializer.data)
