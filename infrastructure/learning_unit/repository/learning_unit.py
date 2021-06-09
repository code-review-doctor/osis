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

from django.db.models import F, OuterRef, Subquery, Case, When, Q, CharField, Value, QuerySet
from django.db.models.functions import Concat, Substr, Length

from base.models.academic_year import AcademicYear as AcademicYearDatabase
from base.models.entity_version import EntityVersion as EntityVersionDatabase
from base.models.enums import learning_unit_year_subtypes
from base.models.enums.learning_component_year_type import PRACTICAL_EXERCISES, LECTURING
from base.models.learning_component_year import LearningComponentYear as LearningComponentYearDatabase
from base.models.learning_container import LearningContainer as LearningContainerDatabase
from base.models.learning_container_year import LearningContainerYear as LearningContainerYearDatabase
from base.models.learning_unit import LearningUnit as LearningUnitDatabase
from base.models.learning_unit_enrollment import LearningUnitEnrollment as LearningUnitEnrollmentDatabase
from base.models.learning_unit_year import LearningUnitYear as LearningUnitYearDatabase
from base.models.proposal_learning_unit import ProposalLearningUnit as ProposalLearningUnitDatabase
from ddd.logic.learning_unit.builder.learning_unit_builder import LearningUnitBuilder
from ddd.logic.learning_unit.domain.model.learning_unit import LearningUnit, LearningUnitIdentity
from ddd.logic.learning_unit.dtos import LearningUnitFromRepositoryDTO, LearningUnitSearchDTO, PartimFromRepositoryDTO
from ddd.logic.learning_unit.repository.i_learning_unit import ILearningUnitRepository
from ddd.logic.shared_kernel.academic_year.builder.academic_year_identity_builder import AcademicYearIdentityBuilder
from osis_common.ddd.interface import EntityIdentity, ApplicationService, Entity
from reference.models.language import Language as LanguageDatabase


