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
import datetime
import functools
import operator
from typing import Optional, List

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import F, QuerySet, OuterRef, Subquery, Q, Value, Case, When
from django.db.models.expressions import RawSQL
from django.db.models.functions import Cast
from django_cte import With

from base.models.entity_version import EntityVersion
from base.models.enums import learning_container_year_types, learning_component_year_type
from base.models.learning_component_year import LearningComponentYear
from base.models.learning_unit_year import LearningUnitYear, LearningUnitYearQuerySet
from base.models.utils.func import ArrayConcat
from ddd.logic.application.domain.builder.vacant_course_builder import VacantCourseBuilder
from ddd.logic.application.domain.model.entity_allocation import EntityAllocation
from ddd.logic.application.domain.model.vacant_course import VacantCourseIdentity, VacantCourse
from ddd.logic.application.dtos import VacantCourseFromRepositoryDTO
from ddd.logic.application.repository.i_vacant_course_repository import IVacantCourseRepository


class VacantCourseRepository(IVacantCourseRepository):
    @classmethod
    def search(
            cls,
            entity_ids: Optional[List[VacantCourseIdentity]] = None,
            code: str = None,
            entity_allocation: EntityAllocation = None,
            with_entity_allocation_children: bool = False,
            **kwargs
    ) -> List[VacantCourse]:
        qs = _vacant_course_base_qs()
        if entity_allocation and with_entity_allocation_children:
            qs = _annotate_entity_allocation_parents(qs)

        if entity_ids is not None:
            filter_clause = functools.reduce(
                operator.or_,
                ((Q(code=entity_id.code) & Q(year=entity_id.year)) for entity_id in entity_ids)
            )
            qs = qs.filter(filter_clause)
        if code is not None:
            qs = qs.filter(learning_container_year__acronym__icontains=code)
        if entity_allocation and not with_entity_allocation_children:
            qs = qs.filter(entity_allocation=entity_allocation.code)
        if entity_allocation and with_entity_allocation_children:
            qs = qs.filter(
                Q(entity_allocation=entity_allocation.code)
                | Q(entity_allocation_parents__contains=[entity_allocation.code])
            )

        results = []
        for row_as_dict in qs:
            dto_from_database = VacantCourseFromRepositoryDTO(
                code=row_as_dict['code'],
                year=row_as_dict['year'],
                title=row_as_dict['title'],
                is_in_team=row_as_dict['is_in_team'],
                entity_allocation=row_as_dict['entity_allocation'],
                vacant_declaration_type=row_as_dict['vacant_declaration_type'],
                lecturing_volume_available=row_as_dict['lecturing_volume_available'],
                lecturing_volume_total=row_as_dict['lecturing_volume_total'],
                practical_volume_available=row_as_dict['practical_volume_available'],
                practical_volume_total=row_as_dict['practical_volume_total'],
            )
            results.append(VacantCourseBuilder.build_from_repository_dto(dto_from_database))
        return results

    @classmethod
    def get(cls, entity_id: 'VacantCourseIdentity') -> 'VacantCourse':
        qs = _vacant_course_base_qs().filter(
            code=entity_id.code,
            year=entity_id.year,
        )
        obj_as_dict = qs.get()
        dto_from_database = VacantCourseFromRepositoryDTO(**obj_as_dict)
        return VacantCourseBuilder.build_from_repository_dto(dto_from_database)


def _vacant_course_base_qs() -> QuerySet:
    subqs = LearningComponentYear.objects.filter(learning_unit_year_id=OuterRef('pk'))

    main_qs = LearningUnitYearQuerySet.annotate_entity_allocation_acronym(
        LearningUnitYear.objects.filter(
            learning_container_year__container_type__in=[
                learning_container_year_types.COURSE,
                learning_container_year_types.INTERNSHIP,
                learning_container_year_types.DISSERTATION
            ]
        ).annotate_full_title()
    )

    return main_qs.annotate(
            code=F('learning_container_year__acronym'),
            year=F('learning_container_year__academic_year__year'),
            title=F('full_title'),
            is_in_team=F('learning_container_year__team'),
            vacant_declaration_type=F('learning_container_year__type_declaration_vacant'),
            lecturing_volume_total=Subquery(
                subqs.filter(type=learning_component_year_type.LECTURING).values('hourly_volume_total_annual')[:1]
            ),
            lecturing_volume_available=Subquery(
                subqs.filter(type=learning_component_year_type.LECTURING).values('volume_declared_vacant')[:1]
            ),
            practical_volume_total=Subquery(
                subqs.filter(
                    type=learning_component_year_type.PRACTICAL_EXERCISES
                ).values('hourly_volume_total_annual')[:1]
            ),
            practical_volume_available=Subquery(
                subqs.filter(type=learning_component_year_type.PRACTICAL_EXERCISES).values('volume_declared_vacant')[:1]
            )
        ).values(
            "code",
            "year",
            "title",
            "is_in_team",
            "vacant_declaration_type",
            "lecturing_volume_total",
            "lecturing_volume_available",
            "practical_volume_total",
            "practical_volume_available",
            "entity_allocation"
        )


def _annotate_entity_allocation_parents(qs: QuerySet) -> QuerySet:
    def parent_entities(cte):
        return EntityVersion.objects.\
            filter(parent_id__isnull=True).\
            annotate(
                end_date_queryable=Case(
                    When(end_date__isnull=True, then=Value(datetime.date(2099, 1, 1))),
                    default=F('end_date')
                )
            ).values(
                'parent_id',
                'entity_id',
                'start_date',
                'end_date_queryable',
                'acronym',
                parents=RawSQL(
                    "array[]::text[]", [],
                    output_field=ArrayField(models.TextField()),
                )
            ).union(
                cte.join(
                    EntityVersion.objects.annotate(
                        end_date_queryable=Case(
                            When(end_date__isnull=True, then=Value(datetime.date(2099, 1, 1))),
                            default=F('end_date')
                        )
                    ),
                    parent_id=cte.col.entity_id,
                    start_date__gte=cte.col.start_date,
                    end_date_queryable__lte=cte.col.end_date_queryable
                ).values(
                    'parent_id',
                    'entity_id',
                    'start_date',
                    'end_date_queryable',
                    'acronym',
                    parents=ArrayConcat(
                        # Append the parent to the array
                        cte.col.parents,
                        Cast("acronym", models.TextField()),
                        output_field=ArrayField(models.TextField()),
                    ),
                ),
                all=True
            )

    cte = With.recursive(parent_entities)
    qs = qs.annotate(
        entity_allocation_parents=Subquery(
            cte.queryset().filter(
                start_date__lte=OuterRef('learning_container_year__academic_year__start_date'),
                end_date_queryable__gte=OuterRef('learning_container_year__academic_year__end_date'),
                entity_id=OuterRef('learning_container_year__allocation_entity_id')
            ).with_cte(cte).values('parents')[:1],
            output_field=ArrayField(models.TextField()),
        )
    )
    return qs
