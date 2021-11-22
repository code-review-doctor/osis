# ############################################################################
#  OSIS stands for Open Student Information System. It's an application
#  designed to manage the core business of higher education institutions,
#  such as universities, faculties, institutes and professional schools.
#  The core business involves the administration of students, teachers,
#  courses, programs and so on.
#
#  Copyright (C) 2015-2021 Université catholique de Louvain (http://www.uclouvain.be)
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  A copy of this license - GNU General Public License - is available
#  at the root of the source code of this program.  If not,
#  see http://www.gnu.org/licenses/.
# ############################################################################
from django.conf import settings
from django.test import TestCase, RequestFactory, override_settings
from django.utils.translation import gettext_lazy
from rest_framework import exceptions

from backoffice.settings.rest_framework.authentication import ESBAuthentication
from base.models.person import Person


@override_settings(REST_FRAMEWORK_ESB_AUTHENTICATION_SECRET_KEY="401f7ac837da42b97f613d789819ff93537bee6a")
class TestESBAuthentication(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.authentication = ESBAuthentication()
        cls.request_factory = RequestFactory()

        cls.extra_http_headers = {
            'HTTP_AUTHORIZATION': 'ESB 401f7ac837da42b97f613d789819ff93537bee6a',
            'HTTP_ACCEPT_LANGUAGE': 'en',
            'HTTP_X_USER_FIRSTNAME': 'Durant',
            'HTTP_X_USER_LASTNAME': 'Thomas',
            'HTTP_X_USER_EMAIL': 'thomas@dummy.com',
            'HTTP_X_USER_GLOBALID': '0123456789',
        }

    def test_assert_get_secret_key(self):
        self.assertEqual(
            self.authentication.get_secret_key(), settings.REST_FRAMEWORK_ESB_AUTHENTICATION_SECRET_KEY
        )

    def test_assert_mandatory_headers(self):
        mandatory_headers = [
            'HTTP_X_USER_GLOBALID', 'HTTP_X_USER_FIRSTNAME', 'HTTP_X_USER_LASTNAME', 'HTTP_X_USER_EMAIL'
        ]
        self.assertEqual(
            self.authentication.get_mandatory_headers(), mandatory_headers
        )

    def test_assert_raise_exception_if_esb_header_empty_str(self):
        http_headers = {
            **self.extra_http_headers,
            'HTTP_AUTHORIZATION': 'ESB '
        }
        request = self.request_factory.get('/dummy_url', **http_headers)

        with self.assertRaises(exceptions.AuthenticationFailed) as context:
            self.authentication.authenticate(request)

        error_msg = gettext_lazy('Invalid ESB header. No credentials provided.')
        self.assertEqual(context.exception.detail, error_msg)

    def test_assert_raise_exception_if_esb_header_contains_multiple_space(self):
        http_headers = {
            **self.extra_http_headers,
            'HTTP_AUTHORIZATION': 'ESB 401f7ac837da42b97f613d789819ff93537bee6a 565655'
        }
        request = self.request_factory.get('/dummy_url', **http_headers)

        with self.assertRaises(exceptions.AuthenticationFailed) as context:
            self.authentication.authenticate(request)

        error_msg = gettext_lazy('Invalid ESB header. Secret key string should not contain spaces.')
        self.assertEqual(context.exception.detail, error_msg)

    def test_assert_raise_exception_if_missing_one_mandatory_headers(self):
        for mandatory_header in self.authentication.get_mandatory_headers():
            with self.subTest(mandatory_header=mandatory_header):
                http_headers = {
                    **self.extra_http_headers,
                    mandatory_header: ''
                }
                request = self.request_factory.get('/dummy_url', **http_headers)
                with self.assertRaises(exceptions.AuthenticationFailed) as context:
                    self.authentication.authenticate(request)

                error_msg = gettext_lazy('Missing mandatory headers. '
                                         '%(mandatory_headers)s should be present and filled') % {
                    'mandatory_headers': ", ".join(self.authentication.get_mandatory_headers())
                }
                self.assertEqual(context.exception.detail, error_msg)

    def test_assert_raise_exception_if_secret_key_provided_is_not_the_same_as_settings(self):
        http_headers = {
            **self.extra_http_headers,
            'HTTP_AUTHORIZATION': 'ESB 6565656565656565'
        }
        request = self.request_factory.get('/dummy_url', **http_headers)

        with self.assertRaises(exceptions.AuthenticationFailed) as context:
            self.authentication.authenticate(request)
        self.assertEqual(context.exception.detail, gettext_lazy('Invalid token.'))

    def test_assert_create_person_and_user_if_not_exist(self):
        request = self.request_factory.get('/dummy_url', **self.extra_http_headers)
        user_created, secret_key = self.authentication.authenticate(request)

        self.assertEqual(user_created.username, self.extra_http_headers['HTTP_X_USER_EMAIL'])

        person_created = user_created.person
        self.assertEqual(person_created.first_name, self.extra_http_headers['HTTP_X_USER_FIRSTNAME'])
        self.assertEqual(person_created.last_name, self.extra_http_headers['HTTP_X_USER_LASTNAME'])
        self.assertEqual(person_created.email, self.extra_http_headers['HTTP_X_USER_EMAIL'])
        self.assertEqual(person_created.language, self.extra_http_headers['HTTP_ACCEPT_LANGUAGE'])

    def test_assert_update_person_if_person_exist_but_user_not_exist(self):
        existing_person = Person.objects.create(
            global_id=self.extra_http_headers['HTTP_X_USER_GLOBALID'],
            first_name="Paul",
            last_name="Dutronc",
            email="paul.dutronc@dummy.com"
        )

        request = self.request_factory.get('/dummy_url', **self.extra_http_headers)
        user_created, secret_key = self.authentication.authenticate(request)

        self.assertEqual(user_created.person.pk, existing_person.pk)
        self.assertEqual(user_created.username, self.extra_http_headers['HTTP_X_USER_EMAIL'])
