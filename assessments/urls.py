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
from django.conf.urls import url, include
from django.urls import path, register_converter

from assessments.views import score_encoding, upload_xls_utils, pgm_manager_administration, score_sheet
from assessments.views.program_manager import pgm_manager_administration as pgm_manager_administration_new
from assessments.views import scores_responsible
from assessments.views.address.score_sheet import ScoreSheetAddressView, FirstYearBachelorScoreSheetAddressView
from assessments.views.pgm_manager_administration import ProgramManagerListView, ProgramManagerDeleteView, \
    ProgramManagerCreateView, PersonAutocomplete, MainProgramManagerUpdateView, MainProgramManagerPersonUpdateView, \
    ProgramManagerPersonDeleteView
from assessments.views.program_manager.pgm_manager_administration import \
    ProgramManagerListView as ProgramManagerListViewNew, ProgramManagerDeleteView as ProgramManagerDeleteViewNew, \
    ProgramManagerCreateView as ProgramManagerCreateViewNew, \
    MainProgramManagerUpdateView as MainProgramManagerUpdateViewNew, \
    MainProgramManagerPersonUpdateView as MainProgramManagerPersonUpdateViewNew, \
    ProgramManagerPersonDeleteView as ProgramManagerPersonDeleteViewNew
from assessments.views.program_manager.score_search import ScoreSearchFormView
from assessments.views.score_encoding import LearningUnitScoreEncodingView, LearningUnitScoreEncodingFormView, \
    ScoreSheetPDFExportView, ScoreSheetXLSExportView, ScoreSheetXLSImportView, ScoreEncodingProgressOverviewView, \
    ScoreSheetsPDFExportView
from assessments.views.scores_responsible import ScoresResponsibleSearch
from assessments.views.tutor.learning_unit_score_encoding_submit import LearningUnitScoreEncodingTutorSubmitView
from education_group.converters import AcronymConverter

register_converter(AcronymConverter, 'acronym')

