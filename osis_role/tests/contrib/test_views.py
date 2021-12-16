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
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.test.client import RequestFactory
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from base.tests.factories.user import UserFactory
from osis_role.contrib.views import APIPermissionRequiredMixin


class TestApiPermissionRequiredMixin(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Tested class
        class TestAPIView(APIPermissionRequiredMixin, APIView):
            permission_mapping = {
                'GET': 'auth.view_user',
                'POST': None,
                'PUT': ('auth.change_user', ),
            }

            def delete(self, request, *args, **kwargs):
                return Response()

            def get(self, request, *args, **kwargs):
                return Response()
            
            def post(self, request, *args, **kwargs):
                return Response()
            
            def put(self, request, *args, **kwargs):
                return Response()

        cls.api_view = TestAPIView
        cls.factory = RequestFactory()

    def test_user_with_right_permissions_string(self):
        # Create a user with the right permission (defined in the class as a string)
        user = UserFactory()
        user.user_permissions.add(Permission.objects.get(codename="view_user"))

        # Simulate a get request with the specified user
        request = self.factory.get('/osis_role/tests_views/')
        request.user = user
        request._force_auth_user = user
        response = self.api_view.as_view()(request)

        # Check result -> authorized access
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_with_right_permissions_tuple(self):
        # Create a user with the right permissions (defined in the class as a tuple)
        user = UserFactory()
        user.user_permissions.add(Permission.objects.get(codename="change_user"))

        # Simulate a get request with the specified user
        request = self.factory.put('/osis_role/tests_views/')
        request.user = user
        request._force_auth_user = user
        response = self.api_view.as_view()(request)

        # Check result -> authorized access
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_with_wrong_permissions(self):
        # Create a user without the necessary permission
        user = UserFactory()
        user.user_permissions.add(Permission.objects.get(codename="change_user"))

        # Simulate a get request with the specified user
        request = self.factory.get('/osis_role/tests_views/')
        request.user = user
        request._force_auth_user = user
        response = self.api_view.as_view()(request)

        # Check result -> non authorized access
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_not_configured_request(self):
        # Create a user with the right permission
        user = UserFactory()
        user.user_permissions.add(Permission.objects.get(codename="delete_user"))

        # Simulate a get request with the specified user
        request = self.factory.delete('/osis_role/tests_views/')
        request.user = user
        request._force_auth_user = user
        response = self.api_view.as_view()(request)

        # Check result -> authorized access as no permission is required for this request
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_no_request_permission(self):
        # Create a user with the right permission
        user = UserFactory()

        # Simulate a get request with the specified user
        request = self.factory.post('/osis_role/tests_views/')
        request.user = user
        request._force_auth_user = user
        response = self.api_view.as_view()(request)

        # Check result -> authorized access as no permission is required for this request
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_no_authenticated_user(self):
        # Simulate a get request with an anonymous user
        request = self.factory.post('/osis_role/tests_views/')
        response = self.api_view.as_view()(request)
        # Check result -> unauthorized access as the user isn't authenticated
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
