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
from osis_role.contrib.views import PermissionRequiredMixin


class LearningUnitScoreEncodingBaseView(PermissionRequiredMixin, TemplateView):
    # PermissionRequiredMixin
    permission_required = "assessments.can_access_scoreencoding"

    @cached_property
    def person(self):
        return self.request.user.person

    def dispatch(self, request, *args, **kwargs):
        opened_calendars = ScoresExamSubmissionCalendar().get_opened_academic_events()
        if not opened_calendars:
            redirect_url = reverse('outside_scores_encodings_period')
            return HttpResponseRedirect(redirect_url)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            'learning_unit_encoding_url': self.get_learning_unit_encoding_url(),
            'learning_unit_double_encoding_url': self.get_learning_unit_double_encoding_url(),
            'learning_unit_print_url': self.get_learning_unit_print_url(),
            'learning_unit_download_xls_url': self.get_learning_unit_download_xls_url(),
            'learning_unit_upload_xls_url': self.get_learning_unit_upload_xls_url(),
            'learning_unit_submit_url': self.get_learning_unit_submit_url(),
        }

    def get_learning_unit_encoding_url(self):
        return reverse('learning_unit_score_encoding_form', kwargs={
            'learning_unit_code': self.kwargs['learning_unit_code']
        })

    def get_learning_unit_double_encoding_url(self):
        return ""

    def get_learning_unit_print_url(self):
        return reverse('score_sheet_pdf_export', kwargs={
            'learning_unit_code': self.kwargs['learning_unit_code']
        })

    def get_learning_unit_download_xls_url(self):
        return reverse('score_sheet_xls_export', kwargs={
            'learning_unit_code': self.kwargs['learning_unit_code']
        })

    def get_learning_unit_upload_xls_url(self):
        return reverse('score_sheet_xls_import', kwargs={
            'learning_unit_code': self.kwargs['learning_unit_code']
        })

    def get_learning_unit_submit_url(self):
        return reverse('learning_unit_score_encoding_submit', kwargs={
            'learning_unit_code': self.kwargs['learning_unit_code']
        })

    def get_permission_object(self):
        return None
