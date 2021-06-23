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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
import math
from functools import cached_property
from typing import Optional

from django.db.models import OuterRef, Max, Subquery, Exists, Model

from base.models.academic_year import AcademicYear, starting_academic_year
from base.models.external_learning_unit_year import ExternalLearningUnitYear
from base.models.learning_achievement import LearningAchievement
from base.models.learning_component_year import LearningComponentYear
from base.models.learning_container_year import LearningContainerYear
from base.models.learning_unit import LearningUnit
from base.models.learning_unit_year import LearningUnitYear
from base.models.teaching_material import TeachingMaterial
from cms.enums import entity_name
from cms.models.translated_text import TranslatedText


class PostponeLearningUnits:

    @cached_property
    def from_year(self) -> int:
        return starting_academic_year().year

    @property
    def until_year(self) -> int:
        return self.from_year + 7

    def get_queryset(self):
        last_occurence_qs = LearningContainerYear.objects.filter(
            academic_year__year__gte=self.from_year,
            learning_container=OuterRef("learning_container")
        ).values(
            "learning_container"
        ).annotate(
            max_year=Max("academic_year__year")
        ).order_by(
            "learning_container"
        ).values("max_year")

        is_mobility_qs = ExternalLearningUnitYear.objects.filter(
            mobility=True,
            learning_unit_year=OuterRef('learningunityear')
        )

        qs = LearningContainerYear.objects.filter(
            academic_year__year=Subquery(last_occurence_qs[:1]),
            acronym='LINFO2335'
        ).annotate(
            is_mobility=Exists(is_mobility_qs)
        ).exclude(
            is_mobility=True
        )

        return qs

    def postpone(self):
        for lcy in self.get_queryset():
            for year in range(lcy.academic_year.year + 1, self.compute_container_year_end_year(lcy) + 1):
                self.produce_learning_container_year(lcy, year)

    def produce_learning_container_year(self, from_lcy: LearningContainerYear, for_year: int):
        create_learning_container_year_from_template(from_lcy, for_year)

        self.produce_learning_unit_years(from_lcy, for_year)

    def produce_learning_unit_years(self, from_lcy: LearningContainerYear, for_year: int):
        for luy in from_lcy.learningunityear_set.all():
            if self.normalize_year(luy.learning_unit.end_year) >= for_year:
                create_learning_unit_year_from_template(luy, for_year)

                self.produce_components(luy, for_year)
                self.produce_teaching_materials(luy, for_year)
                self.produce_learning_achievements(luy, for_year)
                self.produce_cms(luy, for_year)
                if luy.is_external():
                    self.produce_external_learnig_unit_year(luy, for_year)

    def produce_components(self, from_luy: LearningUnitYear, for_year: int):
        for component in from_luy.learningcomponentyear_set.all():
            create_component_year_from_template(component, for_year)

    def produce_teaching_materials(self, from_luy: LearningUnitYear, for_year: int):
        for material in from_luy.teachingmaterial_set.all():
            create_teaching_material_from_template(material, for_year)

    def produce_learning_achievements(self, from_luy: LearningUnitYear, for_year: int):
        for achievement in from_luy.learningachievement_set.all():
            create_learning_achievement_from_template(achievement, for_year)

    def produce_cms(self, from_luy: LearningUnitYear, for_year: int):
        cms_query = TranslatedText.objects.filter(
            entity=entity_name.LEARNING_UNIT_YEAR,
            reference=from_luy.id
        )
        for cms in cms_query:
            create_cms_from_template(cms, for_year)

    def produce_external_learnig_unit_year(self, from_luy: LearningUnitYear, for_year: int):
        external_learning_unit_year = from_luy.externallearningunityear
        create_external_learning_unit_year_from_template(external_learning_unit_year, for_year)

    def normalize_year(self, academic_year: Optional[AcademicYear]) -> float:
        if academic_year is None:
            return math.inf
        return academic_year.year

    def compute_container_year_end_year(self, lcy: LearningContainerYear) -> int:
        years = LearningUnit.objects.filter(
            learningunityear__learning_container_year=lcy
        ).values_list(
            'end_year__year', flat=True
        )
        years = [year or math.inf for year in years]
        max_year = max(years)
        return min(max_year, self.until_year)


def create_learning_container_year_from_template(
        template_lcy: LearningContainerYear,
        to_year: int
) -> LearningContainerYear:
    acy = AcademicYear.objects.get(year=to_year)
    field_values = get_fields_values(template_lcy)
    field_values['academic_year_id'] = acy.id
    return LearningContainerYear.objects.create(**field_values)


def create_learning_unit_year_from_template(
        template_luy: LearningUnitYear,
        to_year: int
) -> LearningUnitYear:
    acy = AcademicYear.objects.get(year=to_year)
    lcy = LearningContainerYear.objects.get(
        learning_container=template_luy.learning_container_year.learning_container,
        academic_year__year=to_year
    )
    field_values = get_fields_values(template_luy)
    field_values['academic_year_id'] = acy.id
    field_values['learning_container_year_id'] = lcy.id
    return LearningUnitYear.objects.create(**field_values)


def create_external_learning_unit_year_from_template(
        template_external_luy: ExternalLearningUnitYear,
        to_year: int
) -> ExternalLearningUnitYear:
    luy = LearningUnitYear.objects.get(
        learning_unit_year__learning_unit=template_external_luy.learning_unit_year.learning_unit,
        academic_year__year=to_year
    )
    field_values = get_fields_values(template_external_luy)
    field_values['learning_unit_year_id'] = luy.id
    return ExternalLearningUnitYear.objects.create(**field_values)


def create_component_year_from_template(
        template_component_year: LearningComponentYear,
        to_year: int
) -> LearningComponentYear:
    luy = LearningUnitYear.objects.get(
        learning_unit=template_component_year.learning_unit_year.learning_unit,
        academic_year__year=to_year
    )
    field_values = get_fields_values(template_component_year)
    field_values['learning_unit_year_id'] = luy.id
    return LearningComponentYear.objects.create(**field_values)


def create_teaching_material_from_template(
        template_teaching_material: TeachingMaterial,
        to_year: int
) -> TeachingMaterial:
    luy = LearningUnitYear.objects.get(
        learning_unit=template_teaching_material.learning_unit_year.learning_unit,
        academic_year__year=to_year
    )
    field_values = get_fields_values(template_teaching_material)
    field_values['learning_unit_year_id'] = luy.id
    return TeachingMaterial.objects.create(**field_values)


def create_learning_achievement_from_template(
        template_achievement: LearningAchievement,
        to_year: int
) -> LearningAchievement:
    luy = LearningUnitYear.objects.get(
        learning_unit=template_achievement.learning_unit_year.learning_unit,
        academic_year__year=to_year
    )
    field_values = get_fields_values(template_achievement)
    field_values['learning_unit_year_id'] = luy.id
    return LearningAchievement.objects.create(**field_values)


def create_cms_from_template(
        template_cms: TranslatedText,
        to_year: int
) -> TranslatedText:
    luy = LearningUnitYear.objects.get(
        learning_unit__learningunityear__id=template_cms.reference,
        academic_year__year=to_year
    )
    field_values = get_fields_values(template_cms)
    field_values['reference'] = luy.id
    return TranslatedText.objects.create(**field_values)


def get_fields_values(model_obj: Model) -> dict:
    exclude = ('external_id', 'id', 'uuid', 'changed')
    model_fields = type(model_obj)._meta.get_fields()
    return {
        field.column: getattr(model_obj, field.column)
        for field in model_fields
        if field.concrete and field.column not in exclude
    }
