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
from django.utils.translation import gettext_lazy as _
from django.utils.functional import cached_property
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework import exceptions

from assessments.export import score_sheet_xls
from assessments.views.common.score_sheet_xls_export import XLSResponse
from assessments.views.serializers.score_sheet_xls import TutorScoreSheetXLSSerializer
from base.auth.roles.tutor import Tutor
from ddd.logic.encodage_des_notes.soumission.commands import SearchAdressesFeuilleDeNotesCommand, \
    GetFeuilleDeNotesCommand
from infrastructure.messages_bus import message_bus_instance
from osis_role.contrib.helper import EntityRoleHelper


class ScoreSheetXLSExportAPIView(APIView):
    name = 'score_sheet_xls_export'

    @cached_property
    def person(self):
        return self.request.user.person

    def get(self, request, *args, **kwargs):
        if self.feuille_de_notes:
            score_sheet_serialized = TutorScoreSheetXLSSerializer(instance={
                'feuille_de_notes': self.feuille_de_notes,
                'donnees_administratives': self.donnees_administratives,
            }).data

            if len(score_sheet_serialized['rows']):
                virtual_workbook = score_sheet_xls.build_xls(score_sheet_serialized)
                return XLSResponse(xls_file=virtual_workbook, filename=self.get_filename())
            raise ValidationError(detail=_("No student to encode by excel"))
        else:
            raise ValidationError(detail=_("There is no enrollment for this course"))

    @cached_property
    def donnees_administratives(self):
        cmd = SearchAdressesFeuilleDeNotesCommand(
            codes_unite_enseignement=[self.kwargs['learning_unit_code']]
        )
        return message_bus_instance.invoke(cmd)

    @cached_property
    def feuille_de_notes(self):
        if EntityRoleHelper.has_role(self.person, Tutor):
            try:
                cmd = GetFeuilleDeNotesCommand(
                    matricule_fgs_enseignant=self.person.global_id,
                    code_unite_enseignement=self.kwargs['learning_unit_code']
                )
                return message_bus_instance.invoke(cmd)
            except Exception as e:
                raise ValidationError(detail=e.message)
        raise exceptions.PermissionDenied()

    def get_filename(self) -> str:
        return "session_%s_%s_%s.xlsx" % (
            str(self.feuille_de_notes.annee_academique),
            str(self.feuille_de_notes.numero_session),
            str(self.feuille_de_notes.code_unite_enseignement),
        )
