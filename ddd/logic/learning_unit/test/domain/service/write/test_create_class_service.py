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
from django.test import TestCase

from ddd.logic.learning_unit.commands import CreateEffectiveClassCommand
from ddd.logic.learning_unit.domain.model._titles import Titles
from ddd.logic.learning_unit.domain.model._volumes_repartition import LecturingPart, Volumes, PracticalPart, Duration
from ddd.logic.learning_unit.domain.model.effective_class import LecturingEffectiveClass, PracticalEffectiveClass
from ddd.logic.learning_unit.domain.model.learning_unit import LearningUnitIdentity, LearningUnit
from ddd.logic.learning_unit.use_case.write.create_effective_class_service import create_effective_class

from infrastructure.learning_unit.repository.in_memory.effective_class import EffectiveClassRepository
from infrastructure.learning_unit.repository.in_memory.learning_unit import LearningUnitRepository
from ddd.logic.shared_kernel.academic_year.domain.model.academic_year import AcademicYearIdentity
from base.models.enums.learning_unit_year_session import SESSION_123

YEAR = 2020


class TestCreateClassService(TestCase):

    def setUp(self):
        self.learning_unit_repository = LearningUnitRepository()
        self.ue_with_lecturing_and_practical_volumes = _create_lu(
            code="LCOMU1012",
            lecturing_part=LecturingPart(volumes=_build_not_zero_volumes()),
            practical_part=PracticalPart(volumes=_build_not_zero_volumes())
        )
        self.ue_with_practical_volumes_only = _create_lu(
            code='LDRT1012',
            lecturing_part=LecturingPart(volumes=_build_zero_volumes()),
            practical_part=PracticalPart(volumes=_build_not_zero_volumes())
        )

        self.ue_with_lecturing_volumes_only = _create_lu(
            code='LPOIO1256',
            lecturing_part=LecturingPart(volumes=_build_not_zero_volumes()),
            practical_part=PracticalPart(volumes=_build_zero_volumes())
        )

        self.learning_unit_repository.learning_units.extend([
            self.ue_with_lecturing_and_practical_volumes,
            self.ue_with_practical_volumes_only,
            self.ue_with_lecturing_volumes_only
            ]
        )

        self.effective_class_repository = EffectiveClassRepository()

    def test_effective_class_type_lecturing(self):
        effective_class = create_effective_class(
            _build_command(self.ue_with_lecturing_and_practical_volumes.code),
            self.learning_unit_repository,
            self.effective_class_repository
        )
        self.assertIsInstance(effective_class, LecturingEffectiveClass)

    def test_effective_class_type_practical(self):
        effective_class = create_effective_class(
            _build_command(self.ue_with_practical_volumes_only.code),
            self.learning_unit_repository,
            self.effective_class_repository
        )
        self.assertIsInstance(effective_class, PracticalEffectiveClass)

    def test_effective_class_type_lecturing_only(self):
        effective_class = create_effective_class(
            _build_command(self.ue_with_lecturing_volumes_only.code),
            self.learning_unit_repository,
            self.effective_class_repository
        )
        self.assertIsInstance(effective_class, LecturingEffectiveClass)


def _build_command(code: str) -> CreateEffectiveClassCommand:
    cmd = CreateEffectiveClassCommand(
        class_code="A",
        learning_unit_code=code,
        year=YEAR,
        volume_first_quadrimester_hours=10,
        volume_first_quadrimester_minutes=0,
        volume_second_quadrimester_hours=10,
        volume_second_quadrimester_minutes=0,
        volume_annual_quadrimester_hours=20,
        volume_annual_quadrimester_minutes=0,
        title_fr='Fr',
        title_en='en',
        place=None,
        organization_name=None,
        derogation_quadrimester='Q1',
        session_derogation=SESSION_123
    )
    return cmd


def _create_lu(code, lecturing_part, practical_part):
    return LearningUnit(
        entity_id=LearningUnitIdentity(code=code, academic_year=AcademicYearIdentity(year=YEAR)),
        titles=Titles(common_fr='Common fr', specific_fr='specific fr', common_en="common_en",
                      specific_en="speci en"), credits=20, internship_subtype=None,
        responsible_entity_identity=None, periodicity=None, language_id=None, remarks=None, partims=list(),
        derogation_quadrimester=None, lecturing_part=lecturing_part, practical_part=practical_part)


def _build_zero_volumes():
    return Volumes(
        volume_first_quadrimester=Duration(hours=0, minutes=0),
        volume_second_quadrimester=Duration(hours=0, minutes=0),
        volume_annual=Duration(hours=0, minutes=0)
    )


def _build_not_zero_volumes():
    return Volumes(
        volume_first_quadrimester=Duration(hours=10, minutes=0),
        volume_second_quadrimester=Duration(hours=10, minutes=0),
        volume_annual=Duration(hours=20, minutes=0)
    )
