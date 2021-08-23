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

from assessments.forms.score_encoding import ScoreEncodingProgressFilterForm
from assessments.views.common.score_encoding_progress_overview import ScoreEncodingProgressOverviewBaseView
from base.models import synchronization
from ddd.logic.encodage_des_notes.soumission.commands import GetProgressionGeneraleCommand
from infrastructure.messages_bus import message_bus_instance


class ScoreEncodingProgressOverviewProgramManagerView(ScoreEncodingProgressOverviewBaseView):
    # TemplateView
    template_name = "assessments/program_manager/score_encoding_progress_overview.html"

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            'progression_generale': self.get_progression_generale(),
            'search_form': self.get_search_form(),
            'score_search_url': self.get_score_search_url(),
            'last_synchronization': self.get_last_synchronization()
        }

    def get_search_form(self):
        return ScoreEncodingProgressFilterForm(
            matricule_fgs_gestionnaire=self.person.global_id,
            data=self.request.GET or None
        )

    def get_progression_generale(self):
        # TODO: Change to command for program manager
        # cmd = GetProgressionGeneraleCommand(matricule_fgs_enseignant=self.person.global_id)
        # return message_bus_instance.invoke(cmd)
        return dict()

    def get_last_synchronization(self):
        return synchronization.find_last_synchronization_date()

    def get_score_search_url(self):
        return reverse('score_search')
