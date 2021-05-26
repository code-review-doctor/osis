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
from typing import Type

from django.test import TestCase

from base.ddd.utils.business_validator import MultipleBusinessExceptions
from base.models.enums.learning_unit_year_session import SESSION_123
from ddd.logic.learning_unit.builder.learning_unit_identity_builder import LearningUnitIdentityBuilder
from ddd.logic.learning_unit.commands import CreateEffectiveClassCommand
from ddd.logic.learning_unit.domain.model._titles import Titles
from ddd.logic.learning_unit.domain.model._volumes_repartition import LecturingPart, Volumes, PracticalPart
from ddd.logic.learning_unit.domain.model.effective_class import LecturingEffectiveClass, PracticalEffectiveClass, \
    EffectiveClass, EffectiveClassIdentity
from ddd.logic.learning_unit.domain.model.learning_unit import LearningUnit, ExternalLearningUnit
from ddd.logic.learning_unit.domain.validator.exceptions import ShouldBeAlphanumericException, \
    CodeClassAlreadyExistForUeException, ClassTypeInvalidException, AnnualVolumeInvalidException
from ddd.logic.learning_unit.use_case.write.create_effective_class_service import create_effective_class
from infrastructure.learning_unit.repository.in_memory.effective_class import EffectiveClassRepository
from infrastructure.learning_unit.repository.in_memory.learning_unit import LearningUnitRepository

YEAR = 2020


class TestCreateClassServiceEffectiveClassType(TestCase):

    def setUp(self):
        self.learning_unit_repository = LearningUnitRepository()
        self.ue_with_lecturing_and_practical_volumes = _create_lu(
            ue_type=LearningUnit,
            learning_unit_code="LCOMU1012",
            lecturing_part=LecturingPart(volumes=_build_not_zero_volumes()),
            practical_part=PracticalPart(volumes=_build_not_zero_volumes())
        )
        self.ue_with_practical_volumes_only = _create_lu(
            ue_type=LearningUnit,
            learning_unit_code='LDRT1012',
            lecturing_part=LecturingPart(volumes=_build_zero_volumes()),
            practical_part=PracticalPart(volumes=_build_not_zero_volumes())
        )

        self.ue_with_lecturing_volumes_only = _create_lu(
            ue_type=LearningUnit,
            learning_unit_code='LPOIO1256',
            lecturing_part=LecturingPart(volumes=_build_not_zero_volumes()),
            practical_part=PracticalPart(volumes=_build_zero_volumes())
        )

        self.learning_unit_repository.learning_units.extend([
            self.ue_with_lecturing_and_practical_volumes,
            self.ue_with_practical_volumes_only,
            self.ue_with_lecturing_volumes_only
        ])

        self.effective_class_repository = EffectiveClassRepository()

    def test_effective_class_type_lecturing(self):
        effective_class_id = create_effective_class(
            _build_command(learning_unit_code=self.ue_with_lecturing_and_practical_volumes.code, class_code='A'),
            self.learning_unit_repository,
            self.effective_class_repository
        )
        effective_class = self.effective_class_repository.get(effective_class_id)
        self.assertIsInstance(effective_class, LecturingEffectiveClass)

    def test_effective_class_type_practical(self):
        effective_class_id = create_effective_class(
            _build_command(learning_unit_code=self.ue_with_practical_volumes_only.code, class_code='C'),
            self.learning_unit_repository,
            self.effective_class_repository
        )
        effective_class = self.effective_class_repository.get(effective_class_id)
        self.assertIsInstance(effective_class, PracticalEffectiveClass)

    def test_effective_class_type_lecturing_only(self):
        effective_class_id = create_effective_class(
            _build_command(learning_unit_code=self.ue_with_lecturing_volumes_only.code, class_code='B'),
            self.learning_unit_repository,
            self.effective_class_repository
        )
        effective_class = self.effective_class_repository.get(effective_class_id)
        self.assertIsInstance(effective_class, LecturingEffectiveClass)


