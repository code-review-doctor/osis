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
from decimal import Decimal

from django.test import TestCase

from base.tests.factories.learning_component_year import LecturingLearningComponentYearFactory, \
    PracticalLearningComponentYearFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from ddd.logic.application.dtos import LearningUnitVolumeDTO
from ddd.logic.learning_unit.domain.model.learning_unit import LearningUnitIdentity
from ddd.logic.shared_kernel.academic_year.builder.academic_year_identity_builder import AcademicYearIdentityBuilder
from infrastructure.application.services.learning_unit_service import LearningUnitTranslator


class LearningUnitTranslatorSearchLearningUnitVolumes(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.ldroi1200 = LearningUnitYearFactory(
            acronym='LDROI1200',
            academic_year__year=2018,
            learning_container_year__acronym='LDROI1200',
            learning_container_year__academic_year__year=2018
        )
        LecturingLearningComponentYearFactory(learning_unit_year=cls.ldroi1200, hourly_volume_total_annual=Decimal(30))
        PracticalLearningComponentYearFactory(learning_unit_year=cls.ldroi1200, hourly_volume_total_annual=Decimal(5))

        cls.lagro2000 = LearningUnitYearFactory(
            acronym='LAGRO2000',
            academic_year__year=2018,
            learning_container_year__acronym='LAGRO2000',
            learning_container_year__academic_year__year=2018
        )
        LecturingLearningComponentYearFactory(learning_unit_year=cls.lagro2000, hourly_volume_total_annual=Decimal(5))

        cls.service = LearningUnitTranslator()

    def test_should_return_learning_unit_volumes_dto(self):
        learning_unit_ids = [
            LearningUnitIdentity(code='LDROI1200', academic_year=AcademicYearIdentityBuilder.build_from_year(2018)),
            LearningUnitIdentity(code='LAGRO2000', academic_year=AcademicYearIdentityBuilder.build_from_year(2018))
        ]

        results = self.service.search_learning_unit_volumes_dto(learning_unit_ids)
        self.assertEqual(len(results), 2)

        self.assertIn(
            LearningUnitVolumeDTO(
                code="LDROI1200",
                year=2018,
                lecturing_volume_total=Decimal(30),
                practical_volume_total=Decimal(5),
            ),
            results
        )

        self.assertIn(
            LearningUnitVolumeDTO(
                code="LAGRO2000",
                year=2018,
                lecturing_volume_total=Decimal(5),
                practical_volume_total=Decimal(0),
            ),
            results
        )
