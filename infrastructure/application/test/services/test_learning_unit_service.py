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

from attribution.models.enums.function import Functions
from attribution.tests.factories.attribution_charge_new import AttributionChargeNewFactory
from base.models.enums import learning_component_year_type
from base.tests.factories.learning_component_year import LecturingLearningComponentYearFactory, \
    PracticalLearningComponentYearFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFullFactory, LearningUnitYearPartimFactory
from base.tests.factories.tutor import TutorFactory
from ddd.logic.application.dtos import LearningUnitVolumeFromServiceDTO, LearningUnitTutorAttributionFromServiceDTO
from ddd.logic.learning_unit.domain.model.learning_unit import LearningUnitIdentity
from ddd.logic.shared_kernel.academic_year.builder.academic_year_identity_builder import AcademicYearIdentityBuilder
from infrastructure.application.services.learning_unit_service import LearningUnitTranslator


class LearningUnitTranslatorSearchLearningUnitVolumes(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.ldroi1200 = LearningUnitYearFullFactory(
            acronym='LDROI1200',
            academic_year__year=2018,
            learning_container_year__acronym='LDROI1200',
            learning_container_year__academic_year__year=2018,
        )
        LecturingLearningComponentYearFactory(learning_unit_year=cls.ldroi1200, hourly_volume_total_annual=Decimal(30))
        PracticalLearningComponentYearFactory(learning_unit_year=cls.ldroi1200, hourly_volume_total_annual=Decimal(5))

        cls.lagro2000 = LearningUnitYearFullFactory(
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
            LearningUnitVolumeFromServiceDTO(
                code="LDROI1200",
                year=2018,
                lecturing_volume_total=Decimal(30),
                practical_volume_total=Decimal(5),
            ),
            results
        )

        self.assertIn(
            LearningUnitVolumeFromServiceDTO(
                code="LAGRO2000",
                year=2018,
                lecturing_volume_total=Decimal(5),
                practical_volume_total=Decimal(0),
            ),
            results
        )


class LearningUnitTranslatorSearchTutorAttribution(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.ldroi1200 = LearningUnitYearFullFactory(
            acronym='LDROI1200',
            academic_year__year=2018,
            learning_container_year__acronym='LDROI1200',
            learning_container_year__academic_year__year=2018,
        )
        cls.tutor = TutorFactory()

        cls.practical_volume_assigned = AttributionChargeNewFactory(
            attribution__tutor=cls.tutor,
            attribution__function=Functions.CO_HOLDER.name,
            attribution__learning_container_year=cls.ldroi1200.learning_container_year,
            learning_component_year__type=learning_component_year_type.PRACTICAL_EXERCISES,
            learning_component_year__learning_unit_year=cls.ldroi1200,
            allocation_charge=10
        )

        cls.ldroi1200a = LearningUnitYearPartimFactory(
            acronym='LDROI1200A',
            academic_year=cls.ldroi1200.academic_year,
            learning_container_year=cls.ldroi1200.learning_container_year
        )
        cls.practical_volume_assigned_on_partim = AttributionChargeNewFactory(
            attribution__tutor=cls.tutor,
            attribution__function=Functions.CO_HOLDER.name,
            attribution__learning_container_year=cls.ldroi1200a.learning_container_year,
            learning_component_year__type=learning_component_year_type.PRACTICAL_EXERCISES,
            learning_component_year__learning_unit_year=cls.ldroi1200a,
            allocation_charge=15
        )

        cls.service = LearningUnitTranslator()

    def test_should_return_only_attribution_of_learning_unit_full_type(self):
        learning_unit_ids = [
            LearningUnitIdentity(code='LDROI1200', academic_year=AcademicYearIdentityBuilder.build_from_year(2018)),
        ]

        results = self.service.search_tutor_attribution_dto(learning_unit_ids)
        self.assertEqual(len(results), 1)

        self.assertEqual(
            results[0],
            LearningUnitTutorAttributionFromServiceDTO(
                code='LDROI1200',
                year=2018,
                first_name=self.tutor.person.first_name,
                last_name=self.tutor.person.last_name,
                function=Functions.CO_HOLDER.name,
                lecturing_volume=Decimal(0),
                practical_volume=Decimal(10),
            )
        )
