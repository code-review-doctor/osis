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

from base.models.enums import exam_enrollment_state
from base.tests.factories.exam_enrollment import ExamEnrollmentFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from ddd.logic.encodage_des_notes.soumission.dtos import InscriptionExamenDTO, DesinscriptionExamenDTO
from infrastructure.encodage_de_notes.soumission.domain.service.inscription_examen import InscriptionExamenTranslator
from learning_unit.tests.factories.learning_class_year import LearningClassYearFactory


class InscriptionExamenTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.annee = 2020
        cls.numero_session = 2
        cls.code_unite_enseignement = 'LDROI1001'
        cls.translator = InscriptionExamenTranslator()

    def test_should_trouver_aucun_resultats(self):
        result = self.translator.search_inscrits(self.code_unite_enseignement, self.numero_session, self.annee)
        expected_result = set()
        self.assertSetEqual(expected_result, result)

    def test_should_trouver_2_inscriptions_unite_enseignement(self):
        unite_enseignement = LearningUnitYearFactory(
            academic_year__year=self.annee,
            acronym=self.code_unite_enseignement,
        )
        exam_1 = ExamEnrollmentFactory(
            learning_unit_enrollment__learning_unit_year=unite_enseignement,
            session_exam__number_session=self.numero_session,
            enrollment_state=exam_enrollment_state.ENROLLED,
        )
        exam_2 = ExamEnrollmentFactory(
            learning_unit_enrollment__learning_unit_year=unite_enseignement,
            session_exam__number_session=self.numero_session,
            enrollment_state=exam_enrollment_state.ENROLLED,
        )

        result = self.translator.search_inscrits(self.code_unite_enseignement, self.numero_session, self.annee)
        self.assertEqual(len(result), 2)
        expected_result = {
            InscriptionExamenDTO(
                annee=self.annee,
                noma=exam_1.learning_unit_enrollment.offer_enrollment.student.registration_id,
                code_unite_enseignement=self.code_unite_enseignement,
                sigle_formation=exam_1.learning_unit_enrollment.offer_enrollment.education_group_year.acronym,
                date_inscription=exam_1.date_enrollment,
            ),
            InscriptionExamenDTO(
                annee=self.annee,
                noma=exam_2.learning_unit_enrollment.offer_enrollment.student.registration_id,
                code_unite_enseignement=self.code_unite_enseignement,
                sigle_formation=exam_2.learning_unit_enrollment.offer_enrollment.education_group_year.acronym,
                date_inscription=exam_2.date_enrollment,
            ),
        }
        self.assertSetEqual(expected_result, result)

    def test_should_trouver_1_inscription_classe(self):
        class_year = LearningClassYearFactory(
            learning_component_year__learning_unit_year__academic_year__year=self.annee,
            learning_component_year__learning_unit_year__acronym=self.code_unite_enseignement,
            acronym='A'
        )
        exam_1 = ExamEnrollmentFactory(
            learning_unit_enrollment__learning_unit_year=class_year.learning_component_year.learning_unit_year,
            session_exam__number_session=self.numero_session,
            learning_unit_enrollment__learning_class_year=class_year,
            enrollment_state=exam_enrollment_state.ENROLLED,
        )

        result = self.translator.search_inscrits("LDROI1001A", self.numero_session, self.annee)
        self.assertEqual(len(result), 1)
        expected_result = {
            InscriptionExamenDTO(
                annee=self.annee,
                noma=exam_1.learning_unit_enrollment.offer_enrollment.student.registration_id,
                code_unite_enseignement='LDROI1001A',
                sigle_formation=exam_1.learning_unit_enrollment.offer_enrollment.education_group_year.acronym,
                date_inscription=exam_1.date_enrollment,
            )
        }
        self.assertSetEqual(expected_result, result)

    def test_should_trouver_1_desinscription_classe(self):
        class_year = LearningClassYearFactory(
            learning_component_year__learning_unit_year__academic_year__year=self.annee,
            learning_component_year__learning_unit_year__acronym=self.code_unite_enseignement,
            acronym='A'
        )
        exam_1 = ExamEnrollmentFactory(
            learning_unit_enrollment__learning_unit_year=class_year.learning_component_year.learning_unit_year,
            session_exam__number_session=self.numero_session,
            learning_unit_enrollment__learning_class_year=class_year,
            enrollment_state=exam_enrollment_state.NOT_ENROLLED,
        )

        result = self.translator.search_desinscrits("LDROI1001A", self.numero_session, self.annee)
        self.assertEqual(len(result), 1)
        expected_result = {
            DesinscriptionExamenDTO(
                annee=self.annee,
                noma=exam_1.learning_unit_enrollment.offer_enrollment.student.registration_id,
                code_unite_enseignement='LDROI1001A',
                sigle_formation=exam_1.learning_unit_enrollment.offer_enrollment.education_group_year.acronym,
            )
        }
        self.assertSetEqual(expected_result, result)

    def test_should_trouver_1_desinscriptions_unite_enseignement(self):
        unite_enseignement = LearningUnitYearFactory(
            academic_year__year=self.annee,
            acronym=self.code_unite_enseignement,
        )
        exam_1 = ExamEnrollmentFactory(
            learning_unit_enrollment__learning_unit_year=unite_enseignement,
            session_exam__number_session=self.numero_session,
            enrollment_state=exam_enrollment_state.NOT_ENROLLED,
        )
        result = self.translator.search_desinscrits(self.code_unite_enseignement, self.numero_session, self.annee)
        self.assertEqual(len(result), 1)
        expected_result = {
            DesinscriptionExamenDTO(
                annee=self.annee,
                noma=exam_1.learning_unit_enrollment.offer_enrollment.student.registration_id,
                code_unite_enseignement=self.code_unite_enseignement,
                sigle_formation=exam_1.learning_unit_enrollment.offer_enrollment.education_group_year.acronym,
            ),
        }
        self.assertSetEqual(expected_result, result)
