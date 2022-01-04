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
from typing import List, Dict

import attr
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView
from django_filters.views import FilterView

from assessments.api.serializers.scores_responsible import ScoresResponsibleListSerializer
from assessments.forms.scores_responsible import ScoresResponsiblesFilter
from assessments.views.score_encoding.outside_period import get_latest_closest_session_information_message
from base.models import session_exam_calendar
from base.models.academic_year import AcademicYear
from base.models.learning_unit_year import LearningUnitYear
from base.models.person import Person
from base.utils.cache import CacheFilterMixin
from base.views.common import display_success_messages
from ddd.logic.effective_class_repartition.commands import SearchAttributionsToLearningUnitCommand, \
    SearchTutorsDistributedToClassCommand
from ddd.logic.effective_class_repartition.dtos import TutorAttributionToLearningUnitDTO
from ddd.logic.effective_class_repartition.dtos import TutorClassRepartitionDTO
from ddd.logic.encodage_des_notes.soumission.commands import AssignerResponsableDeNotesCommand, \
    GetResponsableDeNotesCommand, SearchResponsableDeNotesCommand
from ddd.logic.encodage_des_notes.soumission.dtos import ResponsableDeNotesDTO
from infrastructure.messages_bus import message_bus_instance
from learning_unit.models.learning_class_year import LearningClassYear


@attr.s(frozen=True, slots=True, auto_attribs=True)
class AttributionDTO:
    code: str
    matricule_fgs: str
    enseignant: str
    statut: str
    responsable_de_notes: bool


class ScoresResponsiblesSearch(LoginRequiredMixin, CacheFilterMixin, FilterView):
    model = LearningUnitYear
    paginate_by = 20
    template_name = "assessments/score_responsible/score_responsibles.html"

    filterset_class = ScoresResponsiblesFilter

    def get_filterset_kwargs(self, filterset_class):
        return {
            **super().get_filterset_kwargs(filterset_class),
            'academic_year': session_exam_calendar.current_sessions_academic_year()
        }

    def render_to_response(self, context, **response_kwargs):
        messages = get_latest_closest_session_information_message()
        context.update({"session_messages": messages})

        if self.request.is_ajax():
            serializer = ScoresResponsibleListSerializer(context['object_list'], many=True)
            return JsonResponse({'object_list': serializer.data})
        return super().render_to_response(context, **response_kwargs)


class SelectScoreResponsible(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = "assessments/score_responsible/select_score_responsible.html"

    permission_required = 'assessments.change_scoresresponsible'

    @cached_property
    def code_unite_enseignement(self) -> str:
        return self.kwargs['code']

    @cached_property
    def academic_year(self) -> 'AcademicYear':
        return session_exam_calendar.current_sessions_academic_year()

    @cached_property
    def responsables_notes(self) -> List['ResponsableDeNotesDTO']:
        codes_complets_classes = {repartition.complete_class_code for repartition in self.repartitions_classes}
        codes = list(codes_complets_classes) + [self.code_unite_enseignement]
        cmd_resp_notes = SearchResponsableDeNotesCommand(
            unites_enseignement=[GetResponsableDeNotesCommand(code, self.academic_year.year) for code in codes]
        )
        return message_bus_instance.invoke(cmd_resp_notes)

    @cached_property
    def attributions_unites_enseignement(self) -> List['TutorAttributionToLearningUnitDTO']:
        cmd_resp_notes = SearchAttributionsToLearningUnitCommand(
            learning_unit_code=self.code_unite_enseignement,
            learning_unit_year=self.academic_year.year,
        )
        return message_bus_instance.invoke(cmd_resp_notes)

    @cached_property
    def repartitions_classes(self) -> List['TutorClassRepartitionDTO']:
        codes_classes_de_unite_enseignement = LearningClassYear.objects.filter(
            learning_component_year__learning_unit_year__acronym=self.code_unite_enseignement,
            learning_component_year__learning_unit_year__academic_year=self.academic_year,
        ).values_list('acronym', flat=True)
        repartitions_classes = []
        for code_classe in codes_classes_de_unite_enseignement:
            cmd_resp_notes = SearchTutorsDistributedToClassCommand(
                class_code=code_classe,
                learning_unit_code=self.code_unite_enseignement,
                learning_unit_year=self.academic_year.year,
            )
            repartitions_classes += message_bus_instance.invoke(cmd_resp_notes)
        return repartitions_classes

    def est_responsable_de_notes_classe(self, repartition: 'TutorClassRepartitionDTO') -> bool:
        return any(
            resp for resp in self.responsables_notes
            if resp.matricule == repartition.personal_id_number
            and resp.code_unite_enseignement == repartition.complete_class_code
        )

    def est_responsable_de_notes_unite_enseignement(self, attribution: 'TutorAttributionToLearningUnitDTO') -> bool:
        return any(
            resp for resp in self.responsables_notes
            if resp.matricule == attribution.personal_id_number
            and resp.code_unite_enseignement == attribution.learning_unit_code
        )

    def get_attributions(self) -> List['AttributionDTO']:
        return [
            AttributionDTO(
                code=self.code_unite_enseignement,
                matricule_fgs=attrib.personal_id_number,
                enseignant=Person.get_str(attrib.first_name, attrib.last_name),
                statut=attrib.function_text,
                responsable_de_notes=bool(self.est_responsable_de_notes_unite_enseignement(attrib)),
            )
            for attrib in self.attributions_unites_enseignement
        ]

    @cached_property
    def get_repartitions_classes_par_code(self) -> Dict[str, List['AttributionDTO']]:
        repartition_classes_par_code = dict()
        for repartition in self.repartitions_classes:
            attribution_dto = AttributionDTO(
                code=repartition.complete_class_code,
                matricule_fgs=repartition.personal_id_number,
                enseignant=Person.get_str(repartition.first_name, repartition.last_name),
                statut=repartition.function_text,
                responsable_de_notes=self.est_responsable_de_notes_classe(repartition)
            )
            repartition_classes_par_code.setdefault(repartition.complete_class_code, []).append(attribution_dto)

        return repartition_classes_par_code

    def post(self, request, *args, **kwargs):
        matricule_fgs = self.request.POST.get('matricule_fgs')
        if matricule_fgs:
            cmd = AssignerResponsableDeNotesCommand(
                code_unite_enseignement=self.code_unite_enseignement,
                annee_unite_enseignement=self.academic_year.year,
                matricule_fgs_enseignant=matricule_fgs
            )

            message_bus_instance.invoke(cmd)
            display_success_messages(request, self.get_success_msg(self.code_unite_enseignement))

        for code_complet_classe in self.get_repartitions_classes_par_code:
            matricule_fgs_classe = self.request.POST.get('matricule_fgs_' + code_complet_classe)
            if matricule_fgs_classe:
                cmd = AssignerResponsableDeNotesCommand(
                    code_unite_enseignement=code_complet_classe,
                    annee_unite_enseignement=self.academic_year.year,
                    matricule_fgs_enseignant=matricule_fgs_classe
                )
                message_bus_instance.invoke(cmd)
                display_success_messages(request, self.get_success_msg(code_complet_classe))

        return redirect(reverse('scores_responsibles_search'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['attributions'] = self.get_attributions()
        context['repartitions_classes'] = self.get_repartitions_classes_par_code
        context['code'] = self.code_unite_enseignement
        context['annee_academique'] = str(self.academic_year)

        return context

    def get_success_msg(self, code: str) -> str:
        return _("Score responsible successfully designated on %(code)s.") % {
            "code": code,
        }
