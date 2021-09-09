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
import urllib

from django.contrib import messages
from django.forms import formset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.functional import cached_property
from django.views.generic import FormView
from django.utils.translation import gettext_lazy as _, ngettext

from assessments.calendar.scores_exam_submission_calendar import ScoresExamSubmissionCalendar
from assessments.forms.score_encoding import ScoreSearchForm, ScoreSearchEncodingForm, ScoreEncodingFormSet
from base.ddd.utils.business_validator import MultipleBusinessExceptions
from ddd.logic.encodage_des_notes.encodage.commands import RechercherNotesCommand, EncoderNotesCommand, \
    EncoderNoteCommand
from infrastructure.messages_bus import message_bus_instance
from osis_role.contrib.views import PermissionRequiredMixin


class ScoreSearchFormView(PermissionRequiredMixin, FormView):
    # PermissionRequiredMixin
    permission_required = "assessments.can_access_scoreencoding"

    # FormView
    template_name = "assessments/program_manager/score_search_form.html"

    @cached_property
    def person(self):
        return self.request.user.person

    def dispatch(self, request, *args, **kwargs):
        opened_calendars = ScoresExamSubmissionCalendar().get_opened_academic_events()
        if not opened_calendars:
            redirect_url = reverse('outside_scores_encodings_period')
            return HttpResponseRedirect(redirect_url)
        return super().dispatch(request, *args, **kwargs)

    def get_search_form(self):
        return ScoreSearchForm(data=self.request.GET or None, matricule_fgs_gestionnaire=self.person.global_id)

    def get_form_class(self):
        return formset_factory(
            ScoreSearchEncodingForm,
            formset=ScoreEncodingFormSet,
            extra=0,
            max_num=len(self.get_initial())
        )

    def get_initial(self):
        formeset_initial = []
        for note_etudiant in self.notes_etudiant_filtered:
            if not note_etudiant.date_echeance_atteinte and not note_etudiant.desinscrit_tardivement:
                formeset_initial.append({
                    'note': note_etudiant.note,
                    'noma': note_etudiant.noma,
                    'code_unite_enseignement': note_etudiant.code_unite_enseignement
                })
            else:
                formeset_initial.append({})
        return formeset_initial

    def form_valid(self, formset):
        cmd = EncoderNotesCommand(
            matricule_fgs_gestionnaire=self.person.global_id,
            notes_encodees=[
                EncoderNoteCommand(
                    noma=form.cleaned_data['noma'],
                    email=next(
                        note.email for note in self.notes_etudiant_filtered if note.noma == form.cleaned_data['noma']
                    ),
                    code_unite_enseignement=form.cleaned_data['code_unite_enseignement'],
                    note=form.cleaned_data['note']
                ) for form in formset if form.has_changed()
            ]
        )

        if cmd.notes_encodees:
            try:
                message_bus_instance.invoke(cmd)
            except MultipleBusinessExceptions as e:
                for exception in e.exceptions:
                    form = next(
                        form for form in formset
                        if form.has_changed() and form.cleaned_data['noma'] == exception.note_id.noma and
                        form.cleaned_data['code_unite_enseignement'] == exception.note_id.code_unite_enseignement
                    )
                    form.add_error('note', exception.message)

        self.display_success_error_counter(cmd, formset)
        if formset.is_valid():
            return self.get_success_url()
        return self.render_to_response(self.get_context_data(form=formset))

    def display_success_error_counter(self, cmd, formset):
        error_counter = sum(1 for form in formset if form.has_changed() and not form.is_valid())
        success_counter = len(cmd.notes_encodees) - error_counter
        if error_counter > 0:
            messages.error(
                self.request,
                ngettext(
                    "There is %(error_counter)s error in form",
                    "There are %(error_counter)s errors in form",
                    error_counter
                ) % {'error_counter': error_counter}
            )
        if success_counter > 0:
            messages.success(self.request, '%s %s' % (str(success_counter), _('Score(s) saved')))

    def get_success_url(self):
        redirect_url = reverse('score_search') + "?" + urllib.parse.urlencode(self.request.GET)
        return redirect(redirect_url)

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            'search_form': self.get_search_form(),
            'notes_etudiant_filtered': self.notes_etudiant_filtered,
            'score_encoding_progress_overview_url': self.get_score_encoding_progress_overview_url()
        }

    @cached_property
    def notes_etudiant_filtered(self):
        search_form = self.get_search_form()
        if search_form.is_valid():
            cmd = RechercherNotesCommand(
                noma=search_form.cleaned_data['noma'],
                nom=search_form.cleaned_data['nom'],
                prenom=search_form.cleaned_data['prenom'],
                etat=search_form.cleaned_data['justification'],
                nom_cohorte=search_form.cleaned_data['nom_cohorte'],
                matricule_fgs_gestionnaire=self.person.global_id
            )
            return message_bus_instance.invoke(cmd)
        return []

    def get_score_encoding_progress_overview_url(self):
        return reverse('score_encoding_progress_overview')
