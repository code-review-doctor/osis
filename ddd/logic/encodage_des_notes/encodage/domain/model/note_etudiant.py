from datetime import date

import attr

from ddd.logic.encodage_des_notes.encodage.domain.model._note import Note
from osis_common.ddd import interface

Noma = str


class IdentiteNoteEtudiant(interface.EntityIdentity):
    noma = attr.ib(type=Noma)
    sigle_formation = attr.ib(type=str)
    code_unite_enseignement = attr.ib(type=str)
    annee_academique = attr.ib(type=int)


class NotesEtudiant(interface.RootEntity):
    entity_id = attr.ib(type=IdentiteNoteEtudiant)
    note = attr.ib(type=Note)
    date_echeance = attr.ib(type=date)

    def encoder(self, note: str) -> None:
        raise NotImplementedError


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
