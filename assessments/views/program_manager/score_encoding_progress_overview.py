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
from django.urls import reverse
from django.utils.functional import cached_property

from assessments.forms.score_encoding import ScoreEncodingProgressFilterForm
from assessments.views.common.score_encoding_progress_overview import ScoreEncodingProgressOverviewBaseView
from base.models import synchronization
from ddd.logic.encodage_des_notes.encodage.commands import GetProgressionGeneraleGestionnaireCommand, \
    GetPeriodeEncodageCommand
from infrastructure.messages_bus import message_bus_instance


class ScoreEncodingProgressOverviewProgramManagerView(ScoreEncodingProgressOverviewBaseView):
    # TemplateView
    template_name = "assessments/program_manager/score_encoding_progress_overview.html"

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            'progression_generale': self.progression_generale,
            'periode_encodage': self.periode_encodage,
            'search_form': self.get_search_form(),
            'score_search_url': self.get_score_search_url(),
            'last_synchronization': self.get_last_synchronization(),
            'learning_unit_count': self.get_learning_unit_count(),
            'cohorte_count': self.get_cohorte_count()
        }

    def get_search_form(self):
        return ScoreEncodingProgressFilterForm(
            matricule_fgs_gestionnaire=self.person.global_id,
            data=self.request.GET or None
        )

    @cached_property
    def periode_encodage(self):
        cmd = GetPeriodeEncodageCommand()
        return message_bus_instance.invoke(cmd)

    @cached_property
    def progression_generale(self):
        search_form = self.get_search_form()
        if search_form.is_bound:
            cmd_kwargs = {'matricule_fgs_gestionnaire': self.person.global_id}
            if search_form.is_valid():
                cmd_kwargs.update({
                    'nom_cohorte': search_form.cleaned_data['cohorte_name'],
                    'code_unite_enseignement': search_form.cleaned_data['learning_unit_code'],
                    'seulement_notes_manquantes': search_form.cleaned_data['incomplete_encodings_only'],
                })
            cmd = GetProgressionGeneraleGestionnaireCommand(**cmd_kwargs)
            return message_bus_instance.invoke(cmd)
        return None

    def get_last_synchronization(self):
        return synchronization.find_last_synchronization_date()

    def get_learning_unit_count(self):
        return len(self.progression_generale.progression_generale) if self.progression_generale else None

    def get_cohorte_count(self):
        search_form = self.get_search_form()
        if search_form.is_valid() and search_form.cleaned_data['cohorte_name']:
            return 1
        return len(search_form.fields['cohorte_name'].choices) - 1

    def get_score_search_url(self):
        return reverse('score_search')
