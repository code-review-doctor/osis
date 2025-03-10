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
import datetime
from typing import Tuple, List, Optional

from dal import autocomplete
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import CharField, Value, When, Case
from django.db.models.functions import Concat
from django.http import JsonResponse
from django.urls import reverse
from django.utils.functional import cached_property

from assessments.forms.score_encoding import ScoreEncodingProgressFilterForm
from assessments.views.common.score_encoding_progress_overview import ScoreEncodingProgressOverviewBaseView
from base.models import synchronization
from base.models.enums.learning_component_year_type import PRACTICAL_EXERCISES
from base.models.learning_unit_year import LearningUnitYear
from base.models.person import Person
from ddd.logic.encodage_des_notes.encodage.commands import GetProgressionGeneraleGestionnaireCommand, \
    GetPeriodeEncodageCommand, SearchEnseignantsCommand, GetCohortesGestionnaireCommand
from ddd.logic.encodage_des_notes.shared_kernel.dtos import ProgressionGeneraleEncodageNotesDTO, PeriodeEncodageNotesDTO
from infrastructure.messages_bus import message_bus_instance
from learning_unit.models.learning_class_year import LearningClassYear


class ScoreEncodingProgressOverviewProgramManagerView(ScoreEncodingProgressOverviewBaseView):
    # TemplateView
    template_name = "assessments/program_manager/score_encoding_progress_overview.html"

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            'progression_generale': self.progression_generale,
            'periode_encodage': self.periode_encodage,
            'search_form': self.get_search_form,
            'score_search_url': self.get_score_search_url(),
            'last_synchronization': self.get_last_synchronization(),
            'learning_unit_count': self.get_learning_unit_count(),
            'cohorte_count': self.get_cohorte_count()
        }

    @cached_property
    def get_search_form(self) -> 'ScoreEncodingProgressFilterForm':
        return ScoreEncodingProgressFilterForm(
            matricule_fgs_gestionnaire=self.person.global_id,
            data=self.request.GET or None
        )

    @cached_property
    def periode_encodage(self) -> 'PeriodeEncodageNotesDTO':
        cmd = GetPeriodeEncodageCommand()
        return message_bus_instance.invoke(cmd)

    @cached_property
    def progression_generale(self) -> Optional['ProgressionGeneraleEncodageNotesDTO']:
        search_form = self.get_search_form
        if search_form.is_bound:
            cmd_kwargs = {'matricule_fgs_gestionnaire': self.person.global_id}
            if search_form.is_valid():
                cmd_kwargs.update({
                    'noms_cohortes': search_form.cleaned_data['cohorte_name'],
                    'code_unite_enseignement': search_form.cleaned_data['learning_unit_code'],
                    'enseignant': search_form.cleaned_data['tutor'],
                    'seulement_notes_manquantes': search_form.cleaned_data['incomplete_encodings_only'],
                })
            cmd = GetProgressionGeneraleGestionnaireCommand(**cmd_kwargs)
            return message_bus_instance.invoke(cmd)
        return None

    @staticmethod
    def get_last_synchronization() -> datetime.date:
        return synchronization.find_last_synchronization_date()

    def get_learning_unit_count(self) -> Optional[int]:
        return len(self.progression_generale.progression_generale) if self.progression_generale else None

    def get_cohorte_count(self) -> int:
        search_form = self.get_search_form
        if search_form.is_valid() and search_form.cleaned_data['cohorte_name']:
            return len(search_form.cleaned_data['cohorte_name'])
        return len(search_form.fields['cohorte_name'].choices) - 1

    @staticmethod
    def get_score_search_url() -> str:
        return reverse('score_search')


class CodeUniteEnseignementAutocomplete(LoginRequiredMixin, autocomplete.Select2ListView):
    def get_list(self) -> List[str]:
        recherche = self.q
        minimum_chars_to_search = 2
        if recherche and len(recherche) > minimum_chars_to_search:
            filtre_sur_ue, has_filtre_sur_classe = self.__separer_filtre_ue_et_classe(recherche)
            periode_encodage = message_bus_instance.invoke(GetPeriodeEncodageCommand())
            qs = LearningUnitYear.objects.filter(
                academic_year__year=periode_encodage.annee_concernee,
                acronym__icontains=filtre_sur_ue,
            ).values_list(
                'pk',
                'acronym',
            )
            codes_classes = LearningClassYear.objects.filter(
                learning_component_year__learning_unit_year_id__in={pk for pk, ___ in qs},
            ).annotate(
                code_classe=Case(
                    When(
                        learning_component_year__type=PRACTICAL_EXERCISES,
                        then=Concat(
                            'learning_component_year__learning_unit_year__acronym',
                            Value('_'),
                            'acronym',
                            output_field=CharField()
                        )
                    ),
                    default=Concat(
                        'learning_component_year__learning_unit_year__acronym',
                        Value('-'),
                        'acronym',
                        output_field=CharField()
                    ),
                    output_field=CharField(),
                )
            ).values_list('code_classe', flat=True)

            codes_ues_et_classes_trouves = {code_ue for __, code_ue in qs} | set(codes_classes)
            if has_filtre_sur_classe:
                codes_ues_et_classes_trouves = {
                    code for code in codes_ues_et_classes_trouves if recherche.upper() in code
                }
            if codes_ues_et_classes_trouves:
                if recherche.upper() not in codes_ues_et_classes_trouves:
                    return [recherche] + list(sorted(codes_ues_et_classes_trouves))
                return list(sorted(codes_ues_et_classes_trouves))
            return []

        else:
            return [recherche]

    @staticmethod
    def __separer_filtre_ue_et_classe(recherche: str) -> Tuple[str, bool]:
        filtre_sur_ue = recherche
        has_filtre_sur_classe = False
        if '-' in filtre_sur_ue:
            index = filtre_sur_ue.index('-')
            has_filtre_sur_classe = True
            filtre_sur_ue = filtre_sur_ue[:index]
        elif '_' in filtre_sur_ue:
            index = filtre_sur_ue.index('_')
            has_filtre_sur_classe = True
            filtre_sur_ue = filtre_sur_ue[:index]
        return filtre_sur_ue, has_filtre_sur_classe


class EnseignantAutocomplete(LoginRequiredMixin, autocomplete.Select2ListView):
    def get_list(self) -> List[str]:
        recherche = self.q
        minimum_chars_to_search = 2
        if recherche and len(recherche) > minimum_chars_to_search:
            enseignants = message_bus_instance.invoke(SearchEnseignantsCommand(recherche))
            return [recherche] + ['{} {}'.format(enseignant.nom, enseignant.prenom) for enseignant in enseignants]
        return [recherche]


class FormationAutocomplete(LoginRequiredMixin, autocomplete.Select2ListView):
    def get(self, request, *args, **kwargs):
        matricule_fgs_gestionnaire = Person.objects.filter(
            user=self.request.user
        ).values_list('global_id', flat=True)[0]
        cmd = GetCohortesGestionnaireCommand(matricule_fgs_gestionnaire=matricule_fgs_gestionnaire)
        results = message_bus_instance.invoke(cmd)
        choices = (
            (cohorte.nom_cohorte, cohorte.nom_cohorte,) for cohorte in results
        )
        if self.q:
            choices = filter(lambda cohorte_tuple: self.q.upper() in cohorte_tuple[1], choices)

        results = [{'id': id, 'text': value, 'title': ' '} for id, value in sorted(choices, key=lambda x: x[1])]
        return JsonResponse({'results': results})
