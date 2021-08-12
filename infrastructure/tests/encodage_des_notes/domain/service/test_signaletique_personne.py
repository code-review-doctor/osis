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

from base.models.enums.person_address_type import PersonAddressType
from base.tests.factories.person import PersonFactory
from base.tests.factories.person_address import PersonAddressFactory
from infrastructure.encodage_de_notes.soumission.domain.service.signaletique_personne import \
    SignaletiquePersonneTranslator


class DeliberationTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.matricule_fgs = '12345678'
        cls.translator = SignaletiquePersonneTranslator()

    def test_should_renvoyer_aucun_resultat(self):
        result = self.translator.search({self.matricule_fgs})
        self.assertEqual(result, set())

    def test_should_renvoyer_email_sans_adresse(self):
        person = PersonFactory(global_id=self.matricule_fgs)
        result = self.translator.search({self.matricule_fgs})
        dto = list(result)[0]
        self.assertEqual(dto.email, person.email)
        self.assertIsNone(dto.adresse_professionnelle)

    def test_should_ignorer_adresse_residentielle(self):
        address = PersonAddressFactory(
            person__global_id=self.matricule_fgs,
            label=PersonAddressType.RESIDENTIAL.name,
        )
        result = self.translator.search({self.matricule_fgs})
        dto = list(result)[0]
        self.assertEqual(dto.email, address.person.email)
        self.assertIsNone(dto.adresse_professionnelle)

    def test_should_renvoyer_adresse_professionnelle(self):
        address = PersonAddressFactory(
            person__global_id=self.matricule_fgs,
            label=PersonAddressType.PROFESSIONAL.name,
        )
        result = self.translator.search({self.matricule_fgs})
        dto = list(result)[0]
        self.assertEqual(dto.adresse_professionnelle.code_postal, address.postal_code)
        self.assertEqual(dto.adresse_professionnelle.ville, address.city)
        self.assertEqual(dto.adresse_professionnelle.rue_numero_boite, address.location)
