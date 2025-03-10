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
from django.contrib.auth.models import User
from rest_framework import renderers
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from base.models.person import Person
from ..serializers.auth_token import AuthTokenSerializer


class AuthToken(APIView):
    """This view allow admin user to generate a token for a specific username """
    name = 'auth-token'
    throttle_classes = ()
    permission_classes = (IsAdminUser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = AuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        if self.request.META.get('HTTP_X_USER_GLOBALID'):
            self._handle_user_headers(user)
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})

    def _handle_user_headers(self, user: User):
        Person.objects.update_or_create(
            global_id=self.request.META['HTTP_X_USER_GLOBALID'],
            defaults={
                'user_id': user.pk,
                'first_name': self.request.META['HTTP_X_USER_FIRSTNAME'],
                'last_name': self.request.META['HTTP_X_USER_LASTNAME'],
                'email': self.request.META['HTTP_X_USER_EMAIL'],
                'language': self.request.META.get('HTTP_ACCEPT_LANGUAGE', 'en'),
            }
        )
