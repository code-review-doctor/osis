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

from base.models.enums import organization_type
from base.models.enums.learning_container_year_types import LearningContainerYearType
from base.models.enums.learning_unit_year_periodicity import PeriodicityEnum
from base.models.enums.quadrimesters import DerogationQuadrimester
from base.tests.factories.campus import CampusFactory
from ddd.logic.learning_unit.commands import CreateLearningUnitCommand
from ddd.logic.learning_unit.tests.factory.ucl_entity import DRTEntityFactory
from ddd.logic.learning_unit.use_case.write import create_learning_unit_service
from infrastructure.learning_unit.repository.in_memory.learning_unit import LearningUnitRepository
from infrastructure.learning_unit.repository.in_memory.ucl_entity import UclEntityRepository


class TestCreateLearningUnitService(TestCase):

    def setUp(self):
        self.learning_unit_repository = LearningUnitRepository()
        self.learning_unit_repository.entities.clear()
        self.entity_repository = UclEntityRepository()
        self.fac_drt = DRTEntityFactory()
        self.entity_repository.save(self.fac_drt)
        campus = CampusFactory(organization__type=organization_type.MAIN)
        self.command = CreateLearningUnitCommand(
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
            teaching_place_uuid=campus.uuid
        )

    def test_mapping_command_to_domain_obj(self):
        cmd = self.command
        identity = create_learning_unit_service.create_learning_unit(
            cmd,
            self.learning_unit_repository,
            self.entity_repository
        )
        persisted_learning_unit = self.learning_unit_repository.get(identity)
        self.assertEqual(persisted_learning_unit.entity_id.code, cmd.code)
        self.assertEqual(persisted_learning_unit.entity_id.year, cmd.academic_year)

        self.assertEqual(persisted_learning_unit.type.name, cmd.type)
        self.assertEqual(persisted_learning_unit.titles.common_fr, cmd.common_title_fr)
        self.assertEqual(persisted_learning_unit.titles.specific_fr, cmd.specific_title_fr)
        self.assertEqual(persisted_learning_unit.titles.common_en, cmd.common_title_en)
        self.assertEqual(persisted_learning_unit.titles.specific_en, cmd.specific_title_en)
        self.assertEqual(persisted_learning_unit.credits, cmd.credits)
        self.assertIsNone(persisted_learning_unit.internship_subtype)
        self.assertEqual(persisted_learning_unit.responsible_entity_identity.code, cmd.responsible_entity_code)
        self.assertEqual(persisted_learning_unit.periodicity.name, cmd.periodicity)
        self.assertEqual(persisted_learning_unit.language_id.code_iso, cmd.iso_code)

        self.assertEqual(persisted_learning_unit.remarks.publication_fr, cmd.remark_publication_fr)
        self.assertEqual(persisted_learning_unit.remarks.publication_en, cmd.remark_publication_en)

        volumes_lecturing = persisted_learning_unit.lecturing_part.volumes
        self.assertEqual(volumes_lecturing.volume_annual, cmd.lecturing_volume_annual)
        self.assertEqual(volumes_lecturing.volume_first_quadrimester, cmd.lecturing_volume_q1)
        self.assertEqual(volumes_lecturing.volume_second_quadrimester, cmd.lecturing_volume_q2)

        volumes_practical = persisted_learning_unit.practical_part.volumes
        self.assertEqual(volumes_practical.volume_annual, cmd.practical_volume_annual)
        self.assertEqual(volumes_practical.volume_first_quadrimester, cmd.practical_volume_q1)
        self.assertEqual(volumes_practical.volume_second_quadrimester, cmd.practical_volume_q2)

        self.assertEqual(persisted_learning_unit.derogation_quadrimester.name, cmd.derogation_quadrimester)

    def test_mapping_when_practical_volume_is_none(self):
        cmd = attr.evolve(
            self.command,
            code="LDROI1002",
            practical_volume_q1=None,
            practical_volume_q2=None,
            practical_volume_annual=None,
        )
        identity = create_learning_unit_service.create_learning_unit(
            cmd,
            self.learning_unit_repository,
            self.entity_repository
        )
        persisted_learning_unit = self.learning_unit_repository.get(identity)
        self.assertIsNone(persisted_learning_unit.practical_part)

    def test_mapping_when_practical_volume_is_0(self):
        cmd = attr.evolve(
            self.command,
            code="LDROI1003",
            practical_volume_q1=0.0,
            practical_volume_q2=0.0,
            practical_volume_annual=0.0,
        )
        identity = create_learning_unit_service.create_learning_unit(
            cmd,
            self.learning_unit_repository,
            self.entity_repository
        )
        persisted_learning_unit = self.learning_unit_repository.get(identity)
        self.assertIsNone(persisted_learning_unit.practical_part)
