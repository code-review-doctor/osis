from typing import List

import attr

from osis_common.ddd import interface


@attr.s(slots=True)
class RapportNoteEtudiant(interface.EntityIdentity):
    numero_ligne = attr.ib(type=int)
    mail_etudiant = attr.ib(type=str)
    messages = attr.ib(type=str)  # plusieurs exceptions possibles par note encodée

    def __str__(self):
        return "{numero_ligne} ({email}): {message}".format(numero_ligne=self.numero_ligne, email=self.mail_etudiant, message=...)


@attr.s(slots=True)
class RapportEncodage(interface.RootEntity):
    rapports_notes_etudiant = attr.ib(type=List[RapportNoteEtudiant], default=[])

    def ajouter_messages(self, ligne_sur_feuille_de_notes: int, mail_etudiant: str, messages: List[str]):
        rapport = RapportNoteEtudiant(
            numero_ligne=ligne_sur_feuille_de_notes,
            mail_etudiant=mail_etudiant,
            messages=messages,
        )
        self.rapports_notes_etudiant.append(rapport)
