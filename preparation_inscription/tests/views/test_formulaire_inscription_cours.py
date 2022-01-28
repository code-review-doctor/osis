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
import mock
from django.http.response import HttpResponseForbidden
from django.test import TestCase
from django.urls import reverse

from base.tests.factories.person import PersonFactory
from base.tests.factories.program_manager import ProgramManagerFactory
from ddd.logic.preparation_programme_annuel_etudiant.dtos import FormulaireInscriptionCoursDTO, ContenuGroupementDTO, \
    GroupementDTO
from education_group.tests.ddd.factories.domain.group import GroupFactory
from program_management.ddd.domain.program_tree_version import STANDARD

ACRONYM = 'LCOMI200M'

YEAR = 2021


class TestFormulaireInscriptionCoursView(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('default_enrollment_form', kwargs={'year': YEAR, 'acronym': ACRONYM})

    def setUp(self) -> None:
        pgm_manager = ProgramManagerFactory()
        self.person = pgm_manager.person
        self.client.force_login(self.person.user)
        #
        fetch_tree_patcher = mock.patch(
            'preparation_inscription.views.formulaire_inscription_cours.FormulaireInscriptionCoursView.get_group_obj',
            return_value=GroupFactory()
        )
        fetch_tree_patcher.start()
        self.addCleanup(fetch_tree_patcher.stop)

        self.fetch_from_cache_patcher = mock.patch(
            'preparation_inscription.views.formulaire_inscription_cours._get_formation_inscription_cours',
            return_value=FormulaireInscriptionCoursDTO(
                annee_formation=YEAR,
                sigle_formation=ACRONYM,
                version_formation=STANDARD,
                intitule_formation='Bachelier en sciences économiques et de gestion',
                racine=ContenuGroupementDTO(
                    groupement_contenant=GroupementDTO(
                        intitule='intitule',
                        obligatoire=True,
                        chemin_acces=''
                    ),
                    unites_enseignement_contenues=[],
                    groupements_contenus=[]
                )
            )
        )
        self.fetch_from_cache_patcher.start()
        self.addCleanup(self.fetch_from_cache_patcher.stop)

    def test_user_has_not_permission(self):
        person_without_permission = PersonFactory()
        self.client.force_login(person_without_permission.user)

        response = self.client.get(self.url)

        self.assertTemplateUsed(response, "access_denied.html")
        self.assertEqual(response.status_code, HttpResponseForbidden.status_code)

    def test_assert_template_used(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "onglets.html")
