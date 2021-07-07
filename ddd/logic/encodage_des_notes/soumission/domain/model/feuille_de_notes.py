from typing import Set

import attr

from ddd.logic.encodage_des_notes.soumission.domain.model._note_etudiant import NoteEtudiant
from osis_common.ddd import interface


class IdentiteFeuilleDeNotes(interface.EntityIdentity):
    numero_session = attr.ib(type=int)
    code_unite_enseignement = attr.ib(type=str)
    annee_academique = attr.ib(type=int)


class FeuilleDeNotes(interface.RootEntity):
    entity_id = attr.ib(type=IdentiteFeuilleDeNotes)
    notes = attr.ib(type=Set[NoteEtudiant])

    def encoder_note(
            self,
            noma_etudiant: str,
            note: str,
    ) -> None:
        # TODO :: builder pour créer objet Note
        raise NotImplementedError

    def soumettre(self) -> None:
        # itérer sur notes et les passer en "soumises = True"
        raise NotImplementedError
