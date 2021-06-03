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

from django.test import SimpleTestCase

from base.models.enums.learning_container_year_types import LearningContainerYearType
from base.models.enums.learning_unit_year_periodicity import PeriodicityEnum
from base.models.enums.quadrimesters import DerogationQuadrimester
from ddd.logic.learning_unit.builder.learning_unit_builder import LearningUnitBuilder
from ddd.logic.learning_unit.commands import CreateLearningUnitCommand, GetLearningUnitCommand
from ddd.logic.learning_unit.test.factory.ucl_entity import DRTEntityFactory
from ddd.logic.learning_unit.use_case.read import get_learning_unit_service
from infrastructure.learning_unit.repository.in_memory.learning_unit import LearningUnitRepository


class TestGetLearningUnitService(SimpleTestCase):

    def setUp(self):
        self.learning_unit_repository = LearningUnitRepository()
        self.fac_drt = DRTEntityFactory()
        lu_command = _get_create_learning_unit_command()
        self.learning_unit = LearningUnitBuilder.build_from_command(
            cmd=lu_command,
            all_existing_identities=[],
            responsible_entity_identity=self.fac_drt.entity_id
        )
        self.learning_unit_repository.save(self.learning_unit)
        self.command = GetLearningUnitCommand(code=self.learning_unit.code, year=self.learning_unit.year)

    def test_mapping_command_to_domain_obj(self):
        learning_unit = get_learning_unit_service.get_learning_unit(
            self.command,
            self.learning_unit_repository,
        )
        self.assertEqual(learning_unit, self.learning_unit)
        fields = vars(self.learning_unit)
        for field in fields:
            self.assertEqual(getattr(learning_unit, field), getattr(self.learning_unit, field), field)


def _get_create_learning_unit_command():
    lu_command = CreateLearningUnitCommand(
        code="LDROI1001",
        academic_year=2020,
        type=LearningContainerYearType.COURSE.name,
        common_title_fr="Introduction au droit",
        specific_title_fr="Partie 1 : droit civil",
        common_title_en="Introduction to law",
        specific_title_en="Part 1 : civic law",
        credits=7.0,
        internship_subtype=None,
        responsible_entity_code=self.fac_drt.entity_id.code,
        periodicity=PeriodicityEnum.ANNUAL.name,
        iso_code="fr-be",
        remark_faculty="Remark fac",
        remark_publication_fr="Remarqué publiée sur le portail",
        remark_publication_en="Remark published",
        practical_volume_q1=5.0,
        practical_volume_q2=15.0,
        practical_volume_annual=20.0,
        lecturing_volume_q1=25.0,
        lecturing_volume_q2=35.0,
        lecturing_volume_annual=60.0,
        derogation_quadrimester=DerogationQuadrimester.Q1and2.name,
        teaching_place_uuid=None
    )
    return lu_command
