from django.test import TestCase

from base.tests.factories.learning_unit_enrollment import LearningUnitEnrollmentFactory
from ddd.logic.learning_unit.tests.factory.effective_class import LDROI1001XEffectiveClassIdentityFactory
from ddd.logic.learning_unit.tests.factory.learning_unit import LDROI1001LearningUnitIdentityFactory
from infrastructure.learning_unit.domain.service.student_enrollments_to_effective_class import \
    StudentEnrollmentsTranslator
from learning_unit.tests.factories.learning_class_year import LearningClassYearFactory


class TestStudentEnrollmentsTranslator(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.translator = StudentEnrollmentsTranslator()

    def test_should_trouver_aucune_inscription_classe(self):
        identite_classe_non_existante = LDROI1001XEffectiveClassIdentityFactory()
        self.assertFalse(self.translator.has_enrollments_to_class(identite_classe_non_existante))

    def test_should_trouver_inscription_classe(self):
        identite_classe = _create_learning_class_year_enrollment_with_identity()
        self.assertTrue(self.translator.has_enrollments_to_class(identite_classe))

    def test_should_trouver_aucune_inscription_unite_enseignement(self):
        identite_unite_enseignement_non_existante = LDROI1001LearningUnitIdentityFactory()
        self.assertFalse(self.translator.has_enrollments_to_learning_unit(identite_unite_enseignement_non_existante))

    def test_should_trouver_aucune_inscription_unite_enseignement_si_inscription_classe(self):
        identite_classe = _create_learning_class_year_enrollment_with_identity()
        self.assertFalse(self.translator.has_enrollments_to_learning_unit(identite_classe.learning_unit_identity))

    def test_should_trouver_inscription_unite_enseignement(self):
        identite_unite_enseignement = _create_learning_unit_year_enrollment_with_identity()
        self.assertTrue(self.translator.has_enrollments_to_learning_unit(identite_unite_enseignement))


def _create_learning_class_year_enrollment_with_identity():
    identite_classe = LDROI1001XEffectiveClassIdentityFactory()
    classe = LearningClassYearFactory(
        acronym=identite_classe.class_code,
        learning_component_year__learning_unit_year__acronym=identite_classe.learning_unit_identity.code,
        learning_component_year__learning_unit_year__academic_year__year=identite_classe.learning_unit_identity.year,
    )
    inscription_classe = LearningUnitEnrollmentFactory(
        learning_unit_year=classe.learning_component_year.learning_unit_year,
        learning_class_year=classe,
    )
    return identite_classe


def _create_learning_unit_year_enrollment_with_identity():
    identite_unite_enseignement = LDROI1001LearningUnitIdentityFactory()
    inscription_unite_enseignement = LearningUnitEnrollmentFactory(
        learning_unit_year__acronym=identite_unite_enseignement.code,
        learning_unit_year__academic_year__year=identite_unite_enseignement.academic_year.year,
        learning_class_year=None,
    )
    return identite_unite_enseignement
