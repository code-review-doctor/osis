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
from datetime import date

import attr

from ddd.logic.encodage_des_notes.soumission.domain.model._note import Note
from osis_common.ddd import interface

Noma = str


@attr.s(frozen=True, slots=True)
class IdentiteNoteEtudiant(interface.EntityIdentity):
    noma = attr.ib(type=Noma)


@attr.s(slots=True, eq=False)
class NoteEtudiant(interface.Entity):
    entity_id = attr.ib(type=IdentiteNoteEtudiant)
    note = attr.ib(type=Note)
    date_limite_de_remise = attr.ib(type=date)
    est_soumise = attr.ib(type=bool)

    @property
    def is_chiffree(self) -> bool:
        return type(self.note.value) in (float, int)

    @property
    def is_manquant(self) -> bool:
        return not bool(self.note.value)

    @property
    def is_justification(self) -> bool:
        return not self.is_manquant and not self.is_chiffree
