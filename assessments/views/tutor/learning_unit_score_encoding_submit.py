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
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.functional import cached_property
from django.views.generic import TemplateView

from assessments.calendar.scores_exam_submission_calendar import ScoresExamSubmissionCalendar
from base.views.mixins import AjaxTemplateMixin
from ddd.logic.encodage_des_notes.soumission.commands import GetFeuilleDeNotesCommand, SoumettreNoteCommand, \
    SoumettreNotesCommand
from infrastructure.messages_bus import message_bus_instance
from osis_role.contrib.views import AjaxPermissionRequiredMixin


class LearningUnitScoreEncodingTutorSubmitView(AjaxPermissionRequiredMixin, AjaxTemplateMixin, TemplateView):
    # PermissionRequiredMixin
    permission_required = "assessments.can_access_scoreencoding"

    # FormView
    template_name = "assessments/tutor/learning_unit_score_encoding_submit_inner.html"

    @cached_property
    def person(self):
        return self.request.user.person

    def dispatch(self, request, *args, **kwargs):
        opened_calendars = ScoresExamSubmissionCalendar().get_opened_academic_events()
        if not opened_calendars:
            redirect_url = reverse('outside_scores_encodings_period')
            return HttpResponseRedirect(redirect_url)
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        cmd = SoumettreNotesCommand(
            matricule_fgs_enseignant=self.person.global_id,
            code_unite_enseignement=self.feuille_de_notes.code_unite_enseignement,
            annee_unite_enseignement=self.feuille_de_notes.annee_academique,
            numero_session=self.feuille_de_notes.numero_session,
            notes=[
                SoumettreNoteCommand(noma_etudiant=note.noma)
                for note in self.feuille_de_notes.get_notes_en_attente_de_soumission()
            ]
        )
        message_bus_instance.invoke(cmd)
        return self._ajax_response()

    def get_success_url(self):
        return reverse(
            'learning_unit_score_encoding',
            kwargs={'learning_unit_code': self.kwargs['learning_unit_code']}
        )

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            'draft_scores_not_submitted': self.feuille_de_notes.quantite_notes_en_attente_de_soumission,
        }

    @cached_property
    def feuille_de_notes(self):
        cmd = GetFeuilleDeNotesCommand(
            matricule_fgs_enseignant=self.person.global_id,
            code_unite_enseignement=self.kwargs['learning_unit_code'].upper()
        )
        return message_bus_instance.invoke(cmd)
