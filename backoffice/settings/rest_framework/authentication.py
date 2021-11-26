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
from typing import List

from django.conf import settings
from django.contrib.auth import backends
from django.utils.translation import gettext_lazy
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication, get_authorization_header

from base.models.person import Person


class ESBAuthentication(BaseAuthentication):
    """
    ESB authentication

    ESB should authenticate by passing a secret key in the "Authorization"
    HTTP header, prepended with the string "ESB ".  For example:

        Authorization: ESB 401f7ac837da42b97f613d789819ff93537bee6a
    """

    keyword = 'ESB'

    def get_secret_key(self):
        return settings.REST_FRAMEWORK_ESB_AUTHENTICATION_SECRET_KEY

    def get_mandatory_headers(self) -> List[str]:
        return [
            'HTTP_X_USER_GLOBALID',
            'HTTP_X_USER_FIRSTNAME',
            'HTTP_X_USER_LASTNAME',
            'HTTP_X_USER_EMAIL',
        ]

    def authenticate(self, request):
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != self.keyword.lower().encode() or not self.get_secret_key():
            return None

        if len(auth) == 1:
            msg = gettext_lazy('Invalid ESB header. No credentials provided.')
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = gettext_lazy('Invalid ESB header. Secret key string should not contain spaces.')
            raise exceptions.AuthenticationFailed(msg)

        try:
            token = auth[1].decode()
        except UnicodeError:
            msg = gettext_lazy('Invalid ESB header. Secret key string should not contain invalid characters.')
            raise exceptions.AuthenticationFailed(msg)

        if any([not request.META.get(mandatory_header) for mandatory_header in self.get_mandatory_headers()]):
            msg = gettext_lazy('Missing mandatory headers. %(mandatory_headers)s should be present and filled') % {
                'mandatory_headers': ", ".join(self.get_mandatory_headers())
            }
            raise exceptions.AuthenticationFailed(msg)

        return self.authenticate_credentials(token, request)

    def authenticate_credentials(self, key, request):
        if key != self.get_secret_key():
            msg = gettext_lazy('Invalid token.')
            raise exceptions.AuthenticationFailed(msg)

        person, created = Person.objects.update_or_create(
            global_id=request.META['HTTP_X_USER_GLOBALID'],
            defaults={
                'first_name': request.META['HTTP_X_USER_FIRSTNAME'],
                'last_name': request.META['HTTP_X_USER_LASTNAME'],
                'email': request.META['HTTP_X_USER_EMAIL'],
                'language': request.META.get('HTTP_ACCEPT_LANGUAGE', 'en'),
            }
        )
        if not person.user_id:
            UserModel = backends.get_user_model()
            user, _ = UserModel.objects.get_or_create(**{
                UserModel.USERNAME_FIELD: request.META['HTTP_X_USER_EMAIL'],
            }, defaults={
                'first_name': request.META['HTTP_X_USER_FIRSTNAME'],
                'last_name': request.META['HTTP_X_USER_LASTNAME'],
                UserModel.EMAIL_FIELD: request.META['HTTP_X_USER_EMAIL'],
            })
            person.user = user
            person.save()

        return (person.user, self.get_secret_key(),)

    def authenticate_header(self, request):
        return self.keyword
