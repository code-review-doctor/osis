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
import datetime
import mock
from io import BytesIO
from unittest.mock import patch

from django.http import HttpResponseNotAllowed
from django.http.response import HttpResponseForbidden, HttpResponseRedirect, HttpResponse
from django.test import TestCase
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from openpyxl import load_workbook

from base.business.learning_units.xls_generator import generate_xls_teaching_material
from base.forms.learning_unit.search.educational_information import LearningUnitDescriptionFicheFilter
from base.models.enums import entity_type
from base.models.enums import organization_type
from base.models.enums.academic_calendar_type import AcademicCalendarTypes
from base.models.enums.learning_unit_year_subtypes import FULL
from base.tests.factories.academic_calendar import AcademicCalendarFactory
from base.tests.factories.academic_year import create_current_academic_year, AcademicYearFactory
from base.tests.factories.entity_version import EntityVersionFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.person import FacultyManagerForUEFactory, PersonWithPermissionsFactory, PersonFactory
from base.tests.factories.program_manager import ProgramManagerFactory
from base.tests.factories.teaching_material import TeachingMaterialFactory
from base.tests.factories.user import UserFactory
from base.views.learning_units.search.common import SearchTypes
from cms.enums.entity_name import LEARNING_UNIT_YEAR
from cms.tests.factories.text_label import TextLabelFactory
from cms.tests.factories.translated_text import TranslatedTextFactory
from cms.tests.factories.translated_text_label import TranslatedTextLabelFactory
from ddd.logic.preparation_programme_annuel_etudiant.dtos import FormulaireInscriptionCoursDTO
from education_group.tests.ddd.factories.domain.group import GroupFactory
from learning_unit.tests.factories.faculty_manager import FacultyManagerFactory

from education_group.ddd.domain.group import Group
from education_group.templatetags.version_details import version_details
from program_management.ddd.domain.node import NodeIdentity
from program_management.tests.ddd.factories.program_tree import ProgramTreeFactory
from program_management.tests.ddd.factories.program_tree_version import ProgramTreeVersionFactory
from infrastructure.formation_catalogue.repository.in_memory.program_tree import InMemoryProgramTreeRepository

ACRONYM = 'LCOMI200M'

YEAR = 2021


class TestFormulaireInscriptionCourssView(TestCase):
    #
    @classmethod
    def setUpTestData(cls):
        # cls.root_node_code = ACRONYM
        #
        #
        # cls.program_tree = ProgramTreeFactory(
        #     entity_id__year=YEAR,
        #     entity_id__code=cls.root_node_code,
        # )
        # cls.fake_program_tree_repository = InMemoryProgramTreeRepository()
        # cls.fake_program_tree_repository.create(cls.program_tree)
        #
        # cls.program_tree_version = ProgramTreeVersionFactory(
        #     tree=cls.program_tree,
        #     entity_id__version_name='STANDARD',
        #     program_tree_repository=cls.fake_program_tree_repository,
        #     title_fr="Title fr",
        # )


        cls.url = reverse('default_enrollment_form', kwargs={'year': YEAR, 'acronym': ACRONYM})

    def setUp(self) -> None:
        pgm_manager = ProgramManagerFactory()
        self.person = pgm_manager.person
        self.client.force_login(self.person.user)
        #
        fetch_tree_patcher = mock.patch('preparation_inscription.views.formulaire_inscription_cours.FormulaireInscriptionCoursView.get_group_obj',
                                        return_value=GroupFactory())
        fetch_tree_patcher.start()
        self.addCleanup(fetch_tree_patcher.stop)

        self.fetch_from_cache_patcher = mock.patch(
            'preparation_inscription.views.formulaire_inscription_cours._get_formation_inscription_cours',
            return_value=FormulaireInscriptionCoursDTO(
                annee_formation=YEAR,
                sigle_formation=ACRONYM,
                version_formation='',
                intitule_complet_formation='',
                racine=None
            )
        )
        self.fetch_from_cache_patcher.start()
        self.addCleanup(self.fetch_from_cache_patcher.stop)

        # self.url = reverse('default_enrollment_form', kwargs={'year': YEAR, 'acronym': ACRONYM})


    def test_user_has_not_permission(self):
        person_without_permission = PersonFactory()
        self.client.force_login(person_without_permission.user)

        response = self.client.get(self.url)

        self.assertTemplateUsed(response, "access_denied.html")
        self.assertEqual(response.status_code, HttpResponseForbidden.status_code)

    # @mock.patch('preparation_inscription.views.formulaire_inscription_cours.FormulaireInscriptionCoursView.get_group_obj')
    # @mock.patch('preparation_inscription.views.formulaire_inscription_cours._get_formation_inscription_cours')
    # def test_assert_template_used(self, mock_FormulaireInscriptionCoursDTO, mock_get_group_obj):
    def test_assert_template_used(self):
        response = self.client.get(self.url)
        # mock_get_group_obj = GroupFactory()
        # mock_FormulaireInscriptionCoursDTO = FormulaireInscriptionCoursDTO(
        #     annee_formation=YEAR,
        #     sigle_formation=ACRONYM,
        #     version_formation='',
        #     intitule_complet_formation='',
        #     racine=None
        # )
        self.assertTemplateUsed(response, "onglets.html")
    #
    # @mock.patch('preparation_inscription.views.formulaire_inscription_cours.FormulaireInscriptionCoursView.get_group_obj')
    # @mock.patch('preparation_inscription.views.formulaire_inscription_cours._get_formation_inscription_cours')
    # def test_assert_context_have_keys(self, mock_FormulaireInscriptionCoursDTO, mock_get_group_obj):
    def test_assert_context_have_keys(self):
        response = self.client.get(self.url)
        # mock_get_group_obj = GroupFactory()
        # mock_FormulaireInscriptionCoursDTO = FormulaireInscriptionCoursDTO(
        #     annee_formation=YEAR,
        #     sigle_formation=ACRONYM,
        #     version_formation='',
        #     intitule_complet_formation='',
        #     racine=None
        # )
        self.assertIn('code', response.context)
        self.assertIn('title', response.context)
        self.assertIn('formulaire_inscription_cours', response.context)
        self.assertIn('year', response.context)
