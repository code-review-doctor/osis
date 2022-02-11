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

from ddd.logic.learning_unit.domain.model.learning_unit import LearningUnitIdentity
from ddd.logic.preparation_programme_annuel_etudiant.domain.service.i_catalogue_unites_enseignement import \
    ICatalogueUnitesEnseignementTranslator
from ddd.logic.preparation_programme_annuel_etudiant.dtos import UniteEnseignementCatalogueDTO


class CatalogueUnitesEnseignementTranslatorInMemory(ICatalogueUnitesEnseignementTranslator):
    dtos = [
        UniteEnseignementCatalogueDTO(
            bloc=1,
            code="LSINF1311",
            intitule_complet="Human-computer interaction",
            quadrimestre="Q1",
            quadrimestre_texte="Q1",
            credits_absolus=Decimal(5),
            credits_relatifs=None,
            volume_annuel_pm=30,
            volume_annuel_pp=15,
            obligatoire=True,
            session_derogation=""
        ),
        UniteEnseignementCatalogueDTO(
            bloc=1,
            code="LINGE1225",
            intitule_complet="Programmation en économie et gestion",
            quadrimestre="Q1",
            quadrimestre_texte="Q1",
            credits_absolus=Decimal(5),
            credits_relatifs=None,
            volume_annuel_pm=30,
            volume_annuel_pp=15,
            obligatoire=True,
            session_derogation=""
        )
    ]

    @classmethod
    def search(cls, entity_ids: List['LearningUnitIdentity']) -> List['UniteEnseignementCatalogueDTO']:
        codes = [entity_id.code for entity_id in entity_ids]
        return [dto for dto in cls.dtos if dto.code in codes]
