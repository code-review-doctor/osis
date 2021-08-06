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

from ddd.logic.encodage_des_notes.encodage.domain.model._note import Note
from osis_common.ddd import interface

Noma = str


@attr.s(frozen=True, slots=True)
class IdentiteNoteEtudiant(interface.EntityIdentity):
    noma = attr.ib(type=Noma)
    code_unite_enseignement = attr.ib(type=str)
    annee_academique = attr.ib(type=int)
    numero_session = attr.ib(type=int)


@attr.s(slots=True)
class NoteEtudiant(interface.RootEntity):
    entity_id = attr.ib(type=IdentiteNoteEtudiant)
    note = attr.ib(type=Note)
    date_echeance = attr.ib(type=date)

    def encoder(self, note: str) -> None:
        raise NotImplementedError

    # def __encoder_note_de_presence(self):
    #     pass
    #
    # def __encoder_absence_justifiee(self):
    #     pass
    #
    # def __corriger_note(self):
    #     pass


@attr.s(frozen=True, slots=True)
class IdentiteFeuilleDeNotes(interface.EntityIdentity):
    numero_session = attr.ib(type=int)
    # code_unite_enseignement = attr.ib(type=str)
    sigle_cohorte = attr.ib(type=str)
    annee_academique = attr.ib(type=int)


class FeuilleDeNotesParFormation(interface.RootEntity):
    entity_id = attr.ib(type=IdentiteFeuilleDeNotes)
    credits_unite_enseignement = attr.ib(type=float)
    notes = attr.ib(type=Set[NoteEtudiant])  # type: Set[NoteEtudiant]

# from datetime import date
# from typing import List
#
# import attr
#
# from ddd.logic.encodage_des_notes.encodage.domain.model._note import Note
# from osis_common.ddd import interface
#
# Noma = str
#
#
# class IdentiteNoteEtudiant(interface.EntityIdentity):
#     # noma = attr.ib(type=Noma)
#     sigle_formation = attr.ib(type=str)
#     code_unite_enseignement = attr.ib(type=str)
#     annee_academique = attr.ib(type=int)
#
#
# class IdentiteNotesEtudiant(interface.EntityIdentity):
#     noma = attr.ib(type=Noma)
#     # sigle_formation = attr.ib(type=str)
#     # code_unite_enseignement = attr.ib(type=str)
#     # annee_academique = attr.ib(type=int)
#
#
# class NoteEtudiant(interface.RootEntity):
#     entity_id = attr.ib(type=IdentiteNoteEtudiant)
#     note = attr.ib(type=Note)
#     date_echeance = attr.ib(type=date)
#
#
# class NotesEtudiant(interface.RootEntity):
#     entity_id = attr.ib(type=IdentiteNotesEtudiant)
#     notes = attr.ib(type=List[NoteEtudiant])
#     # note = attr.ib(type=Note)
#     # date_echeance = attr.ib(type=date)