class LearningUnitRepository(ILearningUnitRepository):

    @classmethod
    def has_proposal_this_year_or_in_past(cls, learning_unit: 'LearningUnit') -> bool:
        return ProposalLearningUnitDatabase.objects.filter(
            learning_unit_year__learning_unit__learningunityear__acronym=learning_unit.entity_id.code,
            learning_unit_year__academic_year__year__lte=learning_unit.entity_id.year
        ).exists()

    @classmethod
    def has_enrollments(cls, learning_unit: 'LearningUnit') -> bool:
        return LearningUnitEnrollmentDatabase.objects.filter(
            learning_unit_year__acronym=learning_unit.entity_id.code,
            learning_unit_year__academic_year__year=learning_unit.entity_id.year
        ).exists()

    @classmethod
    def search_learning_units_dto(
            cls,
            code: str = None,
            year: int = None,
            full_title: str = None,
            type: str = None,
            responsible_entity_code: str = None
    ) -> List['LearningUnitSearchDTO']:
        qs = _get_common_queryset()
        # FIXME :: reuse Django filter
        if code is not None:
            qs = qs.filter(
                acronym__icontains=code,
            )
        if year is not None:
            qs = qs.filter(
                academic_year__year=year,
            )
        if type is not None:
            qs = qs.filter(
                learning_container_year__container_type=type,
            )
        if responsible_entity_code is not None:
            qs = qs.filter(
                requirement_entity__entityversion__acronym__icontains=responsible_entity_code,
            )
        if full_title is not None:
            qs = qs.filter(
                Q(learning_container_year__common_title__icontains=full_title)
                | Q(specific_title__icontains=full_title),
            )

        qs = qs.annotate(
            code=F('acronym'),
            year=F('academic_year__year'),
            type=F('learning_container_year__container_type'),
            full_title=Case(
                When(
                    Q(learning_container_year__common_title__isnull=True) |
                    Q(learning_container_year__common_title__exact=''),
                    then='specific_title'
                ),
                When(
                    Q(specific_title__isnull=True) | Q(specific_title__exact=''),
                    then='learning_container_year__common_title'
                ),
                default=Concat('learning_container_year__common_title', Value(' - '), 'specific_title'),
                output_field=CharField(),
            ),
            responsible_entity_code=Subquery(
                EntityVersionDatabase.objects.filter(
                    entity__id=OuterRef('requirement_entity_id')
                ).order_by('-start_date').values('acronym')[:1]
            ),
            responsible_entity_title=Subquery(
                EntityVersionDatabase.objects.filter(
                    entity__id=OuterRef('requirement_entity_id')
                ).order_by('-start_date').values('title')[:1]
            ),
        ).values(
            "year",
            "code",
            "full_title",
            "type",
            "responsible_entity_code",
            "responsible_entity_title",
        )
        result = []
        for data_dict in qs.values():
            result.append(LearningUnitSearchDTO(**data_dict))
        return result

    @classmethod
    def save(cls, entity: 'LearningUnit') -> None:
        # FIXME :: use get_or_create (or save) instead of Django create()
        learning_container = LearningContainerDatabase.objects.create()

        learning_unit = LearningUnitDatabase.objects.create(
            learning_container=learning_container,
        )

        requirement_entity_id = EntityVersionDatabase.objects.filter(
            acronym=entity.responsible_entity_identity.code
        ).values_list('entity_id', flat=True).get()

        academic_year_id = AcademicYearDatabase.objects.filter(
            year=entity.academic_year.year
        ).values_list('pk', flat=True).get()

        learning_container = LearningContainerDatabase.objects.create()

        learning_container_year = LearningContainerYearDatabase.objects.create(
            learning_container=learning_container,
            acronym=entity.code,
            academic_year_id=academic_year_id,
            container_type=entity.type.name,
            common_title=entity.titles.common_fr,
            common_title_english=entity.titles.common_en,
            requirement_entity_id=requirement_entity_id
        )

        language_id = LanguageDatabase.objects.filter(
            code=entity.language_id.code_iso
        ).values_list('pk', flat=True).get()

        learn_unit_year = LearningUnitYearDatabase.objects.create(
            learning_unit=learning_unit,
            academic_year_id=academic_year_id,
            learning_container_year=learning_container_year,
            acronym=entity.code,  # FIXME :: Is this correct ? Duplicated with container.acronym ?
            specific_title=entity.titles.specific_fr,
            specific_title_english=entity.titles.specific_en,
            credits=entity.credits,
            internship_subtype=entity.internship_subtype.name if entity.internship_subtype else None,
            periodicity=entity.periodicity.name,
            language_id=language_id,
            faculty_remark=entity.remarks.faculty,
            other_remark=entity.remarks.publication_fr,
            other_remark_english=entity.remarks.publication_en,
            quadrimester=entity.derogation_quadrimester.name,
            subtype=learning_unit_year_subtypes.FULL
        )

        LearningComponentYearDatabase.objects.create(
            type=LECTURING,
            learning_unit_year=learn_unit_year,
            hourly_volume_partial_q1=entity.lecturing_part.volumes.volume_first_quadrimester,
            hourly_volume_partial_q2=entity.lecturing_part.volumes.volume_second_quadrimester,
            hourly_volume_total_annual=entity.lecturing_part.volumes.volume_annual,
        )
        LearningComponentYearDatabase.objects.create(
            type=PRACTICAL_EXERCISES,
            learning_unit_year=learn_unit_year,
            hourly_volume_partial_q1=entity.practical_part.volumes.volume_first_quadrimester,
            hourly_volume_partial_q2=entity.practical_part.volumes.volume_second_quadrimester,
            hourly_volume_total_annual=entity.practical_part.volumes.volume_annual,
        )
        return entity.entity_id

    @classmethod
    def get(cls, entity_id: 'LearningUnitIdentity') -> 'LearningUnit':
        qs = _get_common_queryset().filter(acronym=entity_id.code, academic_year__year=entity_id.year)
        partims = _get_partims(qs)
        qs = _annotate_queryset(qs)
        qs = _values_queryset(qs)
        obj_as_dict = qs.get()
        partims_dto = [
            PartimFromRepositoryDTO(**partim) for partim in partims
        ]
        dto_from_database = LearningUnitFromRepositoryDTO(**obj_as_dict, partims=partims_dto)
        return LearningUnitBuilder.build_from_repository_dto(dto_from_database)

    @classmethod
    def search(cls, entity_ids: Optional[List[EntityIdentity]] = None, **kwargs) -> List[Entity]:
        raise NotImplementedError

    @classmethod
    def delete(cls, entity_id: 'LearningUnitIdentity', **kwargs: 'ApplicationService') -> None:
        obj = LearningUnitYearDatabase.objects.get(
            acronym=entity_id.code,
            academic_year__year=entity_id.year,
        )
        obj.delete()

    @classmethod
    def get_all_identities(cls) -> List['LearningUnitIdentity']:
        all_learn_unit_years = LearningUnitYearDatabase.objects.filter(
            subtype=learning_unit_year_subtypes.FULL
        ).values(
            "acronym",
            "academic_year__year",
        )

        return [
            LearningUnitIdentity(
                code=learning_unit['acronym'],
                academic_year=AcademicYearIdentityBuilder.build_from_year(year=learning_unit['academic_year__year'])
            )
            for learning_unit in all_learn_unit_years
        ]


