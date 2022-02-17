##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2022 Université catholique de Louvain (http://www.uclouvain.be)
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
from decimal import Decimal
from typing import List, Union, Optional

import attr

from osis_common.ddd.interface import DTO

UNITE_ENSEIGNEMENT = 'UNITE_ENSEIGNEMENT'
GROUPEMENT = 'GROUPEMENT'


@attr.s(frozen=True, slots=True, auto_attribs=True)
class UniteEnseignementDTO(DTO):
    bloc: int
    code: str
    intitule_complet: str
    quadrimestre: str
    quadrimestre_texte: str
    credits_absolus: Decimal
    volume_annuel_pm: int
    volume_annuel_pp: int
    obligatoire: bool
    session_derogation: str
    credits_relatifs: int
    chemin_acces: str  # Exemple : 'LDROI1001B|LDROI102C|LDROI1001
    ajoutee: bool = attr.ib(default=False)

    @property
    def type(self):
        return UNITE_ENSEIGNEMENT


@attr.s(frozen=True, slots=True, auto_attribs=True)
class GroupementDTO(DTO):
    intitule: str
    intitule_complet: str
    obligatoire: bool
    chemin_acces: str  # Exemple : 'LDROI1001B|LDROI102C|LDROI1001

    @property
    def type(self):
        return GROUPEMENT


@attr.s(frozen=True, slots=True, auto_attribs=True)
class ContenuGroupementDTO(DTO):
    groupement_contenant: GroupementDTO
    contenu: List[Union['UniteEnseignementDTO', 'ContenuGroupementDTO']]


@attr.s(frozen=True, slots=True, auto_attribs=True)
class FormulaireInscriptionCoursDTO(DTO):
    annee_formation: int
    sigle_formation: str
    version_formation: str
    intitule_formation: str
    racine: ContenuGroupementDTO


@attr.s(frozen=True, slots=True, auto_attribs=True)
class UniteEnseignementCatalogueDTO(DTO):
    bloc: int
    code: str
    intitule_complet: str
    quadrimestre: str
    quadrimestre_texte: str
    credits_absolus: Decimal
    credits_relatifs: Optional[int]
    volume_annuel_pm: Optional[int]
    volume_annuel_pp: Optional[int]
    obligatoire: bool
    session_derogation: str


@attr.s(frozen=True, slots=True, auto_attribs=True)
class GroupementCatalogueDTO(DTO):
    # groupement provenant du catalogue (sans surcharge d'ajout, suppression ou modification)
    code: str
    intitule: str
    obligatoire: bool
    remarque: str
    credits: Decimal
    intitule_complet: str


# FIXME: Rename to GroupementCatalogueDTO
@attr.s(frozen=True, slots=True, auto_attribs=True)
class ContenuGroupementCatalogueDTO(DTO):
    # groupement provenant du catalogue (sans surcharge d'ajout, suppression ou modification)
    groupement_contenant: GroupementCatalogueDTO
    contenu_ordonne_catalogue: List[Union['UniteEnseignementCatalogueDTO', 'ContenuGroupementCatalogueDTO']]


@attr.s(frozen=True, slots=True, auto_attribs=True)
class FormationDTO(DTO):
    racine: ContenuGroupementCatalogueDTO
    annee: int
    sigle: str
    version: str
    transition_name: str
    intitule_formation: str


@attr.s(frozen=True, slots=True, auto_attribs=True)
class ProgrammeInscriptionCoursDTO(DTO):
    uuid: str
    code: str
    sigle: str
    annee: int
    version: str
    transition_name: str
    intitule_complet_formation: str  # intitulé de la formation + version formation
    racine: 'GroupementInscriptionCoursDTO'

    @property
    def title(self):
        title = self.sigle
        if self.version and self.transition_name:
            title += "[{} - {}]".format(self.version, self.transition_name)
        elif self.version:
            title += "[{}]".format(self.version)
        elif self.transition_name:
            title += "[{}]".format(self.transition_name)
        return title


@attr.s(frozen=True, slots=True, auto_attribs=True)
class GroupementInscriptionCoursDTO(DTO):
    intitule_complet: str
    obligatoire: bool
    code: str
    unites_enseignement_ajoutees: List['UniteEnseignementAjouteeDTO']
    #  Comment because nominal case (program without adjustment) only for now
    # unites_enseignement_supprimees: List['UniteEnseignementSupprimeeDTO']
    # unites_enseignement_modifiees: List['UniteEnseignementModifieeDTO']
    # unites_enseignements: List['UniteEnseignementProgrammeDTO']
    contenu: List[Union['UniteEnseignementProgrammeDTO', 'GroupementInscriptionCoursDTO']]

    @property
    def type(self):
        return GROUPEMENT


@attr.s(frozen=True, slots=True, auto_attribs=True)
class UniteEnseignementProgrammeDTO(DTO):
    code: str
    intitule: str
    obligatoire: bool
    bloc: int

    @property
    def type(self):
        return '%s' % UNITE_ENSEIGNEMENT


@attr.s(frozen=True, slots=True, auto_attribs=True)
class UniteEnseignementAjouteeDTO(DTO):
    code: str
    intitule: str
    obligatoire: bool
    bloc: int
    a_la_suite_de: str


@attr.s(frozen=True, slots=True, auto_attribs=True)
class UniteEnseignementModifieeDTO(DTO):
    code: str
    #  TODO: champs éditables


@attr.s(frozen=True, slots=True, auto_attribs=True)
class UniteEnseignementSupprimeeDTO(DTO):
    code: str


@attr.s(frozen=True, slots=True, auto_attribs=True)
class GroupementAjusteFromRepositoryDTO(DTO):
    code_programme: str
    annee: int
    version_programme: str
    nom_transition: str
    code_groupement: str
    unites_enseignement_ajoutees: List['UniteEnseignementAjouteeDTO']
    #  Comment because nominal case (program without adjustment) only for now
    # unites_enseignement_supprimees: List['UniteEnseignementSupprimeeDTO']
    # unites_enseignement_modifiees: List['UniteEnseignementModifieeDTO']


@attr.s(frozen=True, slots=True, auto_attribs=True)
class GroupementContenantDTO(DTO):
    intitule: str
    intitule_complet: str
    elements_contenus: List[Union['UniteEnseignementContenueDTO', 'GroupementContenuDTO']]


@attr.s(frozen=True, slots=True, auto_attribs=True)
class UniteEnseignementContenueDTO(DTO):
    code: str
    intitule_complet: str
    obligatoire: bool

    volume_annuel_pm: int
    volume_annuel_pp: int
    bloc: Optional[int]
    quadrimestre_texte: str
    credits_absolus: Decimal
    credits_relatifs: int
    session_derogation: str

    ajoute: bool = attr.ib(default=False)
    modifie: bool = attr.ib(default=False)
    supprime: bool = attr.ib(default=False)

    @property
    def type(self):
        return UNITE_ENSEIGNEMENT

    @property
    def is_modifie(self):
        return self.modifie


@attr.s(frozen=True, slots=True, auto_attribs=True)
class GroupementContenuDTO(DTO):
    code: str
    intitule_complet: str
    obligatoire: bool

    @property
    def type(self):
        return GROUPEMENT
