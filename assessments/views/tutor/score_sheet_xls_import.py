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
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.functional import cached_property
from django.views.generic import FormView

from assessments.calendar.scores_exam_submission_calendar import ScoresExamSubmissionCalendar
from assessments.forms.score_file import ScoreFileForm
from assessments.views.serializers.score_sheet_xls_import import ScoreSheetXLSImportSerializer, \
    ScoreSheetXLSImportSerializerError
from base.views.mixins import AjaxTemplateMixin
from osis_role.contrib.views import AjaxPermissionRequiredMixin


class ScoreSheetXLSImportView(AjaxPermissionRequiredMixin, AjaxTemplateMixin, FormView):
    # PermissionRequiredMixin
    permission_required = "assessments.can_access_scoreencoding"

    # FormView
    template_name = "assessments/common/xls_import_modal_inner.html"
    form_class = ScoreFileForm

    @cached_property
    def person(self):
        return self.request.user.person

    def dispatch(self, request, *args, **kwargs):
        opened_calendars = ScoresExamSubmissionCalendar().get_opened_academic_events()
        if not opened_calendars:
            redirect_url = reverse('outside_scores_encodings_period')
            return HttpResponseRedirect(redirect_url)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        xls_workbook = form.cleaned_data['file']
        try:
            score_sheet_serialized = ScoreSheetXLSImportSerializer(xls_workbook.active).data
            for note_etudiant in score_sheet_serialized['notes_etudiants']:
                # TODO: Create command and invoke bus
                pass
        except ScoreSheetXLSImportSerializerError as e:
            messages.add_message(self.request, messages.ERROR, e.message)
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse('learning_unit_score_encoding', kwargs={
            'learning_unit_code': self.kwargs['learning_unit_code']
        })
