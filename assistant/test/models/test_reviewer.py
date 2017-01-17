##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2016 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.test import TestCase
from base.models.person import Person
from django.contrib.auth.models import User
from assistant.models.reviewer import Reviewer
from assistant.enums import reviewer_role


class MessageModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='reviewer', email='reviewer@uclouvain.be', password='secret'
        )
        self.person = Person.objects.create(user=self.user, first_name='Laurent', last_name='last_name')
        self.reviewer = Reviewer.objects.create(person=self.person, role=reviewer_role.RESEARCH_ASSISTANT)
        self.reviewer.save()

    def test_reviewer_basic(self):
        self.assertEqual(self.reviewer.role, reviewer_role.RESEARCH_ASSISTANT)
        self.assertEqual(self.reviewer.person.first_name, 'Laurent')
