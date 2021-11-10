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
import contextlib

from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from assessments.views.common.score_sheet_xls_import import ScoreSheetXLSImportBaseView
from assessments.views.serializers.score_sheet_xls_import import ProgramManagerScoreSheetXLSImportSerializer
from base.ddd.utils.business_validator import MultipleBusinessExceptions
from ddd.logic.encodage_des_notes.encodage.commands import EncoderNotesCommand, EncoderNoteCommand
from ddd.logic.encodage_des_notes.shared_kernel.commands import GetEncoderNotesRapportCommand
from infrastructure.messages_bus import message_bus_instance


class ScoreSheetXLSImportProgramManagerView(ScoreSheetXLSImportBaseView):
    def get_xls_import_serializer_cls(self):
        return ProgramManagerScoreSheetXLSImportSerializer

    def call_command(self, matricule, score_sheet_serialized):
        cmd = self._get_command(self.person.global_id, score_sheet_serialized)

        with contextlib.suppress(MultipleBusinessExceptions):
            message_bus_instance.invoke(cmd)

        get_rapport_cmd = GetEncoderNotesRapportCommand(from_transaction_id=cmd.transaction_id)
        rapport = message_bus_instance.invoke(get_rapport_cmd)

        for note_non_enregistrees in rapport.get_notes_non_enregistrees():
            row_number = next(
                note_etudiant['row_number'] for note_etudiant in score_sheet_serialized['notes_etudiants']
                if note_etudiant['noma'] == note_non_enregistrees.noma
            )
            error_message = "{} : {} {}".format(note_non_enregistrees.cause, _('Row'), str(row_number))
            messages.error(self.request, error_message)

        nombre_notes_enregistrees = len(rapport.get_notes_enregistrees())
        if nombre_notes_enregistrees:
            messages.success(self.request, "{} {}".format(str(nombre_notes_enregistrees), _("Score(s) saved")))
        else:
            messages.error(self.request, _("No score injected"))

    @staticmethod
    def _get_command(matricule_gestionnaire, score_sheet_serialized):
        cmd = EncoderNotesCommand(
            matricule_fgs_gestionnaire=matricule_gestionnaire,
            notes_encodees=[
                EncoderNoteCommand(
                    noma=note_etudiant['noma'],
                    email=note_etudiant['email'],
                    code_unite_enseignement=note_etudiant['code_unite_enseignement'],
                    note=note_etudiant['note'],
                ) for note_etudiant in score_sheet_serialized['notes_etudiants'] if note_etudiant['note']
            ]
        )
        return cmd
