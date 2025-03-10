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
from django.utils.functional import cached_property
from django.views import View
from rules.contrib.views import LoginRequiredMixin

from assessments.views.program_manager.score_sheet_xls_export import ScoreSheetXLSExportProgramManagerView
from assessments.views.program_manager.score_sheet_xls_import import ScoreSheetXLSImportProgramManagerView
from assessments.views.tutor.score_sheet_xls_export import ScoreSheetXLSExportTutorView
from assessments.views.tutor.score_sheet_xls_import import ScoreSheetXLSImportTutorView
from base.auth.roles.program_manager import ProgramManager
from base.auth.roles.tutor import Tutor
from base.models.person import Person
from osis_role.contrib.helper import EntityRoleHelper


class ScoreSheetXLSExportView(LoginRequiredMixin, View):
    @cached_property
    def person(self) -> Person:
        return self.request.user.person

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if EntityRoleHelper.has_role(self.person, Tutor):
            return ScoreSheetXLSExportTutorView.as_view()(request, *args, **kwargs)
        elif EntityRoleHelper.has_role(self.person, ProgramManager):
            return ScoreSheetXLSExportProgramManagerView.as_view()(request, *args, **kwargs)
        return self.handle_no_permission()


class ScoreSheetXLSImportView(LoginRequiredMixin, View):
    @cached_property
    def person(self):
        return self.request.user.person

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if EntityRoleHelper.has_role(self.person, Tutor):
            return ScoreSheetXLSImportTutorView.as_view()(request, *args, **kwargs)
        elif EntityRoleHelper.has_role(self.person, ProgramManager):
            return ScoreSheetXLSImportProgramManagerView.as_view()(request, *args, **kwargs)
        return self.handle_no_permission()
