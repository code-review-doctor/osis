from decimal import Decimal

from django.test import TestCase

from base.models.enums.learning_component_year_type import LECTURING
from base.models.enums.learning_unit_year_session import DerogationSession
from base.models.enums.quadrimesters import DerogationQuadrimester
from base.tests.factories.learning_component_year import LecturingLearningComponentYearFactory, \
    PracticalLearningComponentYearFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from ddd.logic.learning_unit.builder.effective_class_builder import EffectiveClassBuilder
from ddd.logic.learning_unit.builder.effective_class_identity_builder import EffectiveClassIdentityBuilder
from ddd.logic.learning_unit.domain.model.effective_class import EffectiveClassIdentity
from ddd.logic.learning_unit.domain.model.learning_unit import LearningUnitIdentity
from ddd.logic.learning_unit.dtos import EffectiveClassFromRepositoryDTO
from ddd.logic.shared_kernel.academic_year.domain.model.academic_year import AcademicYearIdentity
from infrastructure.learning_unit.repository.effective_class import EffectiveClassRepository
from learning_unit.models.learning_class_year import LearningClassYear as LearningClassYearDb
from learning_unit.tests.factories.learning_class_year import LearningClassYearFactory


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

        self.campus = self.learning_unit_year.campus

        self.class_repository = EffectiveClassRepository()

    def test_save_and_get_make_correct_mapping(self):
        dto_object = EffectiveClassFromRepositoryDTO(
            class_code='X',
            learning_unit_code=self.learning_unit_year.acronym,
            learning_unit_year=self.learning_unit_year.academic_year.year,
            title_fr='Titre en francais',
            title_en='TItle in english',
            teaching_place=self.campus.name,
            teaching_organization=self.campus.organization.name,
            derogation_quadrimester=DerogationQuadrimester.Q1.name,
            session_derogation=DerogationSession.SESSION_123.name,
            volume_q1=Decimal('1.5'),
            volume_q2=Decimal('2.6'),
            class_type=LECTURING
        )
        effective_class_to_persist = EffectiveClassBuilder.build_from_repository_dto(dto_object)
        self.class_repository.save(effective_class_to_persist)
        effective_class = self.class_repository.get(entity_id=effective_class_to_persist.entity_id)

        self.assertEqual(effective_class, effective_class_to_persist)
        fields = vars(effective_class)
        for field in fields:
            self.assertEqual(getattr(effective_class, field), getattr(effective_class_to_persist, field), field)

    def test_delete(self):
        class_db = LearningClassYearFactory()
        class_identity = EffectiveClassIdentityBuilder.build_from_code_and_learning_unit_identity_data(
            class_code=class_db.acronym,
            learning_unit_year=class_db.learning_component_year.learning_unit_year.academic_year.year,
            learning_unit_code=class_db.learning_component_year.learning_unit_year.acronym
        )
        self.assertEqual(LearningClassYearDb.objects.all().count(), 1)
        self.class_repository.delete(class_identity)
        self.assertEqual(LearningClassYearDb.objects.all().count(), 0)

    def test_get_all_identities(self):
        classes_db = [LearningClassYearFactory() for _ in range(5)]
        identities = [
            EffectiveClassIdentity(
                class_code=class_db.acronym,
                learning_unit_identity=LearningUnitIdentity(
                    academic_year=AcademicYearIdentity(
                        year=class_db.learning_component_year.learning_unit_year.academic_year.year
                    ),
                    code=class_db.learning_component_year.learning_unit_year.acronym
                )
            )
            for class_db in classes_db
        ]
        # assert lists contain same elements regardless order
        self.assertCountEqual(identities, self.class_repository.get_all_identities())
