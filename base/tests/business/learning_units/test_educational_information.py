##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2018 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
import datetime
from unittest.mock import patch

from base.business.learning_unit_proposal import compute_proposal_type
from base.tests.factories.person import PersonFactory
from base.tests.factories.proposal_learning_unit import ProposalLearningUnitFactory
from base.business import learning_unit_proposal as lu_proposal_business
from base import models as mdl_base

from django.test import TestCase, SimpleTestCase

from base.models.enums import organization_type, proposal_type, entity_type, \
    learning_container_year_types, entity_container_year_link_type, \
    learning_unit_year_subtypes, proposal_state
from base.tests.factories.academic_year import create_current_academic_year
from base.tests.factories.campus import CampusFactory
from base.tests.factories.entity import EntityFactory
from base.tests.factories.entity_container_year import EntityContainerYearFactory
from base.tests.factories.entity_version import EntityVersionFactory
from base.tests.factories.learning_container_year import LearningContainerYearFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFakerFactory
from base.tests.factories.organization import OrganizationFactory
from base.tests.factories.academic_year import create_current_academic_year

from attribution.tests.factories.attribution import AttributionFactory
from base.business.learning_units.educational_information import get_responsible_and_learning_unit_yr_list, PERSON, LEARNING_UNIT_YEARS
from base.tests.factories.tutor import TutorFactory


class TestEducationalInformation(TestCase):

    def setUp(self):
        self.learning_unit_year_1 = LearningUnitYearFakerFactory()
        self.person_lu_1 = PersonFactory()
        self.tutor_lu1_1 = TutorFactory(person=self.person_lu_1)
        self.attribution_lu1 = AttributionFactory(learning_unit_year=self.learning_unit_year_1, tutor=self.tutor_lu1_1)
        self.learning_unit_year_1.summary_status=False
        self.learning_unit_year_1.summary_responsibles=[self.attribution_lu1]

        self.learning_unit_year_2 = LearningUnitYearFakerFactory()
        self.person_lu_2 = PersonFactory()
        self.tutor_lu1_2_1 = TutorFactory(person=self.person_lu_2)
        self.person_lu_3 = PersonFactory()
        self.tutor_lu2_2_2 = TutorFactory(person=self.person_lu_3)
        self.attribution_lu2_1 = AttributionFactory(learning_unit_year=self.learning_unit_year_2, tutor=self.tutor_lu1_2_1)
        self.attribution_lu2_2 = AttributionFactory(learning_unit_year=self.learning_unit_year_2, tutor=self.tutor_lu2_2_2)
        self.learning_unit_year_2.summary_status=False
        self.learning_unit_year_2.summary_responsibles=[self.attribution_lu2_1, self.attribution_lu2_2]

        self.learning_unit_year_3 = LearningUnitYearFakerFactory()
        self.attribution_lu3 = AttributionFactory(learning_unit_year=self.learning_unit_year_3, tutor=self.tutor_lu1_1)
        self.learning_unit_year_3.summary_status=False
        self.learning_unit_year_3.summary_responsibles=[self.attribution_lu3]

    def test_get_learning_unit_yr_list_with_one_responsible(self):
        learning_units = get_responsible_and_learning_unit_yr_list([self.learning_unit_year_1])
        self.assertCountEqual(learning_units, [
            {PERSON: self.attribution_lu1.tutor.person, LEARNING_UNIT_YEARS: [self.learning_unit_year_1]}])

    def test_get_learning_unit_yr_list_with_two_responsibles(self):
        learning_units = get_responsible_and_learning_unit_yr_list([self.learning_unit_year_2])
        self.assertCountEqual(learning_units, [
            {PERSON: self.attribution_lu2_1.tutor.person, LEARNING_UNIT_YEARS: [self.learning_unit_year_2]},
            {PERSON: self.attribution_lu2_2.tutor.person, LEARNING_UNIT_YEARS: [self.learning_unit_year_2]}])

    def test_get_learning_unit_yr_one_person_with_several_learning_unit_for_which_he_is_responsible(self):
        learning_units = get_responsible_and_learning_unit_yr_list(
            [self.learning_unit_year_1, self.learning_unit_year_3])
        self.assertCountEqual(learning_units, [
            {PERSON: self.tutor_lu1_1.person,
             LEARNING_UNIT_YEARS: [self.learning_unit_year_1, self.learning_unit_year_3]}])

    def test_get_learning_unit_yr_list_with_summary_already_updated(self):
        learning_unit_year_updated = LearningUnitYearFakerFactory()
        learning_unit_year_updated.summary_status=True
        learning_units = get_responsible_and_learning_unit_yr_list([learning_unit_year_updated])
        self.assertCountEqual(learning_units, [])