urlpatterns = [
    url(r'^scores_encoding/', include([
        url(r'^$', score_encoding.scores_encoding, name='scores_encoding'),
        url(r'^outside_period/$',
            score_encoding.outside_period, name='outside_scores_encodings_period'),
        url(r'^online/(?P<learning_unit_year_id>[0-9]+)/$',
            score_encoding.online_encoding, name='online_encoding'),
        url(r'^online/(?P<learning_unit_year_id>[0-9]+)/form$',
            score_encoding.online_encoding_form, name='online_encoding_form'),
        url(r'^online/([0-9]+)/submission$',
            score_encoding.online_encoding_submission, name='online_encoding_submission'),
        url(r'^online/(?P<learning_unit_year_id>[0-9]+)/double_form$',
            score_encoding.online_double_encoding_form, name='online_double_encoding_form'),
        url(r'^online/(?P<learning_unit_year_id>[0-9]+)/double_validation$',
            score_encoding.online_double_encoding_validation, name='online_double_encoding_validation'),
        url(r'^specific_criteria/$',
            score_encoding.specific_criteria, name='specific_criteria'),
        url(r'^specific_criteria/submission/$',
            score_encoding.specific_criteria_submission, name='specific_criteria_submission'),
        url(r'^specific_criteria/search/$',
            score_encoding.search_by_specific_criteria, name='search_by_specific_criteria'),
        url(r'^notes_printing_all(?:/(?P<tutor_id>[0-9]+))?(?:/(?P<education_group_year_id>[0-9]+))?/$',
            score_encoding.notes_printing_all, name='notes_printing_all'),
        url(r'^notes_printing/(?P<learning_unit_year_id>[0-9]+)(?:/(?P<tutor_id>[0-9]+))?/$',
            score_encoding.notes_printing, name='notes_printing'),
        url(r'^xlsdownload/([0-9]+)/$',
            score_encoding.export_xls, name='scores_encoding_download'),
        url(r'^upload/(?P<learning_unit_year_id>[0-9]+)/$',
            upload_xls_utils.upload_scores_file, name='upload_encoding'),

        # New URL's
        path('overview', ScoreEncodingProgressOverviewView.as_view(), name="score_encoding_progress_overview"),
        path('search', ScoreSearchFormView.as_view(), name='score_search'),
        path('<str:learning_unit_code>/', include(([
            path('', LearningUnitScoreEncodingView.as_view(), name='learning_unit_score_encoding'),
            path('form', LearningUnitScoreEncodingFormView.as_view(), name='learning_unit_score_encoding_form'),
            path(
                'submit',
                LearningUnitScoreEncodingTutorSubmitView.as_view(),
                name='learning_unit_score_encoding_submit',
            ),
            path('pdf_export', ScoreSheetPDFExportView.as_view(), name='score_sheet_pdf_export'),
            path('xls_export', ScoreSheetXLSExportView.as_view(), name='score_sheet_xls_export'),
            path('xls_import', ScoreSheetXLSImportView.as_view(), name='score_sheet_xls_import'),
        ]))),
        path('pdf_export', ScoreSheetsPDFExportView.as_view(), name='score_sheets_pdf_export'),
    ])),

    url(r'^offers/', include([
        url(r'^(?P<education_group_id>[0-9]+)/', include([
            url(r'^score_encoding/$', score_sheet.offer_score_encoding_tab, name='offer_score_encoding_tab'),
            url(r'^score_sheet_address/save/$', score_sheet.save_score_sheet_address, name='save_score_sheet_address'),
        ])),

        # New URL's
        path('<acronym:acronym>/', include([
            url(r'^score_encoding/$', ScoreSheetAddressView.as_view(), name='score_sheet_address'),
            url(
                r'^first_year_bachelor/score_encoding/$',
                FirstYearBachelorScoreSheetAddressView.as_view(),
                name='first_year_bachelor_score_sheet_address'
            ),
        ]))
    ])),

    url(r'^pgm_manager/', include([
        url(r'^$', pgm_manager_administration.pgm_manager_administration, name='pgm_manager'),
        url(r'^search$', pgm_manager_administration.pgm_manager_search, name='pgm_manager_search'),
        url(r'^manager_list/$', ProgramManagerListView.as_view(), name='manager_list'),
        url(r'^update_main/(?P<pk>[0-9]+)/$', MainProgramManagerUpdateView.as_view(), name='update_main'),
        url(r'^update_main_person/(?P<pk>[0-9]+)/$', MainProgramManagerPersonUpdateView.as_view(),
            name='update_main_person'),
        url(r'^delete_manager/(?P<pk>[0-9]+)/$', ProgramManagerDeleteView.as_view(), name='delete_manager'),
        url(r'^delete_manager_person/(?P<pk>[0-9]+)/$', ProgramManagerPersonDeleteView.as_view()),
        url(r'^create$', ProgramManagerCreateView.as_view(), name='create_manager_person'),
        url(r'^person-autocomplete/$', PersonAutocomplete.as_view(), name='person-autocomplete'),
    ])),
    url(r'^program_manager/', include([
        url(r'^$', pgm_manager_administration_new.pgm_manager_administration, name='program_manager'),
        url(r'^search$', pgm_manager_administration_new.pgm_manager_search, name='program_manager_search'),
        url(r'^manager_list/$', ProgramManagerListViewNew.as_view(), name='program_manager_list'),
        url(r'^update_main/(?P<global_id>[0-9]+)/(?P<acronym>[a-zA-Z0-9/ \-_]+)/$',
            MainProgramManagerUpdateViewNew.as_view(), name='update_main'),
        url(r'^update_main_person/(?P<global_id>[0-9]+)/$', MainProgramManagerPersonUpdateViewNew.as_view(),
            name='update_main_person'),
        url(r'^delete_manager/(?P<global_id>[0-9]+)/(?P<acronym>[a-zA-Z0-9/ \-_]+)/$',
            ProgramManagerDeleteViewNew.as_view(), name='delete_manager'),
        url(r'^delete_manager_person/(?P<global_id>[0-9]+)/$', ProgramManagerPersonDeleteViewNew.as_view(),
            name='delete_manager_person'),
        url(r'^create$', ProgramManagerCreateViewNew.as_view(), name='create_program_manager_person'),
        url(r'^person-autocomplete/$', PersonAutocomplete.as_view(), name='person-autocomplete'),
    ])),

    url(r'^srm_manager/', include([
        url(r'^list/$', ScoresResponsibleSearch.as_view(), name='scores_responsible_list'),
        url(r'^scores_responsible_management/edit/$', scores_responsible.scores_responsible_management,
            name='scores_responsible_management'),
        url(r'^scores_responsible_add/(?P<pk>[0-9]+)/$', scores_responsible.scores_responsible_add,
            name='scores_responsible_add'),
    ])),

    url(r'^$', score_encoding.assessments, name="assessments"),
]
