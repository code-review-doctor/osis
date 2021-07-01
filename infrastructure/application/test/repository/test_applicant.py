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

from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase

from attribution.models.enums.function import Functions
from attribution.tests.factories.attribution_charge_new import AttributionChargeNewFactory
from base.models.enums import learning_component_year_type
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.tutor import TutorFactory
from ddd.logic.application.domain.model.applicant import ApplicantIdentity, Applicant
from ddd.logic.application.domain.model._attribution import Attribution
from ddd.logic.learning_unit.domain.model.learning_unit import LearningUnitIdentity
from ddd.logic.shared_kernel.academic_year.domain.model.academic_year import AcademicYearIdentity
from infrastructure.application.repository.applicant import ApplicantRepository


class ApplicantRepositoryGet(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.global_id = '7989898985'
        cls.tutor_db = TutorFactory(person__global_id=cls.global_id)
        cls.ldroi1200 = LearningUnitYearFactory(
            acronym='LDROI1200',
            academic_year__year=2018,
            learning_container_year__acronym='LDROI1200',
            learning_container_year__academic_year__year=2018
        )

        cls.attribution_practical_ldroi1200 = AttributionChargeNewFactory(
            attribution__tutor=cls.tutor_db,
            attribution__end_year=2020,
            attribution__learning_container_year=cls.ldroi1200.learning_container_year,
            attribution__substitute=None,
            learning_component_year__learning_unit_year=cls.ldroi1200,
            learning_component_year__type=learning_component_year_type.PRACTICAL_EXERCISES,
            allocation_charge=Decimal(9.5)
        )
        cls.repository = ApplicantRepository()

    def test_get_assert_return_not_found(self):
        applicant_id_unknown = ApplicantIdentity(global_id="5656892656")
        with self.assertRaises(ObjectDoesNotExist):
            self.repository.get(applicant_id_unknown)

    def test_get_assert_return_instance(self):
        applicant_id = ApplicantIdentity(global_id=self.global_id)
        applicant = self.repository.get(applicant_id)

        self.assertIsInstance(applicant, Applicant)
        self.assertEqual(applicant.entity_id, applicant_id)
        self.assertEqual(applicant.first_name, self.tutor_db.person.first_name)
        self.assertEqual(applicant.last_name, self.tutor_db.person.last_name)

        self.assertEqual(len(applicant.attributions), 1)
        expected_attribution = Attribution(
            course_id=LearningUnitIdentity(code="LDROI1200", academic_year=AcademicYearIdentity(year=2018)),
            course_title=self.ldroi1200.learning_container_year.common_title + " - " + self.ldroi1200.specific_title,
            function=Functions[self.attribution_practical_ldroi1200.attribution.function],
            end_year=AcademicYearIdentity(year=self.attribution_practical_ldroi1200.attribution.end_year),
            start_year=AcademicYearIdentity(year=self.attribution_practical_ldroi1200.attribution.start_year),
            lecturing_volume=None,
            practical_volume=self.attribution_practical_ldroi1200.allocation_charge,
            is_substitute=False
        )
        self.assertEqual(applicant.attributions[0], expected_attribution)


class ApplicantRepositorySearch(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.ldroi1200 = LearningUnitYearFactory(
            acronym='LDROI1200',
            academic_year__year=2018,
            learning_container_year__acronym='LDROI1200',
            learning_container_year__academic_year__year=2018
        )

        cls.tutors_db = []
        for index in range(1, 3):
            tutor_db = TutorFactory(person__global_id="564689797" + str(index))
            AttributionChargeNewFactory(
                attribution__tutor=tutor_db,
                attribution__end_year=2020,
                attribution__learning_container_year=cls.ldroi1200.learning_container_year,
                learning_component_year__learning_unit_year=cls.ldroi1200,
                learning_component_year__type=learning_component_year_type.PRACTICAL_EXERCISES,
                allocation_charge=Decimal(index)
            )
            cls.tutors_db.append(tutor_db)

        cls.repository = ApplicantRepository()

    def test_search_without_filtering_assert_return_multiple_instances(self):
        results = self.repository.search()

        self.assertEqual(len(results), len(self.tutors_db))

        results_ids = [applicant.entity_id for applicant in results]
        self.assertIn(
            ApplicantIdentity(global_id=self.tutors_db[0].person.global_id),
            results_ids
        )
        self.assertIn(
            ApplicantIdentity(global_id=self.tutors_db[1].person.global_id),
            results_ids
        )
