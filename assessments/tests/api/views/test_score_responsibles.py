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

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from assessments.tests.factories.score_responsible import ScoreResponsibleFactory
from base.models.learning_unit_year import LearningUnitYear
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.learning_unit import LearningUnitFactory
from assessments.api.views.score_responsibles import ScoreResponsibleList

ACRONYM_LECON2019 = 'LECON2019'
ACRONYM_LECON2021 = 'LECON2021'


class ScoreResponsiblesAPIViewTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.current_academic_year = AcademicYearFactory(current=True)
        cls.next_academic_year = AcademicYearFactory(year=cls.current_academic_year.year+1)
        cls.learning_unit = LearningUnitFactory()
        cls.learning_unit_year = LearningUnitYear(
            academic_year=cls.current_academic_year,
            learning_unit=cls.learning_unit,
            acronym=ACRONYM_LECON2021
        )
        cls.learning_unit_year.save()
        cls.learning_unit_year_next = LearningUnitYear(
            academic_year=cls.next_academic_year,
            learning_unit=cls.learning_unit,
            acronym=ACRONYM_LECON2021
        )
        cls.learning_unit_year_next.save()

        cls.score_responsible = ScoreResponsibleFactory(learning_unit_year=cls.learning_unit_year, tutor__person__last_name='Abba')
        cls.score_responsible_next = ScoreResponsibleFactory(learning_unit_year=cls.learning_unit_year_next)

        cls.learning_unit2 = LearningUnitFactory()
        cls.learning_unit_year2 = LearningUnitYear(
            academic_year=cls.current_academic_year,
            learning_unit=cls.learning_unit2,
            acronym=ACRONYM_LECON2019
        )
        cls.learning_unit_year2.save()
        cls.score_responsible2 = ScoreResponsibleFactory(learning_unit_year=cls.learning_unit_year2, tutor__person__last_name='Martin')

        cls.tutor = cls.score_responsible.tutor
        cls.url = reverse('assessments_api_v1:' + ScoreResponsibleList.name)

    def setUp(self):
        self.client.force_authenticate(user=self.tutor.person.user)

    def test_get_not_authorized(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_response(self):
        response = self.client.get(self.url,
                                   data={
                                       'year': str(self.current_academic_year.year),
                                       'learning_unit_codes':
                                           [
                                               self.learning_unit_year.acronym,
                                               self.learning_unit_year2.acronym
                                           ]
                                   }
                                   )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('application/json', response['content-type'])

        results = response.json()
        self._assert_record_equal(results[0], self.score_responsible.tutor.person, self.learning_unit_year.acronym)
        self._assert_record_equal(results[1], self.score_responsible2.tutor.person, self.learning_unit_year2.acronym)

    def _assert_record_equal(self, record, person_score_responsible, acronym):
        self.assertEqual(record.get('learning_unit_acronym'), acronym)
        self.assertEqual(record.get('year'), self.current_academic_year.year)
        self.assertEqual(record.get('global_id'), person_score_responsible.global_id)
        self.assertEqual(record.get('full_name'), "{} {}".format(person_score_responsible.last_name,
                                                                 person_score_responsible.first_name))
