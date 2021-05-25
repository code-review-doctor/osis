from decimal import Decimal

from django.test import TestCase

from base.models.enums.learning_unit_year_session import DerogationSession
from base.models.enums.quadrimesters import DerogationQuadrimester
from ddd.logic.learning_unit.domain.model._campus import TeachingPlace
from ddd.logic.learning_unit.domain.model._class_titles import ClassTitles
from ddd.logic.learning_unit.domain.model._volumes_repartition import Volumes
from ddd.logic.learning_unit.domain.model.effective_class import LecturingEffectiveClass, EffectiveClassIdentity
from ddd.logic.learning_unit.domain.model.learning_unit import LearningUnitIdentity
from ddd.logic.shared_kernel.academic_year.domain.model.academic_year import AcademicYear, AcademicYearIdentity
from infrastructure.learning_unit.repository.effective_class import EffectiveClassRepository


class EffectiveClassRepositoryTestCase(TestCase):
    def setUp(self):
        self.class_repository = EffectiveClassRepository()
        self.anac = AcademicYear(entity_id=AcademicYearIdentity(year=2021), start_date=None, end_date=None)
        self.learning_unit_identity = LearningUnitIdentity(code='LTEST2021', academic_year=self.anac)
        self.class_identity = EffectiveClassIdentity(code='X', learning_unit_identity=self.learning_unit_identity)
        self.effective_class = LecturingEffectiveClass(
            entity_id=self.class_identity,
            titles=ClassTitles(fr='Title Fr', en='Title En'),
            teaching_place=TeachingPlace(place='Place', organization_name='Organization'),
            derogation_quadrimester=DerogationQuadrimester.Q1.name,
            session_derogation=DerogationSession.SESSION_1XX.name,
            volumes=Volumes(
                volume_first_quadrimester=Decimal(1.0),
                volume_second_quadrimester=Decimal(2.0),
                volume_annual=Decimal(3.0)
            )
        )

    def test_truc(self):
        pass