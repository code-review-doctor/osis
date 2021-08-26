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
from django.contrib.auth.models import Permission, Group
from django.http import HttpResponse
from django.test import TestCase, override_settings
from django.utils.translation import gettext_lazy as _
from rest_framework.reverse import reverse

from base.models.enums.groups import CENTRAL_MANAGER_GROUP, TUTOR
from base.tests.factories.entity_manager import EntityManagerFactory
from base.tests.factories.entity_version import EntityVersionFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.student import StudentFactory
from base.views.user_list import UserListView
from base.views.user_list import _prepare_xls_content, _get_headers
from learning_unit.tests.factories.faculty_manager import FacultyManagerFactory

COL_FOR_LAST_NAME = 0
COL_FOR_FIRST_NAME = 1
COL_FOR_GLOBAL_ID = 2
COL_FOR_EMAIL = 3
COL_FOR_GROUP_NAME = 4
COL_FOR_ENTITIES = 5
COL_FOR_FACULTY_MGR_UE_MANAGED_ENTITIES = 7


class UserListViewTestCase(TestCase):

    def setUp(self):
        self.user = PersonFactory().user
        self.permission = Permission.objects.get(codename='can_read_persons_roles')
        self.client.force_login(self.user)

    def test_user_list_forbidden(self):
        url = reverse('academic_actors_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_user_list_with_permission(self):
        url = reverse('academic_actors_list')
        self.user.user_permissions.add(self.permission)
        response = self.client.get(url)
        self.assertEqual(response.status_code, HttpResponse.status_code)

    def test_donot_return_teacher_only_in_tutor_group(self):
        a_tutor_person = PersonFactory()
        a_tutor_person.user.groups.add(Group.objects.get_or_create(name=TUTOR)[0])
        a_tutor_person.save()
        self.assertCountEqual(UserListView().get_queryset(), [])

    def test_tutor_in_several_groups(self):
        a_tutor_person = PersonFactory()
        a_tutor_person.user.groups.add(Group.objects.get_or_create(name=TUTOR)[0])
        a_tutor_person.user.groups.add(Group.objects.get_or_create(name=CENTRAL_MANAGER_GROUP)[0])
        a_tutor_person.save()

        self.assertCountEqual(UserListView().get_queryset(), [a_tutor_person])

    def test_donot_return_student_in_no_groups(self):
        StudentFactory()
        a_central_manager_person = PersonFactory()
        a_central_manager_person.user.groups.add(Group.objects.get_or_create(name=CENTRAL_MANAGER_GROUP)[0])
        a_central_manager_person.save()

        self.assertCountEqual(UserListView().get_queryset(), [a_central_manager_person])


@override_settings(INSTALLED_APPS=['learning_unit', 'education_group', 'partnership'])
class XlsUserListTestCase(TestCase):
    def setUp(self):
        self.view = UserListView()

        self.entity_drt = EntityVersionFactory(acronym="DRT").entity
        self.entity_espo = EntityVersionFactory(acronym="ESPO").entity

    def test_prepare_xls_content_no_data(self):
        self.assertEqual(_prepare_xls_content(self.view, []), [])

    def test_prepare_xls_content_check_data(self):
        person_faculty_manager = PersonFactory(global_id='12345678')
        FacultyManagerFactory(person=person_faculty_manager, entity=self.entity_drt)
        EntityManagerFactory(person=person_faculty_manager, entity=self.entity_espo)
        FacultyManagerFactory(person=person_faculty_manager, entity=self.entity_espo)

        data = _prepare_xls_content(self.view, [person_faculty_manager])
        self.assertEqual(len(data), 2)
        data_user_faculty_mgr = data[0]
        self.assertEqual(data_user_faculty_mgr[COL_FOR_LAST_NAME], person_faculty_manager.last_name)
        self.assertEqual(data_user_faculty_mgr[COL_FOR_FIRST_NAME], person_faculty_manager.first_name)
        self.assertEqual(data_user_faculty_mgr[COL_FOR_GLOBAL_ID], person_faculty_manager.global_id)
        self.assertEqual(data_user_faculty_mgr[COL_FOR_EMAIL], person_faculty_manager.email)
        self.assertEqual(data_user_faculty_mgr[COL_FOR_GROUP_NAME], "faculty_managers_for_ue")
        self.assertEqual(data_user_faculty_mgr[COL_FOR_ENTITIES], "ESPO\nDRT")
        data_user_entity_mgr = data[1]
        self.assertEqual(data_user_entity_mgr[COL_FOR_LAST_NAME], person_faculty_manager.last_name)
        self.assertEqual(data_user_entity_mgr[COL_FOR_FIRST_NAME], person_faculty_manager.first_name)
        self.assertEqual(data_user_entity_mgr[COL_FOR_GLOBAL_ID], person_faculty_manager.global_id)
        self.assertEqual(data_user_entity_mgr[COL_FOR_EMAIL], person_faculty_manager.email)
        self.assertEqual(data_user_entity_mgr[COL_FOR_GROUP_NAME], "entity_managers")
        self.assertEqual(data_user_entity_mgr[COL_FOR_ENTITIES], "ESPO")

    def test_headers(self):
        titles = _get_headers()
        expected_titles = [
            _('Lastname'),
            _('Firstname'),
            _('Global ID'),
            _('Email'),
            _('Groups'),
            _('Entities'),
            _('Trainings')
        ]
        self.assertListEqual(
            titles,
            expected_titles
        )
