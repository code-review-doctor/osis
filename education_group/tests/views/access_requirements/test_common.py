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
from django.test import TestCase

from base.tests.factories.education_group_year import EducationGroupYearCommonBachelorFactory, \
    EducationGroupYearBachelorFactory
from education_group.views.access_requirements.common import AccessRequirementsMixin


class TestPermissionRequiredMockClass(AccessRequirementsMixin):

    def __init__(self, education_group_year_obj):
        self.egy = education_group_year_obj

    def get_permission_object(self):
        return self.egy


class TestPermissionRequired(TestCase):
    def test_should_return_commonaccessrequirements_permission_when_education_group_year_is_common(self):
        mock_instance = TestPermissionRequiredMockClass(EducationGroupYearCommonBachelorFactory())

        self.assertEqual(
            ('base.change_commonaccessrequirements',),
            mock_instance.get_permission_required()
        )

    def test_should_return_admissioncondition_permission_when_education_group_year_is_not_common(self):
        mock_instance = TestPermissionRequiredMockClass(EducationGroupYearBachelorFactory())

        self.assertEqual(
            ('base.change_accessrequirements',),
            mock_instance.get_permission_required()
        )
