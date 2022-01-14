from typing import Union

import attr

from ddd.logic.preparation_programme_annuel_etudiant.domain.model.chemin_acces import CheminAcces
from ddd.logic.preparation_programme_annuel_etudiant.domain.model.groupement import Groupement
from osis_common.ddd import interface

CodeUniteEnseignement = str
CodeGroupement = str


@attr.s(frozen=True, slots=True, auto_attribs=True)
class UniteEnseignementIdentity(interface.EntityIdentity):
    chemin_acces: CheminAcces  # Exemple : 'LDROI1001B|LDROI102C|LDROI1001


@attr.s(slots=True, auto_attribs=True)
class UniteEnseignement(interface.Entity):
    entity_id: UniteEnseignementIdentity
    code: CodeUniteEnseignement
    inclus_dans: Groupement


@attr.s(slots=True, auto_attribs=True)
class UniteEnseignementAjoutee(interface.Entity):
    entity_id: UniteEnseignementIdentity
    a_la_suite_de: Union[CodeUniteEnseignement, CodeGroupement]


@attr.s(slots=True, auto_attribs=True)
class UniteEnseignementRetiree(interface.Entity):
    entity_id: UniteEnseignementIdentity


@attr.s(slots=True, auto_attribs=True)
class UniteEnseignementAjustee(interface.Entity):
    entity_id: UniteEnseignementIdentity
