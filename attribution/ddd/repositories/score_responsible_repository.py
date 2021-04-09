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
from typing import Optional, List

from django.db.models import F

from attribution.models.attribution_charge_new import AttributionChargeNew
from ddd.logic.attribution.dtos import ScoreResponsibleRepositoryDTO
from osis_common.ddd import interface
from osis_common.ddd.interface import EntityIdentity, Entity


class ScoreResponsibleRepository(interface.AbstractRepository):
    @classmethod
    def create(cls, entity: Entity, **_) -> EntityIdentity:
        raise NotImplementedError

    @classmethod
    def update(cls, entity: Entity, **_) -> EntityIdentity:
        raise NotImplementedError

    @classmethod
    def get(cls, entity_id: EntityIdentity) -> Entity:
        raise NotImplementedError

    @classmethod
    def search(cls, entity_ids: Optional[List[EntityIdentity]] = None, **kwargs) -> List[Entity]:
        raise NotImplementedError

    @classmethod
    def delete(cls, entity_id: EntityIdentity, **_) -> None:
        raise NotImplementedError

    @classmethod
    def search_scores_responsibles_dto(
            cls,
            code: str = None,
            year: int = None,
    ) -> List['ScoreResponsibleRepositoryDTO']:

        qs = AttributionChargeNew.objects.filter(score_responsible=True).select_related('learning_component_year', 'attribution')

        if code is not None:
            qs = qs.filter(
                learning_component_year__learning_unit_year__acronym=code,
            )
        if year is not None:
            qs = qs.filter(
                learning_component_year__learning_unit_year__academic_year__year=year,
            )

        qs = qs.annotate(
            code=F('learning_component_year__learning_unit_year__acronym'),
            year=F('learning_component_year__learning_unit_year__academic_year__year'),
            last_name=F('attribution__tutor__person__last_name'),
            first_name=F('attribution__tutor__person__first_name'),
            email=F('attribution__tutor__person__email'),
        ).values(
            "year",
            "code",
            "last_name",
            "first_name",
            "email",
        )
        # ici distinct?
        result = []
        for data_dict in qs.values():
            result.append(ScoreResponsibleRepositoryDTO(**data_dict))
        return result
