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

import attr
from django.test import TestCase

from base.ddd.utils.business_validator import MultipleBusinessExceptions
from base.models.enums.learning_container_year_types import LearningContainerYearType
from base.models.enums.learning_unit_year_periodicity import PeriodicityEnum
from base.models.enums.learning_unit_year_session import DerogationSession
from base.models.enums.quadrimesters import DerogationQuadrimester
from ddd.logic.learning_unit.builder.effective_class_identity_builder import EffectiveClassIdentityBuilder
from ddd.logic.learning_unit.builder.learning_unit_builder import LearningUnitBuilder
from ddd.logic.learning_unit.builder.ucl_entity_identity_builder import UclEntityIdentityBuilder
from ddd.logic.learning_unit.commands import CreateEffectiveClassCommand, CreateLearningUnitCommand, CreatePartimCommand
from ddd.logic.learning_unit.domain.model.effective_class import LecturingEffectiveClass, PracticalEffectiveClass, \
    EffectiveClass
from ddd.logic.learning_unit.domain.model.learning_unit import LearningUnit
from ddd.logic.learning_unit.domain.validator.exceptions import ShouldBeAlphanumericException, \
    CodeClassAlreadyExistForUeException, ClassTypeInvalidException, AnnualVolumeInvalidException, \
    LearningUnitHasPartimException, LearningUnitHasProposalException, LearningUnitHasEnrollmentException, \
    LearningUnitHasNoVolumeException, TeachingPlaceRequiredException, DerogationQuadrimesterInvalidChoiceException, \
    DerogationSessionInvalidChoiceException
from ddd.logic.learning_unit.tests.factory.learning_unit import LDROI1001CourseLearningUnitFactory
from ddd.logic.learning_unit.use_case.write.create_effective_class_service import create_effective_class
from infrastructure.learning_unit.repository.in_memory.effective_class import EffectiveClassRepository
from infrastructure.learning_unit.repository.in_memory.learning_unit import LearningUnitRepository

YEAR = 2020


class TestCreateClassServiceEffectiveClassType(TestCase):

    def setUp(self):
        self.learning_unit_repository = LearningUnitRepository()
        self.effective_class_repository = EffectiveClassRepository()
        self.command = _build_create_learning_unit_command()

    def test_effective_class_type_lecturing(self):
        ue_with_lecturing_and_practical_volumes = _create_lu(self.command)
        self.learning_unit_repository.save(ue_with_lecturing_and_practical_volumes)
        effective_class_id = create_effective_class(
            _build_create_effective_class_command(
                learning_unit_code=ue_with_lecturing_and_practical_volumes.code,
                class_code='A'
            ),
            self.learning_unit_repository,
            self.effective_class_repository
        )
        effective_class = self.effective_class_repository.get(effective_class_id)
        self.assertIsInstance(effective_class, LecturingEffectiveClass)

    def test_effective_class_type_practical(self):
        command = attr.evolve(
            self.command,
            lecturing_volume_annual=0.0, lecturing_volume_q2=0.0, lecturing_volume_q1=0.0, code='LTEST2022'
        )
        ue_with_practical_volumes_only = _create_lu(command)
        self.learning_unit_repository.save(ue_with_practical_volumes_only)
        effective_class_id = create_effective_class(
            _build_create_effective_class_command(
                learning_unit_code=ue_with_practical_volumes_only.code,
                class_code='C'
            ),
            self.learning_unit_repository,
            self.effective_class_repository
        )
        effective_class = self.effective_class_repository.get(effective_class_id)
        self.assertIsInstance(effective_class, PracticalEffectiveClass)

    def test_effective_class_type_lecturing_only(self):
        command = attr.evolve(
            self.command,
            practical_volume_annual=0.0, practical_volume_q2=0.0, practical_volume_q1=0.0, code='LTEST2023'
        )
        ue_with_lecturing_volumes_only = _create_lu(command)
        self.learning_unit_repository.save(ue_with_lecturing_volumes_only)
        effective_class_id = create_effective_class(
            _build_create_effective_class_command(
                learning_unit_code=ue_with_lecturing_volumes_only.code,
                class_code='B'
            ),
            self.learning_unit_repository,
            self.effective_class_repository
        )
        effective_class = self.effective_class_repository.get(effective_class_id)
        self.assertIsInstance(effective_class, LecturingEffectiveClass)


