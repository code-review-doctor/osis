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
from django.utils.translation import gettext_lazy as _

from assessments.views.common.score_sheet_xls_import import ScoreSheetXLSImportBaseView
from base.ddd.utils.business_validator import MultipleBusinessExceptions
from ddd.logic.encodage_des_notes.soumission.commands import EncoderNoteCommand
from infrastructure.messages_bus import message_bus_instance


class ScoreSheetXLSImportTutorView(ScoreSheetXLSImportBaseView):
    def call_command(self, matricule, score_sheet_serialized):
        injected_notes_counter = 0

        for note_etudiant in score_sheet_serialized['notes_etudiants']:
            cmd = EncoderNoteCommand(
                code_unite_enseignement=note_etudiant['code_unite_enseignement'],
                annee_unite_enseignement=score_sheet_serialized['annee_academique'],
                numero_session=score_sheet_serialized['numero_session'],
                matricule_fgs_enseignant=matricule,
                noma_etudiant=note_etudiant['noma'],
                email_etudiant=note_etudiant['email'],
                note=note_etudiant['note'],
            )
            try:
                message_bus_instance.invoke(cmd)
                injected_notes_counter += 1
            except MultipleBusinessExceptions as e:
                for exception in e.exceptions:
                    error_message = "{} : {} {}".format(exception.message, _('Row'), str(note_etudiant['row_number']))
                    messages.error(self.request, error_message)

        if injected_notes_counter:
            messages.success(self.request, "{} {}".format(str(injected_notes_counter), _("Score(s) saved")))
        else:
            messages.error(self.request, _("No score injected"))
