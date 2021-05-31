from django.test import TestCase

from base.models.enums.learning_container_year_types import LearningContainerYearType
from base.models.enums.learning_unit_year_periodicity import PeriodicityEnum
from base.models.enums.quadrimesters import DerogationQuadrimester
from base.models.learning_unit_year import LearningUnitYear
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.entity_version import EntityVersionFactory
from base.tests.factories.learning_component_year import LecturingLearningComponentYearFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFullFactory, \
    LearningUnitYearPartimFactory, LearningUnitYearFactory
from ddd.logic.learning_unit.builder.learning_unit_builder import LearningUnitBuilder
from ddd.logic.learning_unit.builder.learning_unit_identity_builder import LearningUnitIdentityBuilder
from ddd.logic.learning_unit.builder.ucl_entity_identity_builder import UclEntityIdentityBuilder
from ddd.logic.learning_unit.commands import CreateLearningUnitCommand
from infrastructure.learning_unit.repository.learning_unit import LearningUnitRepository
from reference.tests.factories.language import LanguageFactory


class LearningUnitRepositoryTestCase(TestCase):
    def setUp(self):
        self.learning_unit_repository = LearningUnitRepository()
        anac = AcademicYearFactory(current=True)
        entity_version = EntityVersionFactory()
        language = LanguageFactory()
        self.command = CreateLearningUnitCommand(
            code='LTEST2021',
            academic_year=anac.year,
            type=LearningContainerYearType.COURSE.name,
            common_title_fr='Common FR',
            specific_title_fr='Specific FR',
            common_title_en='Common EN',
            specific_title_en='Specific EN',
            credits=20,
            internship_subtype=None,
            responsible_entity_code=entity_version.acronym,
            periodicity=PeriodicityEnum.ANNUAL.name,
            iso_code=language.code,
            remark_faculty=None,
            remark_publication_fr=None,
            remark_publication_en=None,
            practical_volume_q1=2.0,
            practical_volume_q2=1.0,
            practical_volume_annual=3.0,
            lecturing_volume_q1=2.0,
            lecturing_volume_q2=1.0,
            lecturing_volume_annual=3.0,
            derogation_quadrimester=DerogationQuadrimester.Q1.name,
        )
        self.learning_unit = LearningUnitBuilder.build_from_command(
            cmd=self.command,
            all_existing_identities=[],
            responsible_entity_identity=UclEntityIdentityBuilder.build_from_code(code=entity_version.acronym)
        )

    def test_save_and_get_make_correct_mapping(self):
        self.learning_unit_repository.save(self.learning_unit)
        learning_unit = self.learning_unit_repository.get(entity_id=self.learning_unit.entity_id)

        self.assertEqual(learning_unit, self.learning_unit)
        fields = vars(self.learning_unit)
        for field in fields:
            self.assertEqual(getattr(learning_unit, field), getattr(self.learning_unit, field), field)

    def test_get_learning_unit_with_partims(self):
        luy_db = LearningUnitYearFullFactory(academic_year__current=True)
        partim_db = LearningUnitYearPartimFactory(
            learning_container_year=luy_db.learning_container_year,
            acronym='LTEST1212X',
            academic_year=luy_db.academic_year
        )
        learning_unit = self.learning_unit_repository.get(
            entity_id=LearningUnitIdentityBuilder.build_from_code_and_year(
                code=luy_db.acronym,
                year=luy_db.academic_year.year
            )
        )
        partim = learning_unit.partims[0]
        self.assertEqual(partim.subdivision, partim_db.acronym[-1:], 'subdivision')
        self.assertEqual(partim.language_id.code_iso, partim_db.language.code, 'iso_code')
        self.assertEqual(partim.title_en, partim_db.specific_title_english, 'title_en')
        self.assertEqual(partim.title_fr, partim_db.specific_title, 'title_fr')
        self.assertEqual(partim.remarks.faculty, partim_db.faculty_remark, 'remark_faculty')
        self.assertEqual(partim.remarks.publication_en, partim_db.other_remark_english, 'remark_publication_en')
        self.assertEqual(partim.remarks.publication_fr, partim_db.other_remark, 'remark_publication_fr')
        self.assertEqual(partim.credits, partim_db.credits, 'credits')
        self.assertEqual(partim.periodicity.name, partim_db.periodicity, 'periodicity')

    def test_assert_learning_unit_domain_object_is_not_a_partim(self):
        luy_db = LearningUnitYearFullFactory(academic_year__current=True)
        partim_db = LearningUnitYearPartimFactory(
            learning_container_year=luy_db.learning_container_year,
            acronym='LTEST1212X',
            academic_year=luy_db.academic_year
        )
        partim_acronym = partim_db.acronym
        self.assertTrue(LearningUnitYear.objects.filter(acronym=partim_acronym).exists())
        with self.assertRaises(LearningUnitYear.DoesNotExist):
            self.learning_unit_repository.get(
                entity_id=LearningUnitIdentityBuilder.build_from_code_and_year(
                    code=partim_acronym,
                    year=partim_db.academic_year.year
                )
            )

    def test_assert_ignoring_components_with_volume_equals_to_0(self):
        component = LecturingLearningComponentYearFactory(hourly_volume_total_annual=0.0)
        learning_unit_identity = LearningUnitIdentityBuilder.build_from_code_and_year(
            code=component.learning_unit_year.acronym,
            year=component.learning_unit_year.academic_year.year
        )
        persisted_learning_unit = self.learning_unit_repository.get(learning_unit_identity)
        self.assertIsNone(persisted_learning_unit.lecturing_part)

    def test_assert_ignoring_components_with_volume_equals_to_none(self):
        component = LecturingLearningComponentYearFactory(hourly_volume_total_annual=None)
        learning_unit_identity = LearningUnitIdentityBuilder.build_from_code_and_year(
            code=component.learning_unit_year.acronym,
            year=component.learning_unit_year.academic_year.year
        )
        persisted_learning_unit = self.learning_unit_repository.get(learning_unit_identity)
        self.assertIsNone(persisted_learning_unit.lecturing_part)

    def test_delete(self):
        learning_unit_db = LearningUnitYearFactory()
        class_identity = LearningUnitIdentityBuilder.build_from_code_and_year(
            year=learning_unit_db.academic_year.year,
            code=learning_unit_db.acronym
        )
        self.assertEqual(LearningUnitYear.objects.all().count(), 1)
        self.learning_unit_repository.delete(class_identity)
        self.assertEqual(LearningUnitYear.objects.all().count(), 0)
