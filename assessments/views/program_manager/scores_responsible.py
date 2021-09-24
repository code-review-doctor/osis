##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)
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
import attr
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.db.models import Exists, OuterRef
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.functional import cached_property
from django.views.generic import TemplateView
from django_filters.views import FilterView

from assessments.api.serializers.scores_responsible import BisScoresResponsibleListSerializer
from assessments.forms.scores_responsible import ScoresResponsiblesFilter
from assessments.models.score_responsible import ScoreResponsible
from attribution.models.attribution_new import AttributionNew
from base.models import session_exam_calendar
from base.models.academic_year import AcademicYear
from base.models.learning_unit_year import LearningUnitYear
from base.utils.cache import CacheFilterMixin
from ddd.logic.encodage_des_notes.soumission.commands import AssignerResponsableDeNotesCommand
from infrastructure.messages_bus import message_bus_instance


@attr.s(frozen=True, slots=True)
class AttributionDTO:
    matricule_fgs = attr.ib(type=str)
    enseignant = attr.ib(type=str)
    statut = attr.ib(type=str)
    responsable_de_notes = attr.ib(type=bool)


class ScoresResponsibles(LoginRequiredMixin, PermissionRequiredMixin, CacheFilterMixin, FilterView):
    model = LearningUnitYear
    paginate_by = 20
    template_name = "assessments/score_responsible/score_responsibles.html"

    filterset_class = ScoresResponsiblesFilter
    permission_required = 'assessments.view_scoresresponsible'

    def get_filterset_kwargs(self, filterset_class):
        return {
            **super().get_filterset_kwargs(filterset_class),
            'academic_year': session_exam_calendar.current_sessions_academic_year()
        }

    def render_to_response(self, context, **response_kwargs):
        if self.request.is_ajax():
            serializer = BisScoresResponsibleListSerializer(context['object_list'], many=True)
            return JsonResponse({'object_list': serializer.data})
        return super().render_to_response(context, **response_kwargs)


class SelectScoreResponsible(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = "assessments/score_responsible/select_score_responsible.html"

    permission_required = 'assessments.change_scoresresponsible'

    @cached_property
    def code(self) -> str:
        return self.kwargs['code']

    @cached_property
    def academic_year(self) -> 'AcademicYear':
        return session_exam_calendar.current_sessions_academic_year()

    def get_attributions(self):
        qs = AttributionNew.objects.filter(
            attributionchargenew__learning_component_year__learning_unit_year__acronym=self.code,
            attributionchargenew__learning_component_year__learning_unit_year__academic_year=self.academic_year,
        ).annotate(
            est_responsable_de_notes=Exists(
                ScoreResponsible.objects.filter(
                    learning_unit_year__acronym=self.code,
                    learning_unit_year__academic_year=self.academic_year,
                    tutor=OuterRef('tutor')
                )
            )
        ).order_by(
            "tutor__person__last_name",
            "tutor__person__first_name",
        ).distinct(
            "tutor__person__last_name",
            "tutor__person__first_name",
        )

        return [
            AttributionDTO(
                matricule_fgs=attribution_new.tutor.person.global_id,
                enseignant=str(attribution_new.tutor),
                statut=attribution_new.get_function_display(),
                responsable_de_notes=attribution_new.est_responsable_de_notes
            )
            for attribution_new in qs
        ]

    def post(self, *args, **kwargs):
        matricule_fgs = self.request.POST.get('matricule_fgs')

        cmd = AssignerResponsableDeNotesCommand(
            code_unite_enseignement=self.code,
            annee_unite_enseignement=self.academic_year.year,
            matricule_fgs_enseignant=matricule_fgs
        )

        message_bus_instance.invoke(cmd)

        return redirect(reverse('scores_responsibles_search'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['attributions'] = self.get_attributions()
        context['code'] = self.code
        context['annee_academique'] = str(self.academic_year)

        return context
