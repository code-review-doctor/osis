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

from base.models.enums.peps_type import PepsTypes
from base.tests.factories.student import StudentFactory
from base.tests.factories.student_specific_profile import StudentSpecificProfileFactory
from ddd.logic.encodage_des_notes.soumission.dtos import SignaletiqueEtudiantDTO, EtudiantPepsDTO
from infrastructure.encodage_de_notes.soumission.domain.service.signaletique_etudiant import \
    SignaletiqueEtudiantTranslator


class InscriptionExamenTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.annee = 2020
        cls.numero_session = 2
        cls.translator = SignaletiqueEtudiantTranslator()

    def test_should_trouver_aucun_resultats(self):
        result = self.translator.search(["12316451", "12345678", "11111111"])
        expected_result = set()
        self.assertSetEqual(expected_result, result)

    def test_should_trouver_1_etudiant_avec_peps(self):
        student_peps = StudentSpecificProfileFactory(
            type=PepsTypes.ARTIST.name,
        )
        result = self.translator.search([student_peps.student.registration_id])
        self.assertEqual(len(result), 1)
        expected_result = {
            SignaletiqueEtudiantDTO(
                noma=student_peps.student.registration_id,
                nom=student_peps.student.person.last_name,
                prenom=student_peps.student.person.first_name,
                peps=EtudiantPepsDTO(
                    type_peps=student_peps.type,
                    tiers_temps=student_peps.arrangement_additional_time,
                    copie_adaptee=student_peps.arrangement_appropriate_copy,
                    local_specifique=student_peps.arrangement_specific_locale,
                    autre_amenagement=student_peps.arrangement_other,
                    details_autre_amenagement=student_peps.arrangement_comment,
                    accompagnateur=student_peps.guide,
                ),
            )
        }
        self.assertSetEqual(expected_result, result)

    def test_should_trouver_1_etudiant_sans_peps(self):
        student = StudentFactory()
        result = self.translator.search([student.registration_id])
        self.assertEqual(len(result), 1)
        expected_result = {
            SignaletiqueEtudiantDTO(
                noma=student.registration_id,
                nom=student.person.last_name,
                prenom=student.person.first_name,
                peps=EtudiantPepsDTO(
                    type_peps=None,
                    tiers_temps=None,
                    copie_adaptee=None,
                    local_specifique=None,
                    autre_amenagement=None,
                    details_autre_amenagement=None,
                    accompagnateur=None,
                ),
            )
        }
        self.assertSetEqual(expected_result, result)
