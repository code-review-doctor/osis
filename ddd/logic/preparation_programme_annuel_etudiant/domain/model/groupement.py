from typing import List

import attr

from ddd.logic.preparation_programme_annuel_etudiant.domain.model.chemin_acces import CheminAcces
from osis_common.ddd import interface

CodeGroupement = str


@attr.s(frozen=True, slots=True, auto_attribs=True)
class GroupementIdentity(interface.EntityIdentity):
    chemin_acces: CheminAcces  # Exemple : 'LDROI1001B|LDROI102C|LDROI1001'


@attr.s(slots=True, auto_attribs=True)
class Groupement(interface.Entity):
    entity_id: GroupementIdentity
    inclus_dans: List['Groupement']

    @property
    def code(self) -> str:
        return self.entity_id.chemin_acces.dernier_element
