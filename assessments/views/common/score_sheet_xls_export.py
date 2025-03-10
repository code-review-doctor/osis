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
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils.functional import cached_property
from django.views import View
from django.utils.translation import gettext_lazy as _

from assessments.export import score_sheet_xls
from assessments.views.serializers.score_sheet_xls import ScoreSheetXLSSerializer
from ddd.logic.encodage_des_notes.soumission.commands import SearchAdressesFeuilleDeNotesCommand
from infrastructure.messages_bus import message_bus_instance
from osis_common.decorators.download import set_download_cookie
from osis_common.document import xls_build
from osis_role.contrib.views import PermissionRequiredMixin


# TODO: Move to osis-common
class XLSResponse(HttpResponse):
    def __init__(self, xls_file=b'', filename='', **kwargs):
        super().__init__(
            content=xls_file,
            content_type=xls_build.CONTENT_TYPE_XLS,
            **kwargs
        )
        self._headers['content-disposition'] = ('Content-Disposition',  'attachment; filename=%s' % filename)


class ScoreSheetXLSExportBaseView(PermissionRequiredMixin, View):
    # PermissionRequiredMixin
    permission_required = "assessments.can_access_scoreencoding"

    @cached_property
    def person(self):
        return self.request.user.person

    @cached_property
    def feuille_de_notes(self):
        raise NotImplementedError()

    @cached_property
    def donnees_administratives(self):
        cmd = SearchAdressesFeuilleDeNotesCommand(
            codes_unite_enseignement=[self.kwargs['learning_unit_code']]
        )
        return message_bus_instance.invoke(cmd)

    @set_download_cookie
    def get(self, request, *args, **kwargs):
        score_sheet_serialized = self.get_score_sheet_xls_serializer_cls()(instance={
            'feuille_de_notes': self.feuille_de_notes,
            'donnees_administratives': self.donnees_administratives,
        }).data

        if len(score_sheet_serialized['rows']):
            virtual_workbook = score_sheet_xls.build_xls(score_sheet_serialized)
            return XLSResponse(xls_file=virtual_workbook, filename=self.get_filename())
        else:
            messages.add_message(request, messages.WARNING, _("No students to encode by excel"))
            return HttpResponseRedirect(
                reverse('learning_unit_score_encoding', kwargs={
                    'learning_unit_code': self.kwargs['learning_unit_code'],
                })
            )

    def get_score_sheet_xls_serializer_cls(self):
        return ScoreSheetXLSSerializer

    def get_filename(self) -> str:
        return "session_%s_%s_%s.xlsx" % (
            str(self.feuille_de_notes.annee_academique),
            str(self.feuille_de_notes.numero_session),
            str(self.feuille_de_notes.code_unite_enseignement),
        )
