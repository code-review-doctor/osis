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


class CatalogueFormationsInMemoryTranslator(ICatalogueFormationsTranslator):
    dtos = [
        FormationDTO(
            racine=ContenuGroupementCatalogueDTO(
                groupement_contenant=GroupementCatalogueDTO(
                    intitule='Content:',
                    obligatoire=True,
                    remarque='',
                    credits=Decimal(0),
                    intitule_complet='Content:',
                    code='LECGE100T'
                ),
                unites_enseignement_contenues=[
                    UniteEnseignementCatalogueDTO(
                        bloc=1,
                        code='LESPO1113',
                        intitule_complet='Sociologie et anthropologie des mondes contemporains',
                        quadrimestre='Q1',
                        quadrimestre_texte='Q1',
                        credits_absolus=Decimal(0),
                        credits_relatifs=0,
                        volume_annuel_pm=0,
                        volume_annuel_pp=0,
                        obligatoire=True,
                        session_derogation='',
                    )
                ],
                groupements_contenus=[],
            ),
            annee=2021,
            sigle='ECGE1BA',
            version='',
            intitule_complet='Bachelier en sciences économiques et de gestion',
        ),
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
