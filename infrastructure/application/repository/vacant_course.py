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
from decimal import Decimal
from typing import List, Optional

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import F, QuerySet, OuterRef, Subquery, Q, Value, Case, When, fields
from django.db.models.expressions import RawSQL
from django.db.models.functions import Cast
from django_cte import With

from attribution.models.attribution_charge_new import AttributionChargeNew
from attribution.models.attribution_new import AttributionNew
from base.models.entity_version import EntityVersion
from base.models.enums import learning_container_year_types, learning_component_year_type
from base.models.enums.vacant_declaration_type import VacantDeclarationType
from base.models.learning_component_year import LearningComponentYear
from base.models.learning_unit_year import LearningUnitYear, LearningUnitYearQuerySet
from base.models.utils.func import ArrayConcat
from ddd.logic.application.domain.builder.vacant_course_builder import VacantCourseBuilder
from ddd.logic.application.domain.model.vacant_course import VacantCourseIdentity, VacantCourse
from ddd.logic.application.dtos import VacantCourseFromRepositoryDTO, VacantCourseSearchDTO, \
    TutorAttributionFromRepositoryDTO, TutorAttributionDTO
from ddd.logic.application.repository.i_vacant_course_repository import IVacantCourseRepository
from ddd.logic.shared_kernel.academic_year.domain.model.academic_year import AcademicYearIdentity


class VacantCourseRepository(IVacantCourseRepository):
    @classmethod
    def search(cls, entity_ids: Optional[List[VacantCourseIdentity]] = None, **kwargs) -> List[VacantCourse]:
        qs = _vacant_course_base_qs()
        if entity_ids is not None:
            filter_clause = functools.reduce(
                operator.or_,
                ((Q(code=entity_id.code) & Q(year=entity_id.year)) for entity_id in entity_ids)
            )
            qs = qs.filter(filter_clause)

        results = []
        for obj_as_dict in qs:
            dto_from_database = VacantCourseFromRepositoryDTO(**obj_as_dict)
            results.append(VacantCourseBuilder.build_from_repository_dto(dto_from_database))
        return results

    @classmethod
    def search_vacant_course_dto(
            cls,
            code: str = None,
            academic_year_id: AcademicYearIdentity = None,
            allocation_entity_code: str = None,
            with_allocation_entity_children: bool = False,
            vacant_declaration_types: List[VacantDeclarationType] = None,
            **kwargs
    ) -> List[VacantCourseSearchDTO]:
        qs = _vacant_course_base_qs()
        if allocation_entity_code and with_allocation_entity_children:
            qs = _annotate_allocation_entity_parents(qs)

        if code is not None:
            qs = qs.filter(learning_container_year__acronym__icontains=code)
        if academic_year_id is not None:
            qs = qs.filter(learning_container_year__academic_year__year=academic_year_id.year)
        if vacant_declaration_types is not None:
            qs = qs.filter(
                learning_container_year__type_declaration_vacant__in=[enum.name for enum in vacant_declaration_types]
            )
        if allocation_entity_code and not with_allocation_entity_children:
            qs = qs.filter(allocation_entity=allocation_entity_code)
        if allocation_entity_code and with_allocation_entity_children:
            qs = qs.filter(
                Q(allocation_entity=allocation_entity_code)
                | Q(allocation_entity_parents__contains=[allocation_entity_code])
            )

        tutors_attributions = _prefetch_tutors_attributions(qs)
        results = []
        for row_as_dict in qs:
            tutors_attributions_dto = [
                TutorAttributionDTO(
                    first_name=tutor_attribution.first_name,
                    last_name=tutor_attribution.last_name,
                    function=tutor_attribution.function,
                    lecturing_volume=tutor_attribution.lecturing_volume,
                    practical_volume=tutor_attribution.practical_volume,
                ) for tutor_attribution in tutors_attributions
                if tutor_attribution.code == row_as_dict.code and tutor_attribution.year == row_as_dict.year
            ]
            vacant_course_search_dto = VacantCourseSearchDTO(
                code=row_as_dict['code'],
                year=row_as_dict['year'],
                title=row_as_dict['title'],
                is_in_team=row_as_dict['is_in_team'],
                allocation_entity_code=row_as_dict['allocation_entity'],
                vacant_declaration_type=row_as_dict['vacant_declaration_type'],
                lecturing_volume_available=row_as_dict['lecturing_volume_available'],
                lecturing_volume_total=row_as_dict['lecturing_volume_total'],
                practical_volume_available=row_as_dict['practical_volume_available'],
                practical_volume_total=row_as_dict['practical_volume_total'],
                tutors=tutors_attributions_dto
            )
            results.append(vacant_course_search_dto)
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
    subqs_volume_declared_vacant = subqs.annotate(
        volume_declared_vacant_casted=Case(
            When(volume_declared_vacant__isnull=True, then=Decimal(0.0)),
            default=F('volume_declared_vacant'),
            output_field=fields.DecimalField()
        )
    ).values('volume_declared_vacant_casted')

    subqs_volume_total = subqs.annotate(
        hourly_volume_total_annual_casted=Case(
            When(hourly_volume_total_annual__isnull=True, then=Decimal(0.0)),
            default=F('hourly_volume_total_annual'),
            output_field=fields.DecimalField()
        )
    ).values('hourly_volume_total_annual_casted')

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
            allocation_entity=F('entity_allocation'),
            lecturing_volume_total=Subquery(
                subqs_volume_total.filter(
                    type=learning_component_year_type.LECTURING
                ).values('hourly_volume_total_annual_casted')[:1],
                output_field=fields.DecimalField()
            ),
            lecturing_volume_available=Subquery(
                subqs_volume_declared_vacant.filter(
                    type=learning_component_year_type.LECTURING
                ).values('volume_declared_vacant_casted')[:1],
                output_field=fields.DecimalField()
            ),
            practical_volume_total=Subquery(
                subqs_volume_total.filter(
                    type=learning_component_year_type.PRACTICAL_EXERCISES
                ).values('hourly_volume_total_annual_casted')[:1],
                output_field=fields.DecimalField()
            ),
            practical_volume_available=Subquery(
                subqs_volume_declared_vacant.filter(
                    type=learning_component_year_type.PRACTICAL_EXERCISES
                ).values('volume_declared_vacant_casted')[:1],
                output_field=fields.DecimalField()
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
            "allocation_entity"
        ).exclude(
            lecturing_volume_available=Decimal(0),
            practical_volume_available=Decimal(0)
        )


