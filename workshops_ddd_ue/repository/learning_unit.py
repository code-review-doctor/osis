from typing import Optional, List

from django.db.models import F, OuterRef, Subquery

from base.models.academic_year import AcademicYear as AcademicYearDatabase
from base.models.entity_version import EntityVersion as EntityVersionDatabase
from base.models.learning_container import LearningContainer as LearningContainerDatabase
from base.models.learning_container_year import LearningContainerYear as LearningContainerYearDatabase
from base.models.learning_unit import LearningUnit as LearningUnitDatabase
from base.models.learning_unit_year import LearningUnitYear as LearningUnitYearDatabase
from osis_common.ddd import interface
from osis_common.ddd.interface import EntityIdentity, ApplicationService, Entity
from reference.models.language import Language as LanguageDatabase
from workshops_ddd_ue.domain._academic_year import AcademicYear
from workshops_ddd_ue.domain.learning_unit_year import LearningUnit, LearningUnitIdentity
from workshops_ddd_ue.dto.learning_unit_dto import LearningUnitFromRepositoryDTO
from workshops_ddd_ue.factory.learning_unit_factory import LearningUnitBuilder


class LearningUnitRepository(interface.AbstractRepository):
    @classmethod
    def create(cls, entity: LearningUnit, **kwargs) -> LearningUnitIdentity:
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

        learning_container_year = LearningContainerYearDatabase.objects.create(
            acronym=entity.code,
            academic_year_id=academic_year_id,
            container_type=entity.type.name,
            common_title=entity.titles.common_fr,
            common_title_english=entity.titles.common_en,
            requirement_entity_id=requirement_entity_id
        )

        language_id = LanguageDatabase.objects.filter(
            code=entity.language.iso_code
        ).values_list('pk', flat=True).get()

        learn_unit_year = LearningUnitYearDatabase.objects.create(
            learning_unit=learning_unit,
            academic_year_id=academic_year_id,
            learning_container_year=learning_container_year,
            acronym=entity.code,  # FIXME :: Is this correct ? Duplicated with container.acronym ?
            specific_title=entity.titles.specific_fr,
            specific_title_english=entity.titles.specific_en,
            credits=entity.titles.credits,
            internship_subtype=entity.internship_subtype.name,
            periodicity=entity.periodicity.name,
            language_id=language_id,
            faculty_remark=entity.remarks.faculty,
            other_remark=entity.remarks.publication_fr,
            other_remark_english=entity.remarks.publication_en,
        )

        return entity.entity_id

    @classmethod
    def update(cls, entity: Entity, **kwargs: ApplicationService) -> EntityIdentity:
        raise NotImplementedError

    @classmethod
    def get(cls, entity_id: LearningUnitIdentity) -> LearningUnit:
        qs = _get_common_queryset().filter(acronym=entity_id.code, academic_year__year=entity_id.year)
        qs = _annotate_queryset(qs)
        qs = _values_queryset(qs)
        obj_as_dict = qs.get()
        dto_from_database = LearningUnitFromRepositoryDTO(**obj_as_dict)
        return LearningUnitBuilder.build_from_repository_dto(dto_from_database)

    @classmethod
    def search(cls, entity_ids: Optional[List[EntityIdentity]] = None, **kwargs) -> List[Entity]:
        raise NotImplementedError

    @classmethod
    def delete(cls, entity_id: LearningUnitIdentity, **kwargs: ApplicationService) -> None:
        obj = LearningUnitYearDatabase.objects.get(
            acronym=entity_id.code,
            academic_year__year=entity_id.year,
        )
        obj.delete()

    def get_identities(self) -> List['LearningUnitIdentity']:
        all_learn_unit_years = LearningUnitYearDatabase.objects.all().values(
            "acronym",
            "academic_year__year",
        )

        return [
            LearningUnitIdentity(
                code=learning_unit['acronym'],
                academic_year=AcademicYear(year=learning_unit['academic_year__year'])
            )
            for learning_unit in all_learn_unit_years
        ]


def _annotate_queryset(queryset):
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
                entity__id=OuterRef('requirement_entity_id')
            ).order_by('-start_date').values('acronym')[:1]
        ),
        iso_code=F('language__code'),
        remark_faculty=F('faculty_remark'),
        remark_publication_fr=F('other_remark'),
        remark_publication_en=F('other_remark_english'),
    )
    return queryset


def _values_queryset(queryset):
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
        'periodicity',
        'iso_code',
        'remark_faculty',
        'remark_publication_fr',
        'remark_publication_en',
    )
    return queryset


def _get_common_queryset():
    return LearningUnitYearDatabase.objects.all()
