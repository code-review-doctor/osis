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
from django.urls import path

from assessments.api.views.assessments import CurrentExamSessionView, NextSessionExamView, PreviousSessionExamView
from assessments.api.views.score_responsibles import ScoreResponsibleList
from assessments.api.views.score_sheet_xls_export import ScoreSheetXLSExportAPIView
from assessments.api.views.score_sheets_pdf_export import ScoreSheetsPDFExportAPIView

app_name = "assessments_api_v1"
urlpatterns = [
    path('pdf_export', ScoreSheetsPDFExportAPIView.as_view(), name=ScoreSheetsPDFExportAPIView.name),
    path(
        '<str:learning_unit_code>/xls_export',
        ScoreSheetXLSExportAPIView.as_view(),
        name=ScoreSheetXLSExportAPIView.name,
    ),
    path('current_session/', CurrentExamSessionView.as_view(), name=CurrentExamSessionView.name),
    path('next_session/', NextSessionExamView.as_view(), name=NextSessionExamView.name),
    path('previous_session/', PreviousSessionExamView.as_view(), name=PreviousSessionExamView.name),
    path('score_responsibles/', ScoreResponsibleList.as_view(), name=ScoreResponsibleList.name),
]
