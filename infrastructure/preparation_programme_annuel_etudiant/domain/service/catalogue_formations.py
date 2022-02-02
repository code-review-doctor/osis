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
from typing import List, Union

from ddd.logic.preparation_programme_annuel_etudiant.commands import GetFormationCommand
from ddd.logic.preparation_programme_annuel_etudiant.domain.service.i_catalogue_formations import \
    ICatalogueFormationsTranslator
from ddd.logic.preparation_programme_annuel_etudiant.domain.validator.exceptions import FormationIntrouvableException
from ddd.logic.preparation_programme_annuel_etudiant.dtos import FormationDTO, \
    ContenuGroupementCatalogueDTO, UniteEnseignementDTO, UniteEnseignementCatalogueDTO, GroupementCatalogueDTO
from program_management.ddd.dtos import ProgrammeDeFormationDTO, ContenuNoeudDTO, ElementType


class CatalogueFormationsTranslator(ICatalogueFormationsTranslator):
    @classmethod
    def get_formation(cls, code_programme: str, annee: int) -> 'FormationDTO':
        from infrastructure.messages_bus import message_bus_instance
        program_management_formation_dto = message_bus_instance.invoke(
            GetFormationCommand(
                annee=annee,
                code=code_programme,
            )
        )
        if program_management_formation_dto:
            return _build_formation_dto(program_management_formation_dto)
        raise FormationIntrouvableException(code_programme=code_programme, annee=annee)


def _build_formation_dto(program_management_formation_dto: ProgrammeDeFormationDTO) -> FormationDTO:
    return FormationDTO(
        racine=__build_groupement_contenu(program_management_formation_dto.racine),
        annee=program_management_formation_dto.annee,
        sigle=program_management_formation_dto.sigle,
        version=program_management_formation_dto.version,
        intitule_formation=program_management_formation_dto.intitule_formation,
    )


def __build_groupement_contenu(contenu_noeud: ContenuNoeudDTO) -> ContenuGroupementCatalogueDTO:
    return ContenuGroupementCatalogueDTO(
        groupement_contenant=GroupementCatalogueDTO(
            code=contenu_noeud.code,
            intitule=contenu_noeud.intitule,
            obligatoire=contenu_noeud.obligatoire,
            remarque=contenu_noeud.remarque,
            credits=contenu_noeud.credits,
            intitule_complet=contenu_noeud.intitule_complet,
        ),
        contenu_ordonne_catalogue=__build_contenu_ordonne_catalogue(contenu_noeud.contenu_ordonne)
    )


def __build_contenu_ordonne_catalogue(contenu_ordonne: List[Union['UniteEnseignementDTO', 'ContenuNoeudDTO']]):
    contenu_ordonne_catalogue = []
    for element in contenu_ordonne:
        if element.type == ElementType.UNITE_ENSEIGNEMENT.name:
            contenu_ordonne_catalogue.append(
                UniteEnseignementCatalogueDTO(
                    bloc=element.bloc,
                    code=element.code,
                    intitule_complet=element.intitule_complet,
                    quadrimestre=element.quadrimestre,
                    quadrimestre_texte=element.quadrimestre_texte,
                    credits_absolus=element.credits_absolus,
                    volume_annuel_pm=element.volume_annuel_pm,
                    volume_annuel_pp=element.volume_annuel_pp,
                    obligatoire=element.obligatoire,
                    credits_relatifs=element.credits_relatifs,
                    session_derogation=element.session_derogation,
                )
            )
        elif element.type == ElementType.GROUPEMENT.name:
            contenu_ordonne_catalogue.append(__build_groupement_contenu(element))
    return contenu_ordonne_catalogue
