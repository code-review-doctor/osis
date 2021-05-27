from django.test import TestCase

from base.models.enums.learning_container_year_types import LearningContainerYearType
from base.models.enums.learning_unit_year_periodicity import PeriodicityEnum
from base.models.enums.quadrimesters import DerogationQuadrimester
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.entity_version import EntityVersionFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFullFactory, \
    LearningUnitYearPartimFactory
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
        fields = [
            'titles', 'credits', 'internship_subtype', 'responsible_entity_identity', 'periodicity', 'language_id',
            'remarks', 'partims', 'derogation_quadrimester', 'lecturing_part', 'practical_part'
        ]
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
