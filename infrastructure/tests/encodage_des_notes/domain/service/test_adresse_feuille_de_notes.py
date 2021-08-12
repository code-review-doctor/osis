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

from assessments.tests.factories.score_sheet_address import ScoreSheetAddressFactory
from base.models.enums.education_group_types import TrainingType
from base.tests.factories.cohort_year import CohortYearFactory
from base.tests.factories.education_group_type import EducationGroupTypeFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from infrastructure.encodage_de_notes.soumission.domain.service.adresse_feuille_de_notes import \
    AdresseFeuilleDeNotesTranslator


class AdresseFeuilleDeNotesTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.translator = AdresseFeuilleDeNotesTranslator()

    def test_should_renvoyer_aucun_resultat(self):
        result = self.translator.search({'DROI2M'})
        self.assertEqual(result, set())

    def test_should_renvoyer_1_adresse_pour_1_formation(self):
        score_sheet_address = ScoreSheetAddressFactory(
            education_group=EducationGroupYearFactory(acronym='DROI1BA').education_group
        )
        result = self.translator.search({'DROI1BA'})
        self.assertEqual(len(result), 1)
        dto = list(result)[0]
        self.assertEqual(dto.nom_cohorte, 'DROI1BA')
        self.assertEqual(dto.destinataire, score_sheet_address.recipient)
        self.assertEqual(dto.rue_et_numero, score_sheet_address.location)
        self.assertEqual(dto.code_postal, score_sheet_address.postal_code)
        self.assertEqual(dto.ville, score_sheet_address.city)
        self.assertEqual(dto.pays, score_sheet_address.country.name)
        self.assertEqual(dto.telephone, score_sheet_address.phone)
        self.assertEqual(dto.fax, score_sheet_address.fax)
        self.assertEqual(dto.email, score_sheet_address.email)

    def test_should_renvoyer_1_adresse_pour_1_cohorte(self):
        CohortYearFactory(
            education_group_year__acronym='DROI1BA',
            education_group_year__education_group_type=EducationGroupTypeFactory(name=TrainingType.BACHELOR.name),
        )
        result = self.translator.search({'DROI1BA'})
        self.assertEqual(len(result), 1)
        dto = list(result)[0]
        self.assertEqual(dto.nom_cohorte, 'DROI11BA')
