##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.test import TestCase

from attribution.tests.models import test_attribution
from base.auth.roles import tutor
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.tutor import TutorFactory
from base.tests.factories.user import UserFactory


class TestTutor(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.person = PersonFactory(first_name="James", last_name="Dupont", user=cls.user)
        cls.tutor = TutorFactory(person=cls.person)
        TutorFactory()  # Create fake Tutor
        TutorFactory()  # Create fake Tutor
        cls.learning_unit_year = LearningUnitYearFactory()
        cls.attribution = test_attribution.create_attribution(tutor=cls.tutor,
                                                               learning_unit_year=cls.learning_unit_year,
                                                               score_responsible=False)

    def test_find_by_person(self):
        self.assertEqual(self.tutor, tutor.find_by_person(self.person))

    def test_find_by_person_empty(self):
        person_unknown = PersonFactory()
        self.assertIsNone(tutor.find_by_person(person_unknown))

    def test_find_by_person_wrong_id(self):
        self.assertIsNone(tutor.find_by_person(-1))

    def test_is_tutor(self):
        self.assertTrue(tutor.is_tutor(self.user))

    def test_is_not_tutor(self):
        user_unknown = UserFactory()
        self.assertFalse(tutor.is_tutor(user_unknown))

    def test_find_by_user(self):
        self.assertEqual(self.tutor, tutor.find_by_user(self.user))

    def test_find_by_id(self):
        self.assertEqual(self.tutor, tutor.find_by_id(self.tutor.id))

    def test_find_by_id_wrong_id(self):
        self.assertIsNone(tutor.find_by_id(-1))


class MockRequest:
    COOKIES = {}


class MockSuperUser:
    def has_perm(self, perm):
        return True


request = MockRequest()
request.user = MockSuperUser()


class TestSearch(TestCase):
    @classmethod
    def setUpTestData(cls):
        tutor_names = (
            {"first_name": "Jean", "last_name": "Pierrer"},
            {"first_name": "John", "last_name": "Doe"},
            {"first_name": "Morgan", "last_name": "Wakaba"},
            {"first_name": "Philip", "last_name": "Doe"}
        )

        cls.tutors = [TutorFactory(person=PersonFactory(**name)) for name in tutor_names]

    def test_with_no_criterias(self):
        qs = tutor.search()
        self.assertQuerysetEqual(qs, self.tutors, transform=lambda o: o, ordered=False)

    def test_with_name_criteria(self):
        for tutor_obj in self.tutors:
            with self.subTest(tutor=tutor):
                name =  " ".join([tutor_obj.person.first_name, tutor_obj.person.last_name])
                qs = tutor.search(name=name)
                self.assertQuerysetEqual(qs, [tutor_obj], transform=lambda o: o, ordered=False)
