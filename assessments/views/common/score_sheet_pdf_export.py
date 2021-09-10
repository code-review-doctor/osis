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

from assessments.views.serializers.score_sheet import ScoreSheetPDFSerializer
from ddd.logic.encodage_des_notes.soumission.commands import SearchAdressesFeuilleDeNotesCommand
from infrastructure.messages_bus import message_bus_instance
from osis_common.document import paper_sheet
from osis_role.contrib.views import PermissionRequiredMixin


class ScoreSheetPDFExportBaseView(PermissionRequiredMixin, View):
    # PermissionRequiredMixin
    permission_required = "assessments.can_access_scoreencoding"

    @cached_property
    def person(self):
        return self.request.user.person

    def get(self, request, *args, **kwargs):
        feuille_de_notes = self.get_feuille_de_notes()
        donnees_administratives = self.get_donnees_administratives()

        score_sheet_serialized = ScoreSheetPDFSerializer(instance={
            'feuille_de_notes': feuille_de_notes,
            'donnees_administratives': donnees_administratives
        }, context={'person': self.person})
        return paper_sheet.print_notes(score_sheet_serialized.data)

    def get_feuille_de_notes(self):
        raise NotImplementedError()

    def get_donnees_administratives(self):
        cmd = SearchAdressesFeuilleDeNotesCommand(
            codes_unite_enseignement=[self.kwargs['learning_unit_code']]
        )
        return message_bus_instance.invoke(cmd)


class ScoreSheetsPDFExportBaseView(PermissionRequiredMixin, View):
    # PermissionRequiredMixin
    permission_required = "assessments.can_access_scoreencoding"

    @cached_property
    def person(self):
        return self.request.user.person

    def get(self, request, *args, **kwargs):
        codes_unites_enseignement = self.request.GET.getlist('codes_unite_enseignement')

        score_sheet_serialized = ScoreSheetPDFSerializer(
            instance=[
                {
                    'feuille_de_notes': self.get_feuille_de_notes(code),
                    'donnees_administratives': self.get_donnees_administratives(code)
                } for code in codes_unites_enseignement
            ],
            context={'person': self.person}
        )
        return paper_sheet.print_notes(score_sheet_serialized.data)

    def get_feuille_de_notes(self, code_unite_enseignement: str):
        raise NotImplementedError()

    def get_donnees_administratives(self, code_unite_enseignement: str):
        cmd = SearchAdressesFeuilleDeNotesCommand(
            codes_unite_enseignement=[code_unite_enseignement.upper()]
        )
        return message_bus_instance.invoke(cmd)
