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
    ProgrammeDetailleDTO


class CatalogueFormationsTranslatorInMemory(ICatalogueFormationsTranslator):

    groupement1 = GroupementCatalogueDTO(
        inclus_dans=None,
        intitule='Groupement 1',
        obligatoire=True,
        remarque='Remarque 1',
        commentaire=None

    )
    groupement2 = GroupementCatalogueDTO(
        inclus_dans=None,
        intitule='Groupement 2',
        obligatoire=False,
        remarque='Remarque 2',
        commentaire='Commentaire 2'
    )
    programme_detaille = ProgrammeDetailleDTO(
        groupements=[groupement1, groupement2],
        unites_enseignement=[]
    )
    dtos = [
        FormationDTO(
            programme_detaille=programme_detaille,
            annee=2020,
            sigle='ECGE1BA',
            version='STANDARD',
            intitule_complet='Bachelier ...',
        ),
    ]

    @classmethod
    def get_formation(cls, sigle: str, annee: int, version: str) -> 'FormationDTO':
        return next(
            dto for dto in cls.dtos
            if dto.sigle == sigle and dto.annee == annee and dto.version == version
        )
