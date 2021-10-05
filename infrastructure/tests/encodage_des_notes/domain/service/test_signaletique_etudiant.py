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

from base.models.enums.peps_type import PepsTypes, SportSubtypes, HtmSubtypes
from base.tests.factories.person import PersonFactory
from base.tests.factories.student import StudentFactory
from base.tests.factories.student_specific_profile import StudentSpecificProfileFactory
from ddd.logic.encodage_des_notes.soumission.dtos import SignaletiqueEtudiantDTO
from ddd.logic.encodage_des_notes.shared_kernel.dtos import EtudiantPepsDTO
from infrastructure.encodage_de_notes.shared_kernel.service.signaletique_etudiant import \
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
            guide=None
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
                    sous_type_peps='',
                    tiers_temps=student_peps.arrangement_additional_time,
                    copie_adaptee=student_peps.arrangement_appropriate_copy,
                    local_specifique=student_peps.arrangement_specific_locale,
                    autre_amenagement=student_peps.arrangement_other,
                    details_autre_amenagement=student_peps.arrangement_comment,
                    accompagnateur='',
                ),
            )
        }
        self.assertSetEqual(expected_result, result)

    def test_should_trouver_accompagnateur_pour_etudiant_avec_peps(self):
        student_peps_with_guide = StudentSpecificProfileFactory(
            type=PepsTypes.ARTIST.name,
            guide=PersonFactory()
        )

        result = self.translator.search([student_peps_with_guide.student.registration_id])
        self.assertEqual(len(result), 1)
        expected_result_accompagnateur = "{}, {}".format(
            student_peps_with_guide.guide.last_name.upper(),
            student_peps_with_guide.guide.first_name,
        )

        self.assertEqual(result.pop().peps.accompagnateur, expected_result_accompagnateur)

    def test_should_calculer_sous_type_peps_en_fonction_sport_type_peps(self):
        student_peps_sport_type = StudentSpecificProfileFactory(
            type=PepsTypes.SPORT.name,
            subtype_sport=SportSubtypes.PROMISING_ATHLETE.name
        )

        result = self.translator.search([student_peps_sport_type.student.registration_id])
        self.assertEqual(len(result), 1)
        expected_result = {
            SignaletiqueEtudiantDTO(
                noma=student_peps_sport_type.student.registration_id,
                nom=student_peps_sport_type.student.person.last_name,
                prenom=student_peps_sport_type.student.person.first_name,
                peps=EtudiantPepsDTO(
                    type_peps=student_peps_sport_type.type,
                    sous_type_peps=student_peps_sport_type.subtype_sport,
                    tiers_temps=student_peps_sport_type.arrangement_additional_time,
                    copie_adaptee=student_peps_sport_type.arrangement_appropriate_copy,
                    local_specifique=student_peps_sport_type.arrangement_specific_locale,
                    autre_amenagement=student_peps_sport_type.arrangement_other,
                    details_autre_amenagement=student_peps_sport_type.arrangement_comment,
                    accompagnateur='',
                ),
            )
        }
        self.assertSetEqual(expected_result, result)

    def test_should_calculer_sous_type_peps_en_fonction_handicap_type_peps(self):
        student_peps_sport_type = StudentSpecificProfileFactory(
            type=PepsTypes.DISABILITY.name,
            subtype_disability=HtmSubtypes.REDUCED_MOBILITY.name
        )

        result = self.translator.search([student_peps_sport_type.student.registration_id])
        self.assertEqual(len(result), 1)
        expected_result = {
            SignaletiqueEtudiantDTO(
                noma=student_peps_sport_type.student.registration_id,
                nom=student_peps_sport_type.student.person.last_name,
                prenom=student_peps_sport_type.student.person.first_name,
                peps=EtudiantPepsDTO(
                    type_peps=student_peps_sport_type.type,
                    sous_type_peps=student_peps_sport_type.subtype_disability,
                    tiers_temps=student_peps_sport_type.arrangement_additional_time,
                    copie_adaptee=student_peps_sport_type.arrangement_appropriate_copy,
                    local_specifique=student_peps_sport_type.arrangement_specific_locale,
                    autre_amenagement=student_peps_sport_type.arrangement_other,
                    details_autre_amenagement=student_peps_sport_type.arrangement_comment,
                    accompagnateur='',
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
                peps=None,
            )
        }
        self.assertSetEqual(expected_result, result)

    def test_should_trouver_etudiant_par_nom(self):
        student = StudentFactory()

        self.assertEqual(
            len(self.translator.search([], nom=student.person.last_name)),
            1
        )

    def test_should_trouver_etudiant_par_prenom(self):
        StudentFactory(person__first_name="Icampos")
        StudentFactory(person__first_name="Icampos")
        StudentFactory(person__first_name="Other")

        self.assertEqual(
            len(self.translator.search([], prenom="Icamp")),
            2
        )
