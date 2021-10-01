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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
import uuid
from typing import List

import attr

from osis_common.ddd import interface


@attr.s(frozen=True, slots=True)
class NoteEtudiantEnregistree(interface.ValueObject):
    noma = attr.ib(type=str)
    numero_session = attr.ib(type=int)
    code_unite_enseignement = attr.ib(type=str)
    annee_academique = attr.ib(type=int)


@attr.s(frozen=True, slots=True)
class NoteEtudiantNonEnregistree(interface.ValueObject):
    noma = attr.ib(type=str)
    numero_session = attr.ib(type=int)
    code_unite_enseignement = attr.ib(type=str)
    annee_academique = attr.ib(type=int)
    cause = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class IdentiteEncoderNotesRapport(interface.EntityIdentity):
    transaction_id = attr.ib(type=uuid.UUID)


@attr.s()
class EncoderNotesRapport(interface.RootEntity):
    entity_id = attr.ib(type=IdentiteEncoderNotesRapport)
    notes_enregistrees = attr.ib(init=False, type=List[NoteEtudiantEnregistree], factory=list)
    notes_non_enregistreees = attr.ib(init=False, type=List[NoteEtudiantNonEnregistree], factory=list)

    def add_note_enregistree(self, noma: str, numero_session: int, code_unite_enseignement: str, annee_academique: int):
        note_enregistree = NoteEtudiantEnregistree(noma, numero_session, code_unite_enseignement, annee_academique)
        self.notes_enregistrees.append(note_enregistree)

    def add_note_non_enregistree(
            self,
            noma: str,
            numero_session: int,
            code_unite_enseignement: str,
            annee_academique: int,
            cause: str,
    ):
        note_enregistree = NoteEtudiantNonEnregistree(
            noma, numero_session, code_unite_enseignement, annee_academique, cause
        )
        self.notes_non_enregistreees.append(note_enregistree)

    def get_notes_enregistrees(self) -> List[NoteEtudiantEnregistree]:
        return self.notes_enregistrees

    def get_notes_non_enregistrees(self) -> List[NoteEtudiantNonEnregistree]:
        return self.notes_non_enregistreees
