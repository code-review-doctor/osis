from typing import List

import attr

from osis_common.ddd import interface

CodeGroupement = str


@attr.s(frozen=True, slots=True, auto_attribs=True)
class GroupementIdentity(interface.EntityIdentity):
    code: CodeGroupement


@attr.s(slots=True, auto_attribs=True)
class Groupement(interface.Entity):
    inclus_dans: List['Groupement']
