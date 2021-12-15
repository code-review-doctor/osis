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

from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.program_manager import ProgramManagerFactory
from ddd.logic.encodage_des_notes.encodage.dtos import CohorteGestionnaireDTO
from education_group.models.enums.cohort_name import CohortName
from infrastructure.encodage_de_notes.encodage.domain.service.cohortes_du_gestionnaire import \
    CohortesDuGestionnaireTranslator


class CohorteDuGestionnaireTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.matricule_gestionnaire = '00321234'
        cls.translator = CohortesDuGestionnaireTranslator()
        egy_droi1ba = EducationGroupYearFactory(acronym='DROI1BA')
        cls.education_group_droi1ba = egy_droi1ba.education_group
        cls.academic_year = egy_droi1ba.academic_year
        cls.education_group_droi2m = EducationGroupYearFactory(
            acronym='DROI2M',
            academic_year=cls.academic_year
        ).education_group

    def test_should_renvoyer_aucun_resultat(self):
        result = self.translator.search(
            matricule_gestionnaire=self.matricule_gestionnaire,
            annee_concernee=self.academic_year.year
        )
        self.assertSetEqual(result, set())

    def test_should_renvoyer_2_noms_cohortes_pour_1_gestionnaire(self):
        pm = ProgramManagerFactory(
            person__global_id=self.matricule_gestionnaire,
            education_group=self.education_group_droi1ba,
        )
        ProgramManagerFactory(person=pm.person, education_group=self.education_group_droi2m)
        result = self.translator.search(
            matricule_gestionnaire=self.matricule_gestionnaire,
            annee_concernee=self.academic_year.year
        )
        expected_result = {
            CohorteGestionnaireDTO(nom_cohorte='DROI1BA', matricule_gestionnaire=self.matricule_gestionnaire),
            CohorteGestionnaireDTO(nom_cohorte='DROI2M', matricule_gestionnaire=self.matricule_gestionnaire),
        }
        self.assertSetEqual(expected_result, result)

    def test_should_renvoyer_cohorte_11BA(self):
        ProgramManagerFactory(
            person__global_id=self.matricule_gestionnaire,
            education_group=self.education_group_droi1ba,
            cohort=CohortName.FIRST_YEAR.name,
        )
        result = self.translator.search(
            matricule_gestionnaire=self.matricule_gestionnaire,
            annee_concernee=self.academic_year.year
        )
        expected_result = {
            CohorteGestionnaireDTO(nom_cohorte='DROI11BA', matricule_gestionnaire=self.matricule_gestionnaire),
        }
        self.assertSetEqual(expected_result, result)

    def test_should_renvoyer_cohorte_11BA_et_1BA(self):
        pm = ProgramManagerFactory(
            person__global_id=self.matricule_gestionnaire,
            education_group=self.education_group_droi1ba,
        )
        ProgramManagerFactory(
            person=pm.person,
            education_group=pm.education_group,
            cohort=CohortName.FIRST_YEAR.name,
        )
        result = self.translator.search(
            matricule_gestionnaire=self.matricule_gestionnaire,
            annee_concernee=self.academic_year.year,
        )
        expected_result = {
            CohorteGestionnaireDTO(nom_cohorte='DROI11BA', matricule_gestionnaire=self.matricule_gestionnaire),
            CohorteGestionnaireDTO(nom_cohorte='DROI1BA', matricule_gestionnaire=self.matricule_gestionnaire),
        }
        self.assertSetEqual(expected_result, result)
