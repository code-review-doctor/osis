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
from base.ddd.utils.business_validator import MultipleBusinessExceptions
from ddd.logic.encodage_des_notes.soumission.commands import EncoderFeuilleDeNotesCommand
from ddd.logic.encodage_des_notes.soumission.domain.model.feuille_de_notes import FeuilleDeNotes
from osis_common.ddd import interface


class EncoderFeuilleDeNotes(interface.DomainService):

    @classmethod
    def encoder(
            cls,
            cmd: 'EncoderFeuilleDeNotesCommand',
            feuille_de_notes: 'FeuilleDeNotes',
    ) -> None:
        exceptions = set()
        for note_etd in cmd.notes_etudiants:
            try:
                feuille_de_notes.encoder_note(noma=note_etd.noma, email=note_etd.email, note_encodee=note_etd.note)
            except MultipleBusinessExceptions as e:
                exceptions |= e.exceptions

        if exceptions:
            raise MultipleBusinessExceptions(exceptions=exceptions)
