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
from django.forms import formset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.functional import cached_property
from django.views.generic import FormView

from assessments.calendar.scores_exam_submission_calendar import ScoresExamSubmissionCalendar
from assessments.forms.score_encoding import ScoreEncodingForm
from ddd.logic.encodage_des_notes.soumission.commands import EncoderNoteCommand
from infrastructure.messages_bus import message_bus_instance
from osis_role.contrib.views import PermissionRequiredMixin


class LearningUnitScoreEncodingBaseFormView(PermissionRequiredMixin, FormView):
    # PermissionRequiredMixin
    permission_required = "assessments.can_access_scoreencoding"

    @cached_property
    def person(self):
        return self.request.user.person

    @cached_property
    def feuille_de_notes(self):
        raise NotImplementedError()

    def form_valid(self, formset):
        for form in formset:
            if form.has_changed():
                cmd = EncoderNoteCommand(
                    code_unite_enseignement=self.feuille_de_notes.code_unite_enseignement,
                    annee_unite_enseignement=self.feuille_de_notes.annee_academique,
                    numero_session=self.feuille_de_notes.numero_session,
                    matricule_fgs_enseignant=self.person.global_id,
                    noma_etudiant=form.cleaned_data['noma'],
                    email_etudiant=self.feuille_de_notes.get_email_for_noma(form.cleaned_data['noma']),
                    note=form.cleaned_data['note'],
                )

                message_bus_instance.invoke(cmd)

        redirect_url = reverse(
            'learning_unit_score_encoding',
            kwargs={'learning_unit_code': self.kwargs['learning_unit_code']}
        )
        return redirect(redirect_url)

    def dispatch(self, request, *args, **kwargs):
        opened_calendars = ScoresExamSubmissionCalendar().get_opened_academic_events()
        if not opened_calendars:
            redirect_url = reverse('outside_scores_encodings_period')
            return HttpResponseRedirect(redirect_url)
        return super().dispatch(request, *args, **kwargs)

    def get_form_class(self):
        return formset_factory(ScoreEncodingForm, extra=0)

    def get_initial(self):
        return [
            {
                'note': note_etudiant.note,
                'noma': note_etudiant.noma
            } for note_etudiant in self.feuille_de_notes.notes_etudiants
        ]

    def get_context_data(self, **kwargs):
        context = {
            **super().get_context_data(**kwargs),
            'feuille_de_notes': self.feuille_de_notes,
            'cancel_url': self.get_cancel_url()
        }
        return context

    def get_cancel_url(self):
        return reverse('learning_unit_score_encoding', kwargs={
            'learning_unit_code': self.kwargs['learning_unit_code']
        })

    def get_permission_object(self):
        return None