def _get_partims(qs: QuerySet) -> QuerySet:
    return LearningUnitYearDatabase.objects.filter(
        subtype=learning_unit_year_subtypes.PARTIM,
        learning_container_year_id=Subquery(qs.values('learning_container_year_id'))
    ).annotate(
        subdivision=Substr('acronym', Length('acronym'), output_field=CharField()),
        title_fr=F('specific_title'),
        title_en=F('specific_title_english'),
        iso_code=F('language__code'),
        remark_faculty=F('faculty_remark'),
        remark_publication_fr=F('other_remark'),
        remark_publication_en=F('other_remark_english'),
    ).values(
        'subdivision',
        'title_fr',
        'title_en',
        'credits',
        'periodicity',
        'iso_code',
        'remark_faculty',
        'remark_publication_fr',
        'remark_publication_en'
    )


def _annotate_queryset(queryset: QuerySet) -> QuerySet:
    components = LearningComponentYearDatabase.objects.filter(
        learning_unit_year_id=OuterRef('pk'),
        hourly_volume_total_annual__gt=0.0,
    )
    queryset = queryset.annotate(
        code=F('acronym'),
        year=F('academic_year__year'),
        type=F('learning_container_year__container_type'),
        common_title_fr=F('learning_container_year__common_title'),
        specific_title_fr=F('specific_title'),
        common_title_en=F('learning_container_year__common_title_english'),
        specific_title_en=F('specific_title_english'),
        responsible_entity_code=Subquery(
            EntityVersionDatabase.objects.filter(
                entity__id=OuterRef('learning_container_year__requirement_entity_id')
            ).order_by('-start_date').values('acronym')[:1]
        ),
        attribution_entity_code=Subquery(
            EntityVersionDatabase.objects.filter(
                entity__id=OuterRef('learning_container_year__allocation_entity_id')
            ).order_by('-start_date').values('acronym')[:1]
        ),
        iso_code=F('language__code'),
        remark_faculty=F('faculty_remark'),
        remark_publication_fr=F('other_remark'),
        remark_publication_en=F('other_remark_english'),

        repartition_entity_2=Subquery(  # TODO :: to unit test
            EntityVersionDatabase.objects.filter(
                entity__id=OuterRef('learning_container_year__additional_entity_1_id')
            ).order_by('-start_date').values('acronym')[:1]
        ),
        repartition_entity_3=Subquery(  # TODO :: to unit test
            EntityVersionDatabase.objects.filter(
                entity__id=OuterRef('learning_container_year__additional_entity_2_id')
            ).order_by('-start_date').values('acronym')[:1]
        ),

        lecturing_volume_q1=Subquery(components.filter(type=LECTURING).values('hourly_volume_partial_q1')),
        lecturing_volume_q2=Subquery(components.filter(type=LECTURING).values('hourly_volume_partial_q2')),
        lecturing_volume_annual=Subquery(components.filter(type=LECTURING).values('hourly_volume_total_annual')),
        lecturing_planned_classes=Subquery(components.filter(type=LECTURING).values('planned_classes')),
        lecturing_volume_repartition_responsible_entity=Subquery(  # TODO :: to unit test
            components.filter(type=LECTURING).values('repartition_volume_requirement_entity')
        ),
        lecturing_volume_repartition_entity_2=Subquery(  # TODO :: to unit test
            components.filter(type=LECTURING).values('repartition_volume_additional_entity_1')
        ),
        lecturing_volume_repartition_entity_3=Subquery(  # TODO :: to unit test
            components.filter(type=LECTURING).values('repartition_volume_additional_entity_2')
        ),

        practical_volume_q1=Subquery(components.filter(type=PRACTICAL_EXERCISES).values('hourly_volume_partial_q1')),
        practical_volume_q2=Subquery(components.filter(type=PRACTICAL_EXERCISES).values('hourly_volume_partial_q2')),
        practical_volume_annual=Subquery(
            components.filter(type=PRACTICAL_EXERCISES).values('hourly_volume_total_annual')
        ),
        practical_planned_classes=Subquery(components.filter(type=PRACTICAL_EXERCISES).values('planned_classes')),
        practical_volume_repartition_responsible_entity=Subquery(  # TODO :: to unit test
            components.filter(type=PRACTICAL_EXERCISES).values('repartition_volume_requirement_entity')
        ),
        practical_volume_repartition_entity_2=Subquery(  # TODO :: to unit test
            components.filter(type=PRACTICAL_EXERCISES).values('repartition_volume_additional_entity_1')
        ),
        practical_volume_repartition_entity_3=Subquery(  # TODO :: to unit test
            components.filter(type=PRACTICAL_EXERCISES).values('repartition_volume_additional_entity_2')
        ),

        derogation_quadrimester=F('quadrimester'),
        derogation_session=F('session'),
        teaching_place_uuid=F('campus__uuid'),
        is_active=F('status'),
    )
    return queryset


