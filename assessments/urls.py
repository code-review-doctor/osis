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

from assessments.views.address.score_sheet import ScoreSheetAddressView, FirstYearBachelorScoreSheetAddressView
from assessments.views.address.search import OffersSearch
from assessments.views.home import AssessmentsHome
from assessments.views.program_manager import pgm_manager_administration as pgm_manager_administration_new
from assessments.views.program_manager.pgm_manager_administration import \
    ProgramManagerListView as ProgramManagerListViewNew, ProgramManagerDeleteView as ProgramManagerDeleteViewNew, \
    ProgramManagerCreateView as ProgramManagerCreateViewNew, \
    MainProgramManagerUpdateView as MainProgramManagerUpdateViewNew, \
    MainProgramManagerPersonUpdateView as MainProgramManagerPersonUpdateViewNew, \
    ProgramManagerPersonDeleteView as ProgramManagerPersonDeleteViewNew, PersonAutocomplete
from assessments.views.program_manager.score_encoding_progress_overview import CodeUniteEnseignementAutocomplete, \
    EnseignantAutocomplete, FormationAutocomplete
from assessments.views.program_manager.score_search import ScoreSearchFormView
from assessments.views.program_manager.scores_responsible import ScoresResponsiblesSearch, SelectScoreResponsible
from assessments.views.score_encoding.edit_learning_unit_score import LearningUnitScoreEncodingFormView
from assessments.views.score_encoding.learning_unit_score import LearningUnitScoreEncodingView
from assessments.views.score_encoding.outside_period import OutsidePeriod
from assessments.views.score_encoding.overview import ScoreEncodingProgressOverviewView
from assessments.views.score_encoding.pdf import ScoreSheetsPDFExportView
from assessments.views.score_encoding.xls import ScoreSheetXLSExportView, ScoreSheetXLSImportView
from assessments.views.tutor.learning_unit_score_encoding_submit import LearningUnitScoreEncodingTutorSubmitView
from education_group.converters import AcronymConverter

register_converter(AcronymConverter, 'acronym')

urlpatterns = [
    url(r'^scores_encoding/', include([
        url(r'^outside_period/$',
            OutsidePeriod.as_view(), name='outside_scores_encodings_period'),

        # New URL's
        path('overview', ScoreEncodingProgressOverviewView.as_view(), name="score_encoding_progress_overview"),
        path('search', ScoreSearchFormView.as_view(), name='score_search'),
        path(
            'search_learning_unit_code',
            CodeUniteEnseignementAutocomplete.as_view(),
            name='learning-unit-code-autocomplete',
        ),
        path(
            'search_enseignants',
            EnseignantAutocomplete.as_view(),
            name='enseignants-autocomplete',
        ),
        path(
            'search_formation',
            FormationAutocomplete.as_view(),
            name='formations-autocomplete',
        ),
        path('<str:learning_unit_code>/', include(([
            path('', LearningUnitScoreEncodingView.as_view(), name='learning_unit_score_encoding'),
            path('form', LearningUnitScoreEncodingFormView.as_view(), name='learning_unit_score_encoding_form'),
            path(
                'submit',
                LearningUnitScoreEncodingTutorSubmitView.as_view(),
                name='learning_unit_score_encoding_submit',
            ),
            path('xls_export', ScoreSheetXLSExportView.as_view(), name='score_sheet_xls_export'),
            path('xls_import', ScoreSheetXLSImportView.as_view(), name='score_sheet_xls_import'),
        ]))),
        path('pdf_export', ScoreSheetsPDFExportView.as_view(), name='score_sheets_pdf_export'),
    ])),

    path('offers/', include([
        path('', OffersSearch.as_view(), name='offers_search'),
        path('<acronym:acronym>/', include([
            path('score_encoding', ScoreSheetAddressView.as_view(), name='score_sheet_address'),
            path(
                'first_year_bachelor/score_encoding',
                FirstYearBachelorScoreSheetAddressView.as_view(),
                name='first_year_bachelor_score_sheet_address'
            ),
        ]))
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

    path('scores_responsibles/', include([
        path('', ScoresResponsiblesSearch.as_view(), name='scores_responsibles_search'),
        path('select/<acronym:code>/', SelectScoreResponsible.as_view(), name='score_responsible_select'),
    ])),

    url(r'^$', AssessmentsHome.as_view(), name="assessments"),
]
