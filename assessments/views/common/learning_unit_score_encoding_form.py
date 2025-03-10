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
import contextlib
import datetime
from typing import Optional

from django.forms import formset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.template.defaultfilters import floatformat
from django.urls import reverse
from django.utils.functional import cached_property
from django.views.generic import FormView

from assessments.calendar.scores_exam_submission_calendar import ScoresExamSubmissionCalendar
from assessments.forms.score_encoding import ScoreEncodingForm, ScoreEncodingFormSet
from osis_role.contrib.views import PermissionRequiredMixin


class LearningUnitScoreEncodingBaseFormView(PermissionRequiredMixin, FormView):
    # PermissionRequiredMixin
    permission_required = "assessments.can_access_scoreencoding"

    @cached_property
    def echeance_enseignant_filter(self) -> Optional[datetime.date]:
        with contextlib.suppress(TypeError, ValueError):
            echeance_enseignant_queryparams = self.request.GET.get('echeance_enseignant')
            return datetime.datetime.strptime(echeance_enseignant_queryparams, "%d/%m/%Y").date()
        return None

    @cached_property
    def person(self):
        return self.request.user.person

    @cached_property
    def feuille_de_notes(self):
        raise NotImplementedError()

    def dispatch(self, request, *args, **kwargs):
        opened_calendars = ScoresExamSubmissionCalendar().get_opened_academic_events()
        if not opened_calendars:
            redirect_url = reverse('outside_scores_encodings_period')
            return HttpResponseRedirect(redirect_url)
        return super().dispatch(request, *args, **kwargs)

    def get_form_class(self):
        return formset_factory(ScoreEncodingForm, formset=ScoreEncodingFormSet, extra=0)

    def get_context_data(self, **kwargs):
        context = {
            **super().get_context_data(**kwargs),
            'feuille_de_notes': self.feuille_de_notes,
            'cancel_url': self.get_cancel_url()
        }
        return context

    def get_success_url(self):
        redirect_url = reverse(
            'learning_unit_score_encoding',
            kwargs={'learning_unit_code': self.kwargs['learning_unit_code']}
        )
        return redirect(redirect_url)

    def get_cancel_url(self):
        return reverse('learning_unit_score_encoding', kwargs={
            'learning_unit_code': self.kwargs['learning_unit_code']
        })

    def get_permission_object(self):
        return None

    def _get_initial_note_etudiant(self, note_etudiant):
        try:
            note_format = "1" if self.feuille_de_notes.note_decimale_est_autorisee else "0"
            note_formated = floatformat(float(note_etudiant.note), note_format)
        except ValueError:
            note_formated = note_etudiant.note
        return {'note': note_formated, 'noma': note_etudiant.noma}
