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
from django.test import SimpleTestCase
from django.utils.datetime_safe import datetime

from base.models.academic_year import AcademicYear
from base.models.education_group_year import EducationGroupYear
from education_group.models.group_year import GroupYear
from program_management.models.education_group_version import EducationGroupVersion

STANDARD = 'standard'


class TestEducationGroupVersion(SimpleTestCase):

    def setUp(cls):
        cls.academic_year = AcademicYear(year=datetime.today().year)
        cls.offer = EducationGroupYear(academic_year=cls.academic_year, partial_acronym='PA', acronym='ACRO')
        cls.root_group = GroupYear()

    def test_str_education_group_version(self):
        version = EducationGroupVersion(version_name='version', offer=self.offer, root_group=self.root_group)
        self.assertEqual(str(version), '{} ({})'.format(version.offer, version.version_name))

    def test_str_standard_education_group_version(self):
        version = EducationGroupVersion(offer=self.offer, root_group=self.root_group)
        self.assertEqual(str(version), '{} ({})'.format(version.offer, STANDARD))