class TestCreateClassServiceValidator(TestCase):
    def setUp(self):
        self.learning_unit_repository = LearningUnitRepository()
        self.ue_with_lecturing_and_practical_volumes = _create_lu(
            ue_type=LearningUnit,
            learning_unit_code="LCOMU1012",
            lecturing_part=LecturingPart(volumes=_build_not_zero_volumes()),
            practical_part=PracticalPart(volumes=_build_not_zero_volumes())
        )
        self.ue_external = _create_lu(
            ue_type=ExternalLearningUnit,
            learning_unit_code="ECOMU1002",
            lecturing_part=LecturingPart(volumes=_build_not_zero_volumes()),
            practical_part=PracticalPart(volumes=_build_not_zero_volumes())
        )
        self.ue_no_volumes = _create_lu(
            ue_type=LearningUnit,
            learning_unit_code="LPSP8002",
            lecturing_part=LecturingPart(volumes=_build_zero_volumes()),
            practical_part=PracticalPart(volumes=_build_zero_volumes()),
            credits=0
        )
        self.learning_unit_repository.learning_units.extend([
            self.ue_with_lecturing_and_practical_volumes,
            self.ue_external,
            self.ue_no_volumes
        ])

        self.effective_class_repository = EffectiveClassRepository()
        effective_class_identity = EffectiveClassIdentity(
            class_code='A',
            learning_unit_identity=LearningUnitIdentityBuilder.build_from_code_and_year(
                code=self.ue_with_lecturing_and_practical_volumes.code,
                year=YEAR
            )
        )

        self.effective_class = EffectiveClass(
            entity_id=effective_class_identity,
            titles=None,
            teaching_place=None,
            derogation_quadrimester=None,
            session_derogation=None,
            volumes=None
        )
        self.effective_class_repository.effective_classes.append(
            self.effective_class
        )

    def test_class_code_raise_should_be_alphanumeric_exception(self):
        cmd = _build_command(learning_unit_code=self.ue_with_lecturing_and_practical_volumes.code, class_code='*')
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
        cmd = _build_command(learning_unit_code=self.ue_with_lecturing_and_practical_volumes.code,
                             class_code=already_existing_class_code)
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
        cmd = _build_command(learning_unit_code=self.ue_external.code, class_code='B')
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

    def test_raise_check_class_volumes_consistency_exception(self):
        cmd = _build_command(learning_unit_code=self.ue_no_volumes.code, class_code='C', credits=0)
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


def _build_command(learning_unit_code: str, class_code: str, credits: float = 20) -> CreateEffectiveClassCommand:
    cmd = CreateEffectiveClassCommand(
        class_code=class_code,
        learning_unit_code=learning_unit_code,
        year=YEAR,
        volume_first_quadrimester=10,
        volume_second_quadrimester=10,
        volume_annual=credits,
        title_fr='Fr',
        title_en='en',
        place=None,
        organization_name=None,
        derogation_quadrimester='Q1',
        session_derogation=SESSION_123
    )
    return cmd


def _create_lu(
        ue_type: Type,
        learning_unit_code: str,
        lecturing_part: LecturingPart,
        practical_part: PracticalPart,
        credits: float = 20
):
    #  TODO remplacer par le builder
    return ue_type(
        entity_id=LearningUnitIdentityBuilder.build_from_code_and_year(learning_unit_code, year=YEAR),
        titles=Titles(
            common_fr='Common fr',
            specific_fr='specific fr',
            common_en="common_en",
            specific_en="speci en"),
        credits=credits,
        internship_subtype=None,
        responsible_entity_identity=None,
        periodicity=None,
        language_id=None,
        remarks=None,
        partims=list(),
        derogation_quadrimester='Q1',
        lecturing_part=lecturing_part,
        practical_part=practical_part
    )


def _build_zero_volumes():
    return Volumes(
        volume_first_quadrimester=0.0,
        volume_second_quadrimester=0.0,
        volume_annual=0.0
    )


def _build_not_zero_volumes():
    return Volumes(
        volume_first_quadrimester=10.0,
        volume_second_quadrimester=10.0,
        volume_annual=20.0
    )
