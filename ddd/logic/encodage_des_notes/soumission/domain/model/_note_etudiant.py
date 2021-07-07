from datetime import date

import attr

from ddd.logic.encodage_des_notes.soumission.domain.model._note import Note
from osis_common.ddd import interface

Noma = str


class IdentiteNoteEtudiant(interface.EntityIdentity):
    noma = attr.ib(type=Noma)


class NoteEtudiant(interface.Entity):
    entity_id = attr.ib(type=IdentiteNoteEtudiant)
    note = attr.ib(type=Note)
    date_limite_de_remise = attr.ib(type=date)
    est_soumise = attr.ib(type=bool)
