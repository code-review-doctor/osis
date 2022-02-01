##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2022 Université catholique de Louvain (http://www.uclouvain.be)
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
import mock
from django.contrib import messages
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from base.tests.factories.person import PersonFactory


class TestSupprimerUnitesEnseignement(TestCase):

    code = 'LCOMI200M'
    year = 2021

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('supprimer_unites_enseignement_view', kwargs={'annee': cls.year, 'code_programme': cls.code})

    def setUp(self) -> None:
        self.client.force_login(PersonFactory().user)

    def test_assert_template_used(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "preparation_inscription/supprimer_unites_enseignement.html")

    @mock.patch('infrastructure.utils.MessageBus.invoke')
    def test_post_to_delete_learning_units(self, mock_invoke):
        to_delete = ['A', 'B', 'C']
        response = self.client.post(self.url, data={'to_delete': to_delete})
        msg = next(msg for msg in get_messages(response.wsgi_request))
        self.assertEqual(msg.level, messages.SUCCESS)
        self.assertIn(', '.join(to_delete), msg.message)
