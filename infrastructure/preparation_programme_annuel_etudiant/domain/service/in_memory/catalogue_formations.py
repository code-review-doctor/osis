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
from ddd.logic.preparation_programme_annuel_etudiant.domain.service.i_catalogue_formations import \
    ICatalogueFormationsTranslator
from ddd.logic.preparation_programme_annuel_etudiant.dtos import FormationDTO, GroupementCatalogueDTO, \
    ProgrammeDetailleDTO, UniteEnseignementCatalogueDTO


class CatalogueFormationsTranslatorInMemory(ICatalogueFormationsTranslator):

    groupement_1 = GroupementCatalogueDTO(
        inclus_dans=None,
        intitule='Content:',
        obligatoire=True,
        remarque='Remarque 1',
        informations_principales_agregees="{} ({} crédits) ".format('Content:', 150)
    )
    dtos = [
        FormationDTO(
            programme_detaille=ProgrammeDetailleDTO(
                groupements=[
                    groupement_1,
                    GroupementCatalogueDTO(
                        inclus_dans=None,
                        intitule='Groupement 2',
                        obligatoire=False,
                        remarque='Remarque 2',
                        informations_principales_agregees="{} ({} crédits) ".format('Groupement 2', 150)
                    )
                ],
                unites_enseignement=[
                    UniteEnseignementCatalogueDTO(
                        inclus_dans=groupement_1,
                        bloc=1,
                        code='LESPO1113',
                        intitule_complet='Sociologie et anthropologie des mondes contemporains',
                        quadrimestre='Q1 ou Q2',
                        credits_absolus=5,
                        volume_annuel_pm=40,
                        volume_annuel_pp=0,
                        obligatoire=True,
                        informations_principales_agregees='LESPO1113 Philosophie [30h + 0h] (5 crédits)'
                    )
                ]
            ),
            annee=2021,
            sigle='ECGE1BA',
            version='STANDARD',
            intitule_complet='Bachelier en sciences économiques et de gestion',
        ),
    ]

    @classmethod
    def get_formation(cls, sigle: str, annee: int, version: str, transition: str) -> 'FormationDTO':
        return next(
            dto for dto in cls.dtos
            if dto.sigle == sigle and dto.annee == annee and dto.version == version and dto.transition == transition
        )