class TestCreateClassServiceValidator(TestCase):
    def setUp(self):
        self.learning_unit_repository = LearningUnitRepository()
        self.command = _build_create_learning_unit_command()
        self.ue_with_lecturing_and_practical_volumes = _create_lu(self.command)
        self.learning_unit_repository.save(self.ue_with_lecturing_and_practical_volumes)

        self.effective_class_repository = EffectiveClassRepository()
        effective_class_identity = EffectiveClassIdentityBuilder.build_from_code_and_learning_unit_identity_data(
            class_code='A',
            learning_unit_code=self.ue_with_lecturing_and_practical_volumes.code,
            learning_unit_year=YEAR
        )

        self.effective_class = EffectiveClass(
            entity_id=effective_class_identity,
            titles=None,
            teaching_place=None,
            derogation_quadrimester=None,
            session_derogation=None,
            volumes=None
        )
        self.effective_class_repository.save(self.effective_class)

    def test_class_code_raise_should_be_alphanumeric_exception(self):
        cmd = _build_create_effective_class_command(
            learning_unit_code=self.ue_with_lecturing_and_practical_volumes.code, class_code='*'
        )
        with self.assertRaises(MultipleBusinessExceptions) as class_exceptions:
            create_effective_class(
                cmd,
                self.learning_unit_repository,
                self.effective_class_repository
            )
        self.assertIsInstance(
            class_exceptions.exception.exceptions.pop(),
            ShouldBeAlphanumericException
        )

    def test_class_code_raise_class_code_should_be_unique_for_ue_exception(self):
        already_existing_class_code = self.effective_class.entity_id.class_code
        cmd = _build_create_effective_class_command(
            learning_unit_code=self.ue_with_lecturing_and_practical_volumes.code,
            class_code=already_existing_class_code
        )
        with self.assertRaises(MultipleBusinessExceptions) as class_exceptions:
            create_effective_class(
                cmd,
                self.learning_unit_repository,
                self.effective_class_repository
            )
        self.assertIsInstance(
            class_exceptions.exception.exceptions.pop(),
            CodeClassAlreadyExistForUeException
        )

    def test_raise_should_not_be_type_mobility_or_external_exception(self):
        command = attr.evolve(self.command, type=LearningContainerYearType.EXTERNAL.name, code='LEXTE2021')
        ue_external = _create_lu(command=command)
        self.learning_unit_repository.save(ue_external)
        cmd = _build_create_effective_class_command(learning_unit_code=ue_external.code, class_code='B')
        with self.assertRaises(MultipleBusinessExceptions) as class_exceptions:
            create_effective_class(
                cmd,
                self.learning_unit_repository,
                self.effective_class_repository
            )
        self.assertIsInstance(
            class_exceptions.exception.exceptions.pop(),
            ClassTypeInvalidException
        )

    def test_raise_should_learning_unit_not_have_proposal_exception(self):
        learning_unit_repository = LearningUnitRepository()
        learning_unit_repository.has_proposal_this_year_or_in_past = lambda *args, **kwargs: True
        cmd = _build_create_effective_class_command(
            learning_unit_code=self.ue_with_lecturing_and_practical_volumes.code,
            class_code='Z'
        )
        with self.assertRaises(MultipleBusinessExceptions) as class_exceptions:
            create_effective_class(
                cmd,
                learning_unit_repository,
                self.effective_class_repository
            )
        self.assertIsInstance(
            class_exceptions.exception.exceptions.pop(),
            LearningUnitHasProposalException
        )

    def test_raise_should_learning_unit_not_have_enrollment_exception(self):
        learning_unit_repository = LearningUnitRepository()
        learning_unit_repository.has_enrollments = lambda *args, **kwargs: True
        cmd = _build_create_effective_class_command(
            learning_unit_code=self.ue_with_lecturing_and_practical_volumes.code,
            class_code='Z'
        )
        with self.assertRaises(MultipleBusinessExceptions) as class_exceptions:
            create_effective_class(
                cmd,
                learning_unit_repository,
                self.effective_class_repository
            )
        self.assertIsInstance(
            class_exceptions.exception.exceptions.pop(),
            LearningUnitHasEnrollmentException
        )

    def test_raise_should_learning_unit_not_have_partim_exception(self):
        command = attr.evolve(self.command, code='LPART2021')
        ue_with_partims = _create_lu(command=command)

        partim_cmd = CreatePartimCommand(
            learning_unit_code=ue_with_partims.code,
            learning_unit_year=ue_with_partims.academic_year.year,
            subdivision='T',
            title_fr='Partim FR',
            title_en='Partim EN',
            credits=20,
            periodicity=PeriodicityEnum.ANNUAL.name,
            iso_code='fr-be',
            remark_faculty='Remark Fac',
            remark_publication_fr='Remark FR',
            remark_publication_en='Remark EN',
        )
        ue_with_partims.create_partim(partim_cmd)
        self.learning_unit_repository.save(ue_with_partims)
        cmd = _build_create_effective_class_command(learning_unit_code=ue_with_partims.code, class_code='B')
        with self.assertRaises(MultipleBusinessExceptions) as class_exceptions:
            create_effective_class(
                cmd,
                self.learning_unit_repository,
                self.effective_class_repository
            )
        self.assertIsInstance(
            class_exceptions.exception.exceptions.pop(),
            LearningUnitHasPartimException
        )

    def test_raise_check_learning_unit_has_no_volume_exception(self):
        command = attr.evolve(
            self.command,
            lecturing_volume_q1=0.0, lecturing_volume_q2=0.0, lecturing_volume_annual=0.0,
            practical_volume_annual=0.0, practical_volume_q2=0.0, practical_volume_q1=0.0,
            code='LTEST2025'
        )
        ue_no_volumes = _create_lu(command)
        self.learning_unit_repository.save(ue_no_volumes)
        cmd = _build_create_effective_class_command(learning_unit_code=ue_no_volumes.code, class_code='C')
        with self.assertRaises(MultipleBusinessExceptions) as class_exceptions:
            create_effective_class(
                cmd,
                self.learning_unit_repository,
                self.effective_class_repository
            )
        self.assertIsInstance(
            class_exceptions.exception.exceptions.pop(),
            LearningUnitHasNoVolumeException
        )

    def test_raise_check_partim_volume_inconsistent_exception(self):
        command = attr.evolve(
            self.command,
            lecturing_volume_q1=0.0, lecturing_volume_q2=0.0, lecturing_volume_annual=10.0,
            practical_volume_annual=0.0, practical_volume_q2=0.0, practical_volume_q1=0.0,
            code='LTEST2026'
        )
        ue = _create_lu(command)
        self.learning_unit_repository.save(ue)
        cmd = _build_create_effective_class_command(learning_unit_code=ue.code, class_code='T')
        with self.assertRaises(MultipleBusinessExceptions) as class_exceptions:
            create_effective_class(
                cmd,
                self.learning_unit_repository,
                self.effective_class_repository
            )
        self.assertIsInstance(
            class_exceptions.exception.exceptions.pop(),
            AnnualVolumeInvalidException
        )

    def test_not_raise_check_volume_inconsistent_exception_because_no_volumes_encoded(self):
        ue_command = attr.evolve(
            self.command,
            lecturing_volume_q1=0.0, lecturing_volume_q2=0.0, lecturing_volume_annual=10.0,
            practical_volume_annual=0.0, practical_volume_q2=0.0, practical_volume_q1=0.0,
            code='LTEST2027'
        )
        ue = _create_lu(ue_command)
        self.learning_unit_repository.save(ue)
        cmd = _build_create_effective_class_command(
            learning_unit_code=ue.code,
            class_code='T',
            volume_first_quadrimester=0,
            volume_second_quadrimester=0,
        )
        new_effective_class_identity = create_effective_class(
            cmd,
            self.learning_unit_repository,
            self.effective_class_repository
        )
        self.assertEqual(new_effective_class_identity.class_code, cmd.class_code)
        self.assertEqual(new_effective_class_identity.learning_unit_identity.code, ue_command.code)
        self.assertEqual(new_effective_class_identity.learning_unit_identity.year, ue_command.academic_year)

    def test_teaching_place_be_required(self):
        learning_unit = LDROI1001CourseLearningUnitFactory()
        self.learning_unit_repository.save(learning_unit)
        cmd = CreateEffectiveClassCommand(
            class_code="Z",
            learning_unit_code=learning_unit.code,
            year=learning_unit.year,
            volume_first_quadrimester=None,
            volume_second_quadrimester=None,
            title_fr='Fr',
            title_en='en',
            derogation_quadrimester=None,
            session_derogation=None,
            teaching_place_uuid=None
        )
        with self.assertRaises(MultipleBusinessExceptions) as class_exceptions:
            create_effective_class(
                cmd,
                self.learning_unit_repository,
                self.effective_class_repository
            )
        self.assertIsInstance(
            class_exceptions.exception.exceptions.pop(),
            TeachingPlaceRequiredException
        )

    def test_quadrimester_is_valid_choice(self):
        learning_unit = LDROI1001CourseLearningUnitFactory()
        self.learning_unit_repository.save(learning_unit)
        cmd = CreateEffectiveClassCommand(
            class_code="Z",
            learning_unit_code=learning_unit.code,
            year=learning_unit.year,
            volume_first_quadrimester=None,
            volume_second_quadrimester=None,
            title_fr='Fr',
            title_en='en',
            derogation_quadrimester="invalid choice",
            session_derogation=None,
            teaching_place_uuid=None
        )
        with self.assertRaises(MultipleBusinessExceptions) as class_exceptions:
            create_effective_class(
                cmd,
                self.learning_unit_repository,
                self.effective_class_repository
            )
        self.assertIsInstance(
            class_exceptions.exception.exceptions.pop(),
            DerogationQuadrimesterInvalidChoiceException
        )

    def test_session_is_valid_choice(self):
        learning_unit = LDROI1001CourseLearningUnitFactory()
        self.learning_unit_repository.save(learning_unit)
        cmd = CreateEffectiveClassCommand(
            class_code="Z",
            learning_unit_code=learning_unit.code,
            year=learning_unit.year,
            volume_first_quadrimester=None,
            volume_second_quadrimester=None,
            title_fr='Fr',
            title_en='en',
            derogation_quadrimester=None,
            session_derogation="invalid choice",
            teaching_place_uuid=None
        )
        with self.assertRaises(MultipleBusinessExceptions) as class_exceptions:
            create_effective_class(
                cmd,
                self.learning_unit_repository,
                self.effective_class_repository
            )
        self.assertIsInstance(
            class_exceptions.exception.exceptions.pop(),
            DerogationSessionInvalidChoiceException
        )


