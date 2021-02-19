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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################

from django.contrib.auth.models import Permission
from django.test import TestCase, SimpleTestCase
from django.test.utils import override_settings
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from base.models.enums.education_group_types import TrainingType, MiniTrainingType, GroupType
from base.tests.factories.user import UserFactory
from base.views.common import home, _build_attention_message
from osis_common.tests.factories.application_notice import ApplicationNoticeFactory


class ErrorViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        permission = Permission.objects.get(codename='can_access_academic_calendar')
        cls.user.user_permissions.add(permission)

    @override_settings(DEBUG=False)
    def test_404_error(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('academic_calendar_read', args=[46898]), follow=True)
        self.assertEqual(response.status_code, 404)


class TestCheckNotice(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse(home)
        cls.notice = ApplicationNoticeFactory()

    def setUp(self):
        self.client.force_login(UserFactory())

    def test_context(self):
        response = self.client.get(self.url)
        self.assertEqual(response.context['subject'], self.notice.subject)
        self.assertEqual(response.context['notice'], self.notice.notice)


@override_settings(LANGUAGES=[('fr-be', 'Français'), ], LANGUAGE_CODE='fr-be')
class TestBuildAttentionMessage(SimpleTestCase):

    def test_group(self):
        self.assertEqual(_build_attention_message(GroupType.SUB_GROUP),
                         "Attention ce groupement fait partie de plusieurs formations :"
                         )

    def test_training(self):
        self.assertEqual(
            _build_attention_message(TrainingType.BACHELOR),
            "Attention cette formation fait partie de plusieurs formations :"
        )

    def test_mini_training(self):
        self.assertEqual(
            _build_attention_message(MiniTrainingType.OPEN_MINOR),
            "Attention cette mini-formation fait partie de plusieurs formations :"
        )

    def test_ue(self):
        self.assertEqual(
            _build_attention_message(None),
            "Attention cette unité d'enseignement fait partie de plusieurs formations :"
        )
        return _('Pay attention! This learning unit is used in more than one formation')
