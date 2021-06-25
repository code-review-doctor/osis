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
from typing import Optional, Dict, Type, List, Iterable

from django.db.models import OuterRef, Max, Subquery, Exists, Model, ForeignKey, Q
from django.utils.functional import cached_property

from base.models.academic_year import AcademicYear, starting_academic_year
from base.models.external_learning_unit_year import ExternalLearningUnitYear
from base.models.learning_achievement import LearningAchievement
from base.models.learning_component_year import LearningComponentYear
from base.models.learning_container_year import LearningContainerYear
from base.models.learning_unit import LearningUnit
from base.models.learning_unit_year import LearningUnitYear
from base.models.proposal_learning_unit import ProposalLearningUnit
from base.models.teaching_material import TeachingMaterial
from cms.enums import entity_name
from cms.models.translated_text import TranslatedText

POSTPONEMENT_RANGE = 6


class PostponeLearningUnits:

    @cached_property
    def from_year(self) -> int:
        return starting_academic_year().year

    @property
    def until_year(self) -> int:
        return self.from_year + POSTPONEMENT_RANGE

    def load_container_years_to_postpone(self) -> Iterable[LearningContainerYear]:
        last_occurence_qs = LearningContainerYear.objects.filter(
            Q(academic_year__year__gte=self.from_year) & Q(learningunityear__proposallearningunit__isnull=True),
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

        return LearningContainerYear.objects.filter(
            academic_year__year=Subquery(last_occurence_qs[:1]),
        ).annotate(
            is_mobility=Exists(is_mobility_qs)
        ).exclude(
            is_mobility=True
        ).prefetch_related(
            'learningunityear_set',
            'learningunityear_set__externallearningunityear',
            'learningunityear_set__learningcomponentyear_set',
            'learningunityear_set__learningachievement_set'
        ).distinct()

    def postpone(self):
        for lcy in self.load_container_years_to_postpone():
            for year in range(lcy.academic_year.year + 1, self.compute_container_year_end_year(lcy) + 1):
                default_values = self.load_initial_values_before_proposal(lcy)
                self.postpone_learning_container_year(lcy, year, default_values)

    def postpone_learning_container_year(
            self,
            from_lcy: LearningContainerYear,
            for_year: int,
            initial_values_before_proposal: Dict
    ):
        create_learning_container_year_from_template(
            from_lcy,
            for_year,
            initial_values_before_proposal[LearningContainerYear.__name__]
        )

        for luy in from_lcy.learningunityear_set.all():
            self.postpone_learning_unit_year(luy, for_year, initial_values_before_proposal)

    def postpone_learning_unit_year(
            self,
            from_luy: LearningUnitYear,
            for_year: int,
            initial_values_before_proposal: Dict
    ):
        if not self.compute_learning_unit_year_end_year(from_luy) >= for_year:
            return

        create_learning_unit_year_from_template(
            from_luy,
            for_year,
            initial_values_before_proposal[LearningUnitYear.__name__]
        )

        for component in from_luy.learningcomponentyear_set.all():
            create_component_year_from_template(
                component,
                for_year,
                initial_values_before_proposal[LearningComponentYear.__name__].get(component.type, {})
            )

        for material in from_luy.teachingmaterial_set.all():
            create_teaching_material_from_template(material, for_year)

        for achievement in from_luy.learningachievement_set.all():
            create_learning_achievement_from_template(achievement, for_year)

        if from_luy.is_external():
            create_external_learning_unit_year_from_template(from_luy.externallearningunityear, for_year)

        self.postpone_cms(from_luy, for_year)

    def postpone_cms(self, from_luy: LearningUnitYear, for_year: int):
        cms_query = TranslatedText.objects.filter(entity=entity_name.LEARNING_UNIT_YEAR, reference=from_luy.id)
        for cms in cms_query:
            create_cms_from_template(cms, for_year)

    def load_initial_values_before_proposal(self, lcy: LearningContainerYear) -> Dict:
        proposal = ProposalLearningUnit.objects.filter(learning_unit_year__learning_container_year=lcy).first()
        initial_values = proposal.initial_data if proposal else {}

        cleaned_initial_values = {
            LearningContainerYear.__name__: self._clean_model_initial_values(
                LearningContainerYear,
                initial_values.get('learning_container_year', {})
            ),
            LearningUnitYear.__name__: self._clean_model_initial_values(
                LearningUnitYear,
                initial_values.get('learning_unit_year', {})
            ),
            LearningComponentYear.__name__: self._clean_component_years_initial_values(
                initial_values.get('learning_component_years', [])
            )
        }

        return cleaned_initial_values

    def _clean_component_years_initial_values(self, default_values: List[Dict]) -> Dict:
        return {
            component_type_default_values['type']: self._clean_model_initial_values(
                LearningComponentYear,
                component_type_default_values
            )
            for component_type_default_values
            in default_values
        }

    def _clean_model_initial_values(self, model: Type[Model], default_values) -> Dict:
        exclude = ('id', )
        return {
            self._clean_field_name(model, field_name): field_value
            for field_name, field_value
            in default_values.items() if field_name not in exclude
        }

    def _clean_field_name(self, model: Type[Model], field_name: str) -> str:
        if isinstance(model._meta.get_field(field_name), ForeignKey):
            return "{}_id".format(field_name)
        return field_name

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

        proposal_end_year = self._compute_proposal_end_year(lcy)
        if proposal_end_year:
            return min(
                max(max_year, proposal_end_year),
                self.until_year
            )

        return min(max_year, self.until_year)

    def _compute_proposal_end_year(self, lcy: LearningContainerYear) -> Optional[float]:
        proposal = ProposalLearningUnit.objects.filter(
            learning_unit_year__learning_container_year__learning_container=lcy.learning_container
        ).first()
        if not proposal:
            return None

        end_year_id = proposal.initial_data['learning_unit']['end_year']
        if not end_year_id:
            return math.inf

        return AcademicYear.objects.get(id=end_year_id).year

    def compute_learning_unit_year_end_year(self, luy: LearningUnitYear) -> float:
        proposal = ProposalLearningUnit.objects.filter(
            learning_unit_year__learning_unit=luy.learning_unit
        ).first()
        if not proposal:
            return self.normalize_year(luy.learning_unit.end_year)

        end_year_id = proposal.initial_data['learning_unit']['end_year']
        if not end_year_id:
            return math.inf

        return self.normalize_year(AcademicYear.objects.get(id=end_year_id))


def create_learning_container_year_from_template(
        template_lcy: LearningContainerYear,
        to_year: int,
        defaults: Dict
) -> LearningContainerYear:
    acy = AcademicYear.objects.get(year=to_year)
    field_values = get_fields_values(template_lcy)
    field_values['academic_year_id'] = acy.id
    field_values.update(defaults)
    return LearningContainerYear.objects.create(**field_values)


def create_learning_unit_year_from_template(
        template_luy: LearningUnitYear,
        to_year: int,
        defaults: Dict
) -> LearningUnitYear:
    acy = AcademicYear.objects.get(year=to_year)
    lcy = LearningContainerYear.objects.get(
        learning_container=template_luy.learning_container_year.learning_container,
        academic_year__year=to_year
    )
    field_values = get_fields_values(template_luy)
    field_values['academic_year_id'] = acy.id
    field_values['learning_container_year_id'] = lcy.id
    field_values.update(defaults)
    return LearningUnitYear.objects.create(**field_values)


def create_external_learning_unit_year_from_template(
        template_external_luy: ExternalLearningUnitYear,
        to_year: int
) -> ExternalLearningUnitYear:
    luy = LearningUnitYear.objects.get(
        learning_unit=template_external_luy.learning_unit_year.learning_unit,
        academic_year__year=to_year
    )
    field_values = get_fields_values(template_external_luy)
    field_values['learning_unit_year_id'] = luy.id
    return ExternalLearningUnitYear.objects.create(**field_values)


def create_component_year_from_template(
        template_component_year: LearningComponentYear,
        to_year: int,
        defaults: Dict
) -> LearningComponentYear:
    luy = LearningUnitYear.objects.get(
        learning_unit=template_component_year.learning_unit_year.learning_unit,
        academic_year__year=to_year
    )
    field_values = get_fields_values(template_component_year)
    field_values['learning_unit_year_id'] = luy.id
    field_values.update(defaults)
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


def get_fields_values(model_obj: Model) -> Dict:
    exclude = ('external_id', 'id', 'uuid', 'changed')
    model_fields = type(model_obj)._meta.get_fields()
    return {
        field.column: getattr(model_obj, field.column)
        for field in model_fields
        if field.concrete and field.column not in exclude
    }
