from decimal import Decimal

from django.test import TestCase

from base.models.enums.learning_unit_year_session import DerogationSession
from base.models.enums.quadrimesters import DerogationQuadrimester
from base.tests.factories.learning_component_year import LecturingLearningComponentYearFactory, \
    PracticalLearningComponentYearFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from ddd.logic.learning_unit.builder.effective_class_builder import EffectiveClassBuilder
from ddd.logic.learning_unit.dtos import EffectiveClassFromRepositoryDTO
from infrastructure.learning_unit.repository.effective_class import EffectiveClassRepository


class EffectiveClassRepositoryTestCase(TestCase):
    def setUp(self):
        self.learning_unit_year = LearningUnitYearFactory(
            academic_year__current=True
        )
        self.lecturing = LecturingLearningComponentYearFactory(
            learning_unit_year=self.learning_unit_year
        )
        self.practical = PracticalLearningComponentYearFactory(
            learning_unit_year=self.learning_unit_year
        )

        campus = self.learning_unit_year.campus

        self.class_repository = EffectiveClassRepository()
        self.dto_object = EffectiveClassFromRepositoryDTO(
            code='X',
            learning_unit_code=self.learning_unit_year.acronym,
            learning_unit_year=self.learning_unit_year.academic_year.year,
            title_fr='Titre en francais',
            title_en='TItle in english',
            teaching_place=campus.name,
            teaching_organization=campus.organization.name,
            derogation_quadrimester=DerogationQuadrimester.Q1.name,
            session_derogation=DerogationSession.SESSION_123,
            volume_q1=Decimal(1.5),
            volume_q2=Decimal(2.6),
            volume_annual=Decimal(4.8)
        )
        self.effective_class = EffectiveClassBuilder.build_from_repository_dto(self.dto_object)

    def test_truc(self):
        self.class_repository.save(self.effective_class)
        effective_class = self.class_repository.get(entity_id=self.effective_class.entity_id)
        self.assertEqual(effective_class, self.effective_class)
