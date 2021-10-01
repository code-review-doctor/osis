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
from rest_framework import exceptions
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView

from assessments.views.serializers.score_sheet import ScoreSheetPDFSerializer
from base.auth.roles.tutor import Tutor
from ddd.logic.encodage_des_notes.soumission.commands import GetFeuilleDeNotesCommand, \
    SearchAdressesFeuilleDeNotesCommand
from infrastructure.messages_bus import message_bus_instance
from assessments.export import score_sheet_pdf
from osis_role.contrib.helper import EntityRoleHelper


class ScoreSheetsPDFExportAPIView(APIView):
    name = "score_sheets_pdf_export"

    @cached_property
    def person(self):
        return self.request.user.person

    @cached_property
    def is_tutor(self):
        return EntityRoleHelper.has_role(self.person, Tutor)

    def get(self, request, *args, **kwargs):
        if self.kwargs['learning_unit_code']:
            codes_unites_enseignement = [self.kwargs['learning_unit_code']]
        else:
            codes_unites_enseignement = self.request.GET.getlist('codes')

        if not len(codes_unites_enseignement):
            raise ValidationError(detail="codes queryparam missing")

        score_sheet_serialized = ScoreSheetPDFSerializer(
            instance=[
                {
                    'feuille_de_notes': self.get_feuille_de_notes(code),
                    'donnees_administratives': self.get_donnees_administratives(code)
                } for code in codes_unites_enseignement
            ],
            context={'person': self.person}
        )
        return score_sheet_pdf.print_notes(score_sheet_serialized.data)

    def get_donnees_administratives(self, code_unite_enseignement: str):
        cmd = SearchAdressesFeuilleDeNotesCommand(
            codes_unite_enseignement=[code_unite_enseignement]
        )
        return message_bus_instance.invoke(cmd)

    def get_feuille_de_notes(self, code_unite_enseignement: str):
        if self.is_tutor:
            cmd = GetFeuilleDeNotesCommand(
                matricule_fgs_enseignant=self.person.global_id,
                code_unite_enseignement=code_unite_enseignement
            )
            return message_bus_instance.invoke(cmd)
        raise exceptions.PermissionDenied()
