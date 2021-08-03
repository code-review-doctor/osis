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
import abc
from typing import List

import attr

from base.ddd.utils.business_validator import MultipleBusinessExceptions
from ddd.logic.encodage_des_notes.soumission.commands import EncoderFeuilleDeNotesCommand
from ddd.logic.encodage_des_notes.soumission.domain.model.feuille_de_notes import FeuilleDeNotes
from ddd.logic.encodage_des_notes.soumission.dtos import DonneesAdministrativesFeuilleDeNotesDTO
from ddd.logic.learning_unit.domain.model.learning_unit import LearningUnitIdentity
from education_group.ddd.domain.group import GroupIdentity
from education_group.ddd.domain.mini_training import MiniTrainingIdentity
from education_group.ddd.domain.training import TrainingIdentity
from osis_common.ddd import interface
from program_management.ddd.domain.program_tree_version import ProgramTreeVersionIdentity


@attr.s(frozen=True, slots=True)
class SurchargeIdentity(interface.EntityIdentity):
    position_element = attr.ib(type=str)  # "LDROI100B_2020|LDROI1001_2020|..."


@attr.s(slots=True)
class Surcharge(interface.Entity, abc.ABC):
    entity_id = attr.ib(type=SurchargeIdentity)


@attr.s(slots=True)
class SurchargeAjout(Surcharge):
    pass  # **champs_surchargeables


@attr.s(slots=True)
class SurchargeModification(Surcharge):
    pass  # **champs_surchargeables


@attr.s(slots=True)
class SurchargeSuppression(Surcharge):
    pass


@attr.s(slots=True)
class LCP(interface.RootEntity):
    entity_id = attr.ib(type=ProgramTreeVersionIdentity)
    elements_ajoutes = attr.ib(type=List[SurchargeAjout])
    elements_modifies = attr.ib(type=List[SurchargeModification])
    elements_supprimes = attr.ib(type=List[SurchargeSuppression])


# ----------------------------------------------------------------------------------------------------------------------


@attr.s(frozen=True, slots=True)
class ElementDTO(interface.DTO):
    position = attr.ib(type=str)  # chemin_access == path == "LDROI100B_2020|LDROI1001_2020|..."
    code = attr.ib(type=str)
    annee = attr.ib(type=int)
    type = attr.ib(type=str)  # Formation, miniformation, groupement, cours
    intitule_abrege = attr.ib(type=str)
    intitule_complet = attr.ib(type=str)
    # ... autres champs nécessaire à afficher dans l'arbre ?


@attr.s(frozen=True, slots=True)
class ProgramTreeDTO(interface.DTO):
    racine = attr.ib(type=ElementDTO)
    elements = attr.ib(type=List[ElementDTO])


@attr.s(frozen=True, slots=True)
class TrainingDTO(interface.DTO):
    code = attr.ib(type=str)  # à valider ?
    annee = attr.ib(type=int)
    intitule_abrege = attr.ib(type=str)  # ou sigle ?
    intitule_complet = attr.ib(type=str)
    # ... autres champs nécessaire à afficher dans l'arbre ?


@attr.s(frozen=True, slots=True)
class MiniTrainingDTO(interface.DTO):
    code = attr.ib(type=str)  # à valider ?
    annee = attr.ib(type=int)
    intitule_abrege = attr.ib(type=str)  # ou sigle ?
    intitule_complet = attr.ib(type=str)
    # ... autres champs nécessaire à afficher dans l'arbre ?


@attr.s(frozen=True, slots=True)
class GroupementDTO(interface.DTO):
    code = attr.ib(type=str)
    annee = attr.ib(type=int)
    intitule_complet = attr.ib(type=str)
    # ... autres champs nécessaire à afficher dans l'arbre ?


@attr.s(frozen=True, slots=True)
class UniteEnseignementDTO(interface.DTO):
    # TODO :: à vérifier si existe déjà ?
    code = attr.ib(type=str)
    annee = attr.ib(type=int)
    intitule_complet = attr.ib(type=str)
    # ... autres champs nécessaire à afficher dans l'arbre ?


# ----------------------------------------------------------------------------------------------------------------------


class ContenuProgrammeType(interface.DomainService):

    @classmethod
    def get(cls, identity: 'ProgramTreeVersionIdentity') -> 'ProgramTreeDTO':
        # Devrait convertir liste de NodeIdentity en TrainingIdentity / miniTrainingIdentity / GroupIdentity / LearningUnitIdentity
        # pour réutiliser les services TrainingDetail, MiniTrainingDetail ...
        raise NotImplementedError

    @classmethod
    def get_details_elements(cls, valeurs: Set[Tuple[Code, Annee, Type]]) -> List['ElementDTO']:
        if type == 'TRAINING':
            # training = TrainingDetail().get()
            pass
        elif type == 'MINI_TRAINING':
            # mini_training = MiniTrainingDetail().get()
            pass
        elif type == 'GROUP':
            # groupement = GroupementDetail().get()
            pass
        elif type == 'UNITE_ENSEIGNEMENT':
            # unite_enseignement = MiniTrainingDetail().get()
            pass
        raise NotImplementedError


class TrainingDetail(interface.DomainService):
    @classmethod
    def get(cls, identity: 'TrainingIdentity') -> 'TrainingDTO':
        raise NotImplementedError

    @classmethod
    def search(cls, identities: List['TrainingIdentity']) -> List['TrainingDTO']:
        raise NotImplementedError


class MiniTrainingDetail(interface.DomainService):
    @classmethod
    def get(cls, identity: 'MiniTrainingIdentity') -> 'MiniTrainingDTO':
        raise NotImplementedError

    @classmethod
    def search(cls, identities: List['MiniTrainingIdentity']) -> List['MiniTrainingDTO']:
        raise NotImplementedError


class GroupementDetail(interface.DomainService):
    @classmethod
    def get(cls, identity: 'GroupIdentity') -> 'GroupementDTO':
        raise NotImplementedError

    @classmethod
    def search(cls, identities: List['GroupIdentity']) -> List['GroupementDTO']:
        raise NotImplementedError


class UniteEnseignementDetail(interface.DomainService):
    @classmethod
    def get(cls, code: str, year: int) -> 'UniteEnseignementDetail':
        raise NotImplementedError

    @classmethod
    def search(cls, identities: List['LearningUnitIdentity']) -> List['UniteEnseignementDetail']:
        raise NotImplementedError
