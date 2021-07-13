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
import datetime

from ddd.logic.encodage_des_notes.soumission.commands import EncoderFeuilleDeNotesCommand
from ddd.logic.encodage_des_notes.soumission.domain.service.i_periode_soumission_notes import \
    IPeriodeSoumissionNotesTranslator
from ddd.logic.encodage_des_notes.soumission.domain.validator.exceptions import PeriodeSoumissionNotesFermeeException
from osis_common.ddd import interface


class PeriodeSoumissionOuverte(interface.DomainService):

    @classmethod
    def verifier(
            cls,
            cmd: 'EncoderFeuilleDeNotesCommand',
            periode_soumission_note_translator: 'IPeriodeSoumissionNotesTranslator'
    ) -> None:
        periode = periode_soumission_note_translator.get()
        if not periode:
            raise PeriodeSoumissionNotesFermeeException()

        aujourdhui = datetime.date.today()
        debut_periode = periode.debut_periode_soumission.to_date()
        fin_periode = periode.fin_periode_soumission.to_date()
        periode_est_ouverte = debut_periode < aujourdhui < fin_periode

        annee_est_concernee = cmd.annee_unite_enseignement == periode.annee_concernee

        session_est_concernee = cmd.numero_session == periode.session_concernee

        if not periode_est_ouverte or not annee_est_concernee or not session_est_concernee:
            raise PeriodeSoumissionNotesFermeeException()
