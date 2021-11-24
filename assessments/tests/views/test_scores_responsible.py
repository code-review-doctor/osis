##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2012 Université catholique de Louvain (http://www.uclouvain.be)
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

import mock
from django.contrib.auth.models import Permission
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden
from django.test import TestCase
from django.test.utils import override_settings
from django.urls import reverse

from assessments.calendar.scores_exam_submission_calendar import ScoresExamSubmissionCalendar
from assessments.tests.factories.score_responsible import ScoreResponsibleFactory
from attribution.tests.factories.attribution_charge_new import AttributionChargeNewFactory
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.business.entities import create_entities_hierarchy
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.entity_manager import EntityManagerFactory
from base.tests.factories.group import EntityManagerGroupFactory
from base.tests.factories.learning_unit_enrollment import LearningUnitEnrollmentFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.offer_enrollment import OfferEnrollmentFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.program_manager import ProgramManagerFactory
from base.tests.factories.session_exam_calendar import SessionExamCalendarFactory
from base.tests.factories.tutor import TutorFactory
from base.tests.factories.user import UserFactory


class ScoresResponsibleSearchTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        group = EntityManagerGroupFactory()
        group.permissions.add(Permission.objects.get(codename='view_scoresresponsible'))
        group.permissions.add(Permission.objects.get(codename='change_scoresresponsible'))

        cls.tutor = TutorFactory()
        cls.user = cls.tutor.person.user
        cls.academic_year = AcademicYearFactory(current=True)
        SessionExamCalendarFactory.create_academic_event(cls.academic_year)

        # New structure model
        entities_hierarchy = create_entities_hierarchy()
        cls.root_entity = entities_hierarchy.get('root_entity')
        cls.child_one_entity = entities_hierarchy.get('child_one_entity')
        cls.child_two_entity = entities_hierarchy.get('child_two_entity')
        cls.learning_unit_yr_req_entity_acronym = entities_hierarchy.get('child_one_entity_version').acronym
        cls.root_entity_acronym = entities_hierarchy.get('root_entity_version').acronym

        cls.entity_manager = EntityManagerFactory(
            person=cls.tutor.person,
            entity=cls.root_entity,
            with_child=True
        )

        cls.learning_unit_year = LearningUnitYearFactory(
            academic_year=cls.academic_year,
            acronym="LBIR1210",
            learning_unit__start_year=cls.academic_year,
            learning_container_year__academic_year=cls.academic_year,
            learning_container_year__acronym="LBIR1210",
            learning_container_year__requirement_entity=cls.child_one_entity,
        )

        cls.learning_unit_year_children = LearningUnitYearFactory(
            academic_year=cls.academic_year,
            acronym="LBIR1211",
            learning_unit__start_year=cls.academic_year,
            learning_container_year__academic_year=cls.academic_year,
            learning_container_year__acronym="LBIR1211",
            learning_container_year__requirement_entity=cls.child_two_entity,
        )

        cls.attribution = AttributionChargeNewFactory(
            attribution__tutor=cls.tutor,
            attribution__learning_container_year=cls.learning_unit_year.learning_container_year,
            learning_component_year__learning_unit_year=cls.learning_unit_year,
        )
        cls.score_responsible = ScoreResponsibleFactory(
            learning_unit_year=cls.learning_unit_year,
            tutor=cls.tutor
        )
        cls.attribution_children = AttributionChargeNewFactory(
            attribution__tutor=cls.tutor,
            attribution__learning_container_year=cls.learning_unit_year_children.learning_container_year,
            learning_component_year__learning_unit_year=cls.learning_unit_year_children,
        )
        cls.score_responsible = ScoreResponsibleFactory(
            learning_unit_year=cls.learning_unit_year_children,
            tutor=cls.tutor
        )
        cls.url = reverse('scores_responsibles_search')
        cls.user.groups.add(group)

    def setUp(self):
        self.client.force_login(self.user)

    def test_assert_template_used(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertTemplateUsed(response, 'assessments/score_responsible/score_responsibles.html')

    def test_case_when_user_not_logged(self):
        self.client.logout()
        response = self.client.get(self.url)

        self.assertRedirects(response, "/login/?next={}".format(self.url))

    def test_case_search_without_filter_ensure_ordering(self):
        data = {
            'acronym': '',
            'learning_unit_title': '',
            'tutor': '',
            'scores_responsible': ''
        }
        response = self.client.get(self.url, data=data)

        self.assertEqual(response.status_code, HttpResponse.status_code)
        qs_result = response.context['object_list']

        self.assertEqual(qs_result.count(), 2)
        self.assertEqual(qs_result[0], self.learning_unit_year)
        self.assertEqual(qs_result[1], self.learning_unit_year_children)

    def test_case_search_by_acronym_and_score_responsible(self):
        data = {
            'acronym': self.learning_unit_year.acronym,
            'learning_unit_title': '',
            'tutor': '',
            'scores_responsible': self.tutor.person.last_name
        }
        response = self.client.get(self.url, data=data)

        self.assertEqual(response.status_code, HttpResponse.status_code)
        qs_result = response.context['object_list']

        self.assertEqual(qs_result.count(), 1)
        self.assertEqual(qs_result.first(), self.learning_unit_year)

    def test_case_search_by_requirement_entity(self):
        data = self._data_search_by_req_entity()

        response = self.client.get(self.url, data=data)

        self.assertEqual(response.status_code, HttpResponse.status_code)
        qs_result = response.context['object_list']

        self.assertEqual(qs_result.count(), 1)
        self.assertEqual(qs_result.first(), self.learning_unit_year)

    def test_case_search_by_requirement_entity_with_entity_subordinated(self):
        data = self._data_search_by_req_entity()
        data.update({'with_entity_subordinated': True})

        self._assert_equal_with_entity_subordinated(data, self.root_entity_acronym, [self.learning_unit_year,
                                                                                     self.learning_unit_year_children])
        self._assert_equal_with_entity_subordinated(data, self.learning_unit_yr_req_entity_acronym,
                                                    [self.learning_unit_year])

    def _assert_equal_with_entity_subordinated(self, data, entity, results):
        data.update({'requirement_entity': entity})

        response = self.client.get(self.url, data=data)
        self.assertEqual(response.status_code, HttpResponse.status_code)
        qs_result = response.context['object_list']
        self.assertCountEqual(qs_result, results)

    def _data_search_by_req_entity(self):
        data = {
            'acronym': '',
            'learning_unit_title': '',
            'tutor': '',
            'scores_responsible': '',
            'requirement_entity': self.learning_unit_yr_req_entity_acronym
        }
        return data
