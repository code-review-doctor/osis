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
from typing import List

from base.models.enums.quadrimesters import LearningUnitYearQuadrimester
from ddd.logic.learning_unit.commands import LearningUnitSearchCommand
from ddd.logic.learning_unit.domain.model.learning_unit import LearningUnitIdentity
from ddd.logic.learning_unit.dtos import LearningUnitSearchDTO
from ddd.logic.preparation_programme_annuel_etudiant.domain.service.i_catalogue_unites_enseignement import \
    ICatalogueUnitesEnseignementTranslator
from ddd.logic.preparation_programme_annuel_etudiant.dtos import UniteEnseignementCatalogueDTO


class CatalogueUnitesEnseignementTranslator(ICatalogueUnitesEnseignementTranslator):
    @classmethod
    def search(cls, entity_ids: List['LearningUnitIdentity']) -> List['UniteEnseignementCatalogueDTO']:
        if not entity_ids:
            return []
        from infrastructure.messages_bus import message_bus_instance
        unites_enseignement_dto = message_bus_instance.invoke(
            LearningUnitSearchCommand(
                code_annee_values=[(entity_id.code, entity_id.year) for entity_id in entity_ids]
            )
        )

        return [
            cls._convert_learning_unit_search_dto_to_unite_enseignement_catalogue_dto(dto)
            for dto in unites_enseignement_dto
        ]

    @classmethod
    def _convert_learning_unit_search_dto_to_unite_enseignement_catalogue_dto(
            cls,
            learning_unit_search_dto: 'LearningUnitSearchDTO'
            ) -> 'UniteEnseignementCatalogueDTO':
        return UniteEnseignementCatalogueDTO(
            bloc=1,
            code=learning_unit_search_dto.code,
            intitule_complet=learning_unit_search_dto.full_title,
            quadrimestre=learning_unit_search_dto.quadrimester,
            quadrimestre_texte=LearningUnitYearQuadrimester[learning_unit_search_dto.quadrimester].value,
            credits_absolus=learning_unit_search_dto.credits,
            credits_relatifs=learning_unit_search_dto.credits,
            volume_annuel_pm=learning_unit_search_dto.lecturing_volume_annual,
            volume_annuel_pp=learning_unit_search_dto.practical_volume_annual,
            obligatoire=True,
            session_derogation=learning_unit_search_dto.session_derogation
        )
