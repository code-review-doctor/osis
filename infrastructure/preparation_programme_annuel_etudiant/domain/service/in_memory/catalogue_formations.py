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

from ddd.logic.preparation_programme_annuel_etudiant.domain.service.i_catalogue_formations import \
    ICatalogueFormationsTranslator
from ddd.logic.preparation_programme_annuel_etudiant.dtos import FormationDTO, ContenuGroupementCatalogueDTO, \
    GroupementDTO, GroupementCatalogueDTO, UniteEnseignementCatalogueDTO
from program_management.ddd.domain.program_tree_version import STANDARD

ANNEE = 2021


def _cas_nominal_formation_version_standard():
    SIGLE = 'ECGE1BA'
    groupement = GroupementCatalogueDTO(
        intitule=SIGLE,
        obligatoire=True,
        remarque='Remarque',
        credits=Decimal(10),
        intitule_complet='Bachelier en sciences économiques et de gestion',
    )
    return FormationDTO(
        racine=ContenuGroupementCatalogueDTO(
            groupement_contenant=groupement,
            groupements_contenus=[
                ContenuGroupementCatalogueDTO(
                    groupement_contenant=groupement,
                    groupements_contenus=[
                        ContenuGroupementCatalogueDTO(
                            groupement_contenant=GroupementCatalogueDTO(
                                intitule='Contenu :',
                                obligatoire=True,
                                remarque='Remarque',
                                credits=Decimal(10),
                                intitule_complet='Contenu :',
                            ),
                            groupements_contenus=[],
                            unites_enseignement_contenues=[
                                UniteEnseignementCatalogueDTO(
                                    bloc=1,
                                    code='LESPO1113',
                                    intitule_complet='Sociologie et anthropologie des mondes contemporains',
                                    quadrimestre='Q1or2',
                                    credits_absolus=Decimal(5),
                                    volume_annuel_pm=40,
                                    volume_annuel_pp=0,
                                    obligatoire=False,
                                    credits_relatifs=None,
                                    session_derogation='',
                                    quadrimestre_texte='Q1 ou Q2'
                                )
                            ]
                        )],
                    unites_enseignement_contenues=[]
                )
            ],
            unites_enseignement_contenues=[]
        ),
        annee=ANNEE,
        sigle=SIGLE,
        version=STANDARD,
        intitule_formation='Bachelier en sciences économiques et de gestion'
    )


def _cas_formation_version_particuliere():
    SIGLE = 'CORP2MS/CS'
    groupement = GroupementCatalogueDTO(
        intitule=SIGLE,
        obligatoire=True,
        remarque='Remarque',
        credits=Decimal(10),
        intitule_complet='Master [120] en communication[ Double diplôme UCLouvain - uSherbrooke ]',
    )
    return FormationDTO(
        racine=ContenuGroupementCatalogueDTO(
            groupement_contenant=groupement,
            groupements_contenus=[
                ContenuGroupementCatalogueDTO(
                    groupement_contenant=groupement,
                    groupements_contenus=[
                        ContenuGroupementCatalogueDTO(
                            groupement_contenant=GroupementCatalogueDTO(
                                intitule='Tronc commun',
                                obligatoire=True,
                                remarque='Remarque',
                                credits=Decimal(10),
                                intitule_complet='Tronc commun',
                            ),
                            groupements_contenus=[],
                            unites_enseignement_contenues=[
                                UniteEnseignementCatalogueDTO(
                                    bloc=2,
                                    code='LCOMU2904B',
                                    intitule_complet="Séminaire d'accompagnement au mémoire : méthodologie",
                                    quadrimestre='Q2',
                                    credits_absolus=Decimal(20),
                                    volume_annuel_pm=0,
                                    volume_annuel_pp=0,
                                    obligatoire=False,
                                    credits_relatifs=None,
                                    session_derogation='',
                                    quadrimestre_texte='Q2'
                                )
                            ]
                        )],
                    unites_enseignement_contenues=[]
                )
            ],
            unites_enseignement_contenues=[]
        ),
        annee=ANNEE,
        sigle=SIGLE,
        version='DDSHERBROOKE',
        intitule_formation='Master [120] en communication[ Double diplôme UCLouvain - uSherbrooke ]',
    )


class CatalogueFormationsTranslatorInMemory(ICatalogueFormationsTranslator):
    groupement_ECGE1BA = GroupementCatalogueDTO(
        intitule='ECGE1BA',
        obligatoire=True,
        remarque='Remarque',
        credits=10,
        intitule_complet='Bachelier en sciences économiques et de gestion ',
    )

    dtos = [
        _cas_nominal_formation_version_standard(),
        _cas_formation_version_particuliere()
    ]

    @classmethod
    def get_formation(cls, sigle: str, annee: int, version: str, transition_name: str) -> 'FormationDTO':
        return next(
            dto for dto in cls.dtos
            if dto.sigle == sigle and dto.annee == annee and dto.version == version
        )

    @classmethod
    def get_groupement(
            cls,
            sigle_formation: str,
            annee: int,
            version_formation: str,
            code_groupement: str
    ) -> 'GroupementDTO':
        raise NotImplementedError()
