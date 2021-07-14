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
import decimal
from decimal import Decimal
from typing import Optional

import attr

from base.ddd.utils.business_validator import BusinessValidator
from ddd.logic.encodage_des_notes.business_types import *
from ddd.logic.encodage_des_notes.soumission.domain.validator.exceptions import NoteDecimaleNonAutoriseeException


@attr.s(frozen=True, slots=True)
class ShouldVerifierNoteDecimaleAutorisee(BusinessValidator):
    note = attr.ib(type=str)
    feuille_de_note = attr.ib(type='FeuilleDeNotes')  # type: FeuilleDeNotes

    def validate(self, *args, **kwargs):
        note_chiffree = self.__get_note_chiffree()
        if note_chiffree:
            is_integer = note_chiffree % 1 == 0
            if not self.feuille_de_note.note_decimale_est_autorisee() and not is_integer:
                raise NoteDecimaleNonAutoriseeException()

    def __get_note_chiffree(self) -> Optional[Decimal]:
        try:
            return decimal.Decimal(self.note)
        except decimal.InvalidOperation:
            return
