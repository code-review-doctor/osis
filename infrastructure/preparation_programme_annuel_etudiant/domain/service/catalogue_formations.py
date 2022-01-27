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
from typing import List, Optional

from ddd.logic.preparation_programme_annuel_etudiant.commands import GetFormationCommand
from ddd.logic.preparation_programme_annuel_etudiant.domain.service.i_catalogue_formations import \
    ICatalogueFormationsTranslator
from ddd.logic.preparation_programme_annuel_etudiant.dtos import FormationDTO, GroupementDTO
from ddd.logic.preparation_programme_annuel_etudiant.dtos import GroupementCatalogueDTO, \
    ContenuGroupementCatalogueDTO, UniteEnseignementDTO, UniteEnseignementCatalogueDTO
from program_management.ddd.dtos import ProgrammeDeFormationDTO, ContenuNoeudDTO


def build_formation_dto(program_management_formation_dto: ProgrammeDeFormationDTO) -> FormationDTO:
    racine = build_contenu(program_management_formation_dto.racine)
    return FormationDTO(
        racine=racine,
        annee=program_management_formation_dto.annee,
        sigle=program_management_formation_dto.sigle,
        version=program_management_formation_dto.version,
        intitule_complet=program_management_formation_dto.intitule_version_programme,
    )


class CatalogueFormationsTranslator(ICatalogueFormationsTranslator):
    @classmethod
    def get_formation(cls, sigle: str, annee: int, version: str, transition_name: str) -> Optional['FormationDTO']:
        from infrastructure.messages_bus import message_bus_instance
        program_management_formation_dto = message_bus_instance.invoke(
            GetFormationCommand(
                annee=annee,
                code=sigle,
                version=version,
                transition=transition_name
            )
        )
        if program_management_formation_dto:
            return build_formation_dto(program_management_formation_dto)
        return None

    @classmethod
    def get_groupement(
            cls,
            sigle_formation: str,
            annee: int,
            version_formation: str,
            code_groupement: str
    ) -> 'GroupementDTO':
        raise NotImplementedError()


def build_contenu(contenu_noeud: ContenuNoeudDTO) -> ContenuGroupementCatalogueDTO:
    groupements_contenus = []

    for groupement_contenu in contenu_noeud.groupements_contenus:
        contenu_groupement_catalog = build_contenu(groupement_contenu)
        groupements_contenus.append(contenu_groupement_catalog)

    return construire_contenu_groupement_catalogue_dto(
        contenu_noeud,
        groupements_contenus,
        contenu_noeud.unites_enseignement_contenues,
    )


def construire_contenu_groupement_catalogue_dto(
        contenu_noeud: ContenuNoeudDTO,
        groupements_contenus: List[ContenuGroupementCatalogueDTO],
        unites_enseignement_contenues: List[UniteEnseignementDTO]) -> ContenuGroupementCatalogueDTO:

    groupement_catalogue_dto = _convertir_contenu_noeud_dto_en_groupement_catalogue_dto(contenu_noeud)
    unites_enseignement_contenues_dto = _convertir_unites_enseignement_contenues_en_unites_enseignement_catalogue_dto(
        unites_enseignement_contenues
    )
    return ContenuGroupementCatalogueDTO(
        groupement_contenant=groupement_catalogue_dto,
        groupements_contenus=groupements_contenus,
        unites_enseignement_contenues=unites_enseignement_contenues_dto
    )


def _convertir_contenu_noeud_dto_en_groupement_catalogue_dto(contenu_noeud: ContenuNoeudDTO) -> GroupementCatalogueDTO:
    return GroupementCatalogueDTO(
        code=contenu_noeud.groupement_contenant.code,
        intitule=contenu_noeud.groupement_contenant.intitule,
        obligatoire=contenu_noeud.groupement_contenant.obligatoire,
        remarque=contenu_noeud.groupement_contenant.remarque,
        credits=contenu_noeud.groupement_contenant.credits,
        intitule_complet=contenu_noeud.groupement_contenant.intitule_complet,
    )


def _convertir_unites_enseignement_contenues_en_unites_enseignement_catalogue_dto(
        unites_enseignement_contenues: List['UniteEnseignementDTO']) -> List['UniteEnseignementCatalogueDTO']:
    unites_enseignement_catalogue_dto = []
    for unite_enseignement_contenue in unites_enseignement_contenues:
        unites_enseignement_catalogue_dto.append(
            UniteEnseignementCatalogueDTO(
                bloc=unite_enseignement_contenue.bloc,
                code=unite_enseignement_contenue.code,
                intitule_complet=unite_enseignement_contenue.intitule_complet,
                quadrimestre=unite_enseignement_contenue.quadrimestre,
                quadrimestre_texte=unite_enseignement_contenue.quadrimestre_texte,
                credits_absolus=unite_enseignement_contenue.credits_absolus,
                volume_annuel_pm=unite_enseignement_contenue.volume_annuel_pm,
                volume_annuel_pp=unite_enseignement_contenue.volume_annuel_pp,
                obligatoire=unite_enseignement_contenue.obligatoire,
                credits_relatifs=unite_enseignement_contenue.credits_relatifs,
                session_derogation=unite_enseignement_contenue.session_derogation,
            )
        )
    return unites_enseignement_catalogue_dto
