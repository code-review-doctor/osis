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
from unittest import mock

from django.test import TestCase

from base.ddd.utils.business_validator import MultipleBusinessExceptions
from base.models.enums.learning_container_year_types import LearningContainerYearType
from base.models.enums.learning_unit_year_periodicity import PeriodicityEnum
from base.models.enums.quadrimesters import DerogationQuadrimester
from ddd.logic.learning_unit.builder.learning_unit_builder import LearningUnitBuilder
from ddd.logic.learning_unit.builder.ucl_entity_identity_builder import UclEntityIdentityBuilder
from ddd.logic.learning_unit.commands import CanCreateEffectiveClassCommand, CreateLearningUnitCommand
from ddd.logic.learning_unit.domain.model.learning_unit import LearningUnit
from ddd.logic.learning_unit.use_case.read.check_can_create_class_service import check_can_create_effective_class
from infrastructure.learning_unit.repository.in_memory.learning_unit import LearningUnitRepository


class TestCheckCanCreateEffectiveClass(TestCase):

    def setUp(self):
        self.code = 'LTEST2021'
        self.year = 2020
        self.cmd = CanCreateEffectiveClassCommand(learning_unit_code=self.code, learning_unit_year=self.year)

        self.learning_unit_repository = LearningUnitRepository()

        self.create_lu_command = _build_create_learning_unit_command(self.code, self.year)
        self.learning_unit = _create_lu(self.create_lu_command)

    @mock.patch.object(LearningUnitRepository, 'get')
    def test_check_cannot_create_effective_class(self, mock_lu):
        with self.assertRaises(MultipleBusinessExceptions):
            check_can_create_effective_class(self.cmd, self.learning_unit_repository)

    @mock.patch.object(LearningUnitRepository, 'get')
    def test_check_can_create_effective_class(self, mock_lu):
        mock_lu.return_value = self.learning_unit
        self.assertIsNone(check_can_create_effective_class(self.cmd, self.learning_unit_repository))


def _create_lu(command) -> 'LearningUnit':
    return LearningUnitBuilder.build_from_command(
        cmd=command,
        all_existing_identities=[],
        responsible_entity_identity=UclEntityIdentityBuilder.build_from_code(code='UCL')
    )


def _build_create_learning_unit_command(code: str, year: int) -> 'CreateLearningUnitCommand':
    return CreateLearningUnitCommand(
        code=code,
        academic_year=year,
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
        derogation_quadrimester=DerogationQuadrimester.Q1.name
    )
