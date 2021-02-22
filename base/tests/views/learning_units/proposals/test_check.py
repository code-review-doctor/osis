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
import json

from django.test import TestCase
from rest_framework.reverse import reverse

from base.models.enums import learning_unit_year_subtypes, \
    learning_container_year_types
from base.tests.factories.academic_year import create_current_academic_year
from base.tests.factories.learning_container_year import LearningContainerYearFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory, LearningUnitYearPartimFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.proposal_learning_unit import ProposalLearningUnitFactory


class TestCheck(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.current_academic_year = create_current_academic_year()
        cls.learning_container_year = LearningContainerYearFactory(
            academic_year=cls.current_academic_year,
            container_type=learning_container_year_types.COURSE
        )

        cls.learning_unit_year = LearningUnitYearFactory(
            learning_container_year=cls.learning_container_year,
            acronym="LOSIS4512",
            academic_year=cls.current_academic_year,
            subtype=learning_unit_year_subtypes.FULL,
            credits=15,
            internship_subtype=None,
        )

        cls.partim_learning_unit = LearningUnitYearPartimFactory(
            learning_container_year=cls.learning_container_year,
            acronym="LOSIS4512A",
            academic_year=cls.current_academic_year,

        )
        cls.partim_learning_unit = LearningUnitYearPartimFactory(
            learning_container_year=cls.learning_container_year,
            acronym="LOSIS4512B",
            academic_year=cls.current_academic_year,

        )

        cls.proposal_on_luy1 = ProposalLearningUnitFactory(
             learning_unit_year=cls.learning_unit_year,
         )

        cls.learning_container_year2 = LearningContainerYearFactory(
            academic_year=cls.current_academic_year,
            container_type=learning_container_year_types.COURSE
        )
        cls.learning_unit_year_without_partim = LearningUnitYearFactory(
            learning_container_year=cls.learning_container_year2,
            academic_year=cls.current_academic_year,
            subtype=learning_unit_year_subtypes.FULL,
            credits=15,
            internship_subtype=None,
        )
        cls.proposal_on_ue_without_partim = ProposalLearningUnitFactory(
             learning_unit_year=cls.learning_unit_year_without_partim,
         )
        cls.person = PersonFactory()
        cls.url_name = 'get_related_partims_by_ue'

    def setUp(self):
        self.client.force_login(self.person.user)

    def test_get_related_partims_by_ue_with_partim(self):
        response = self.client.post(reverse(self.url_name), HTTP_X_REQUESTED_WITH='XMLHttpRequest',
                                    data={'selected_action': [self.learning_unit_year.acronym]})
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.content.decode("utf-8"))
        self.assertDictEqual(list(json_response)[0],
                             {"learning_unit_year": "LOSIS4512", "partims": "LOSIS4512A, LOSIS4512B"}
                             )

    def test_get_related_partims_by_ue_without_partim(self):
        response = self.client.post(reverse(self.url_name), HTTP_X_REQUESTED_WITH='XMLHttpRequest',
                                    data={'selected_action': [self.learning_unit_year_without_partim.acronym]})
        self.assertEqual(response.status_code, 200)

        json_response = str(response.content, encoding='utf8')
        self.assertEqual(json_response, '[]')