def _annotate_allocation_entity_parents(qs: QuerySet) -> QuerySet:
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
        allocation_entity_parents=Subquery(
            cte.queryset().filter(
                start_date__lte=OuterRef('learning_container_year__academic_year__start_date'),
                end_date_queryable__gte=OuterRef('learning_container_year__academic_year__end_date'),
                entity_id=OuterRef('learning_container_year__allocation_entity_id')
            ).with_cte(cte).values('parents')[:1],
            output_field=ArrayField(models.TextField()),
        )
    )
    return qs


def _prefetch_tutors_attributions(vacant_course_qs) -> List[TutorAttributionFromRepositoryDTO]:
    subqs = AttributionChargeNew.objects.filter(attribution__id=OuterRef('id'))

    filter_clause = functools.reduce(
        operator.or_,
        ((Q(learning_container_year__acronym=entity_id['code'])
          & Q(learning_container_year__academic_year__year=entity_id['year'])) for entity_id in vacant_course_qs)
    )

    qs = AttributionNew.objects.filter(filter_clause).annotate(
        code=F('learning_container_year__acronym'),
        year=F('learning_container_year__academic_year__year'),
        first_name=F('tutor__person__first_name'),
        last_name=F('tutor__person__last_name'),
        lecturing_volume=Subquery(
            subqs.filter(
                learning_component_year__type=learning_component_year_type.LECTURING
            ).values('allocation_charge')[:1],
            output_field=models.DecimalField()
        ),
        practical_volume=Subquery(
            subqs.filter(
                learning_component_year__type=learning_component_year_type.PRACTICAL_EXERCISES
            ).values('allocation_charge')[:1],
            output_field=models.DecimalField()
        )
    ).values(
        'code',
        'year',
        'first_name',
        'last_name',
        'function',
        'lecturing_volume',
        'practical_volume',
    )
    return [TutorAttributionFromRepositoryDTO(**row) for row in qs]