def _values_queryset(queryset: QuerySet) -> QuerySet:
    queryset = queryset.values(
        'code',
        'year',
        'type',
        'common_title_fr',
        'specific_title_fr',
        'common_title_en',
        'specific_title_en',
        'credits',
        'internship_subtype',
        'responsible_entity_code',
        'attribution_entity_code',
        'periodicity',
        'iso_code',
        'remark_faculty',
        'remark_publication_fr',
        'remark_publication_en',

        'repartition_entity_2',
        'repartition_entity_3',

        'lecturing_volume_q1',
        'lecturing_volume_q2',
        'lecturing_volume_annual',
        'lecturing_planned_classes',
        'lecturing_volume_repartition_responsible_entity',
        'lecturing_volume_repartition_entity_2',
        'lecturing_volume_repartition_entity_3',

        'practical_volume_q1',
        'practical_volume_q2',
        'practical_volume_annual',
        'practical_planned_classes',
        'practical_volume_repartition_responsible_entity',
        'practical_volume_repartition_entity_2',
        'practical_volume_repartition_entity_3',

        'derogation_quadrimester',
        'derogation_session',
        'teaching_place_uuid',
        'professional_integration',
        'is_active',
    )
    return queryset


def _get_common_queryset() -> QuerySet:
    return LearningUnitYearDatabase.objects.filter(
        subtype=learning_unit_year_subtypes.FULL
    ).select_related(
        'academic_year',
        'learning_container_year',
        'language'
    )
