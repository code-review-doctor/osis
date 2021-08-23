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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.test import TestCase

from base.tests.factories.exam_enrollment import ExamEnrollmentFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.session_exam_deadline import SessionExamDeadlineFactory
from ddd.logic.encodage_des_notes.soumission.test.factory.note_etudiant import NoteManquanteEtudiantFactory, \
    NoteChiffreEtudiantFactory, NoteJustificationEtudiantFactory
from infrastructure.encodage_de_notes.soumission.repository.note_etudiant import NoteEtudiantRepository
from learning_unit.tests.factories.learning_class_year import LearningClassYearFactory
from testing.assertions import assert_attrs_instances_are_equal


class NoteEtudiantRepositoryTest(TestCase):
    def setUp(self) -> None:
        self.note_etudiant_repository = NoteEtudiantRepository()

    def test_should_save_note_manquante(self):
        note_etudiant = NoteManquanteEtudiantFactory()
        self._create_save_necessary_data(note_etudiant)

        self.note_etudiant_repository.save(note_etudiant)
        note_retrieved_from_repo = self.note_etudiant_repository.get(note_etudiant.entity_id)

        assert_attrs_instances_are_equal(note_etudiant, note_retrieved_from_repo)

    def test_should_save_note_chiffree_encodee(self):
        note_etudiant = NoteChiffreEtudiantFactory()
        self._create_save_necessary_data(note_etudiant)

        self.note_etudiant_repository.save(note_etudiant)

        note_retrieved_from_repo = self.note_etudiant_repository.get(note_etudiant.entity_id)

        assert_attrs_instances_are_equal(note_etudiant, note_retrieved_from_repo)

    def test_should_save_note_de_justification_encodee(self):
        note_etudiant = NoteJustificationEtudiantFactory()
        self._create_save_necessary_data(note_etudiant)

        self.note_etudiant_repository.save(note_etudiant)

        note_retrieved_from_repo = self.note_etudiant_repository.get(note_etudiant.entity_id)

        assert_attrs_instances_are_equal(note_etudiant, note_retrieved_from_repo)

    def test_should_save_note_soumise(self):
        note_etudiant = NoteChiffreEtudiantFactory(est_soumise=True)
        self._create_save_necessary_data(note_etudiant)

        self.note_etudiant_repository.save(note_etudiant)

        note_retrieved_from_repo = self.note_etudiant_repository.get(note_etudiant.entity_id)

        assert_attrs_instances_are_equal(note_etudiant, note_retrieved_from_repo)

    def test_should_save_note_pour_une_classe(self):
        note_etudiant = NoteChiffreEtudiantFactory(for_class=True)
        self._create_save_necessary_data(note_etudiant, for_class=True)

        self.note_etudiant_repository.save(note_etudiant)
        note_retrieved_from_repo = self.note_etudiant_repository.get(note_etudiant.entity_id)

        assert_attrs_instances_are_equal(note_etudiant, note_retrieved_from_repo)

    def test_should_raise_exception_if_no_note(self):
        note_etudiant_not_persisted = NoteChiffreEtudiantFactory()

        with self.assertRaises(IndexError):
            self.note_etudiant_repository.get(note_etudiant_not_persisted.entity_id)

    def test_should_search_notes_etudiant_by_entity_ids(self):
        notes_etudiant = [NoteChiffreEtudiantFactory(), NoteChiffreEtudiantFactory()]
        for note in notes_etudiant:
            self._create_save_necessary_data(note)
            self.note_etudiant_repository.save(note)

        notes_retrieved = self.note_etudiant_repository.search([note.entity_id for note in notes_etudiant])

        for note in notes_etudiant:
            self.assertIn(note, notes_retrieved)

    def test_should_search_notes_etudiant_by_code_unite_enseignment_annee_session(self):
        notes_etudiant = [NoteChiffreEtudiantFactory(), NoteChiffreEtudiantFactory()]
        for note in notes_etudiant:
            self._create_save_necessary_data(note)
            self.note_etudiant_repository.save(note)

        notes_retrieved = self.note_etudiant_repository.search_by_code_unite_enseignement_annee_session(
            [('LDROI1001', 2020, 2)]
        )

        for note in notes_etudiant:
            self.assertIn(note, notes_retrieved)

    def _create_save_necessary_data(self, note_etudiant_to_save, for_class: bool = False):
        luy_acronym = note_etudiant_to_save.code_unite_enseignement
        if for_class:
            luy_acronym = luy_acronym[:-1]

        luy = LearningUnitYearFactory(
            acronym=luy_acronym,
            academic_year__year=note_etudiant_to_save.entity_id.annee_academique,
            credits=note_etudiant_to_save.credits_unite_enseignement,
        )

        class_attributes = {
            "learning_unit_enrollment__learning_class_year": LearningClassYearFactory(
                learning_component_year__learning_unit_year=luy,
                acronym=note_etudiant_to_save.entity_id.code_unite_enseignement[-1]
            )
        } if for_class else {}

        enrollment = ExamEnrollmentFactory(
            session_exam__number_session=note_etudiant_to_save.entity_id.numero_session,
            session_exam__learning_unit_year=luy,
            learning_unit_enrollment__learning_unit_year=luy,
            learning_unit_enrollment__offer_enrollment__student__registration_id=note_etudiant_to_save.noma,
            learning_unit_enrollment__offer_enrollment__student__person__email=note_etudiant_to_save.email,
            **class_attributes
        )
        SessionExamDeadlineFactory(
            offer_enrollment=enrollment.learning_unit_enrollment.offer_enrollment,
            number_session=note_etudiant_to_save.numero_session,
            deadline=note_etudiant_to_save.get_date_limite_de_remise(),
            deadline_tutor=0
        )