def _build_create_effective_class_command(
        learning_unit_code: str,
        class_code: str,
        volume_first_quadrimester: int = 10,
        volume_second_quadrimester: int = 10
) -> 'CreateEffectiveClassCommand':
    cmd = CreateEffectiveClassCommand(
        class_code=class_code,
        learning_unit_code=learning_unit_code,
        year=YEAR,
        volume_first_quadrimester=volume_first_quadrimester,
        volume_second_quadrimester=volume_second_quadrimester,
        title_fr='Fr',
        title_en='en',
        derogation_quadrimester='Q1',
        session_derogation=DerogationSession.DEROGATION_SESSION_123.value,
        teaching_place_uuid="35bbb236-7de6-4322-a496-fa8397054305"
    )
    return cmd


def _create_lu(command) -> 'LearningUnit':
    return LearningUnitBuilder.build_from_command(
        cmd=command,
        all_existing_identities=[],
        responsible_entity_identity=UclEntityIdentityBuilder.build_from_code(code='UCL')
    )


def _build_create_learning_unit_command() -> 'CreateLearningUnitCommand':
    return CreateLearningUnitCommand(
        code='LTEST2021',
        academic_year=YEAR,
        type=LearningContainerYearType.COURSE.name,
        common_title_fr='Common FR',
        specific_title_fr='Specific FR',
        common_title_en='Common EN',
        specific_title_en='Specific EN',
        credits=20,
        internship_subtype=None,
        responsible_entity_code='DRT',
        periodicity=PeriodicityEnum.ANNUAL.name,
        iso_code='fr-be',
        remark_faculty=None,
        remark_publication_fr=None,
        remark_publication_en=None,
        practical_volume_q1=10.0,
        practical_volume_q2=10.0,
        practical_volume_annual=20.0,
        lecturing_volume_q1=10.0,
        lecturing_volume_q2=10.0,
        lecturing_volume_annual=20.0,
        derogation_quadrimester=DerogationQuadrimester.Q1.name,
        teaching_place_uuid=None
    )
