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
from django.test import TestCase

from base.models.enums import entity_type
from base.models.enums import organization_type
from base.tests.factories.academic_year import create_current_academic_year, AcademicYearFactory
from base.tests.factories.business.learning_units import GenerateAcademicYear
from base.tests.factories.education_group_language import EducationGroupLanguageFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.education_group_year_domain import EducationGroupYearDomainFactory
from base.tests.factories.entity import EntityFactory
from base.tests.factories.entity_version import EntityVersionFactory
from program_management.business import xls_customized
from django.test.utils import override_settings


class XlsCustomizedTestCase(TestCase):
    #
    # @classmethod
    # def setUpTestData(cls):
        # # Create several academic year
        # cls.current_academic_year = create_current_academic_year()
        # start_year = AcademicYearFactory(year=cls.current_academic_year.year + 1)
        # end_year = AcademicYearFactory(year=cls.current_academic_year.year + 10)
        # cls.generated_ac_years = GenerateAcademicYear(start_year, end_year)
    @override_settings(LANGUAGES=[('fr-be', 'Français'), ], LANGUAGE_CODE='fr-be')
    def test_headers_without_selected_parameters(self):
        expected = ['Anac.', 'Sigle/Int. abr.', 'Intitulé', 'Catégorie', 'Type', 'Crédits']
        self.assertListEqual(xls_customized._build_headers([]), expected)

    @override_settings(LANGUAGES=[('fr-be', 'Français'), ], LANGUAGE_CODE='fr-be')
    def test_headers_with_all_parameters_selected(self):
        expected = ['Anac.', 'Sigle/Int. abr.', 'Intitulé', 'Catégorie', 'Type', 'Crédits']
        self.assertListEqual(xls_customized._build_headers([]), expected)
