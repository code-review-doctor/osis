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
from ddd.logic.encodage_des_notes.encodage.test.factory.note_etudiant import NoteEtudiantChiffreeFactory, \
    NoteEtudiantJustificationFactory, NoteManquanteEtudiantFactory
from infrastructure.encodage_de_notes.encodage.repository.note_etudiant import NoteEtudiantRepository
from learning_unit.tests.factories.learning_class_year import LearningClassYearFactory
from testing.assertions import assert_attrs_instances_are_equal


class TestNoteEtudiant(TestCase):
    @classmethod
    def setUpTestData(cls):
        pass

    def setUp(self) -> None:
        self.repo = NoteEtudiantRepository()

    def test_should_save_note_etudiant_chiffree(self):
        note_chiffree = NoteEtudiantChiffreeFactory()
        self._create_save_necessary_data(note_chiffree)
        self.repo.save(note_chiffree)

        assert_attrs_instances_are_equal(note_chiffree, self.repo.get(note_chiffree.entity_id))

    def test_should_save_note_etudiant_justification(self):
        note_justification = NoteEtudiantJustificationFactory()
        self._create_save_necessary_data(note_justification)
        self.repo.save(note_justification)

        assert_attrs_instances_are_equal(note_justification, self.repo.get(note_justification.entity_id))

    def test_should_save_note_etudiant_for_classe(self):
        note_chiffree = NoteEtudiantChiffreeFactory(for_class=True)
        self._create_save_necessary_data(note_chiffree, for_class=True)
        self.repo.save(note_chiffree)

        assert_attrs_instances_are_equal(note_chiffree, self.repo.get(note_chiffree.entity_id))

    def test_should_search_notes_etudiant(self):
        note_chiffree = NoteEtudiantChiffreeFactory()
        self._create_save_necessary_data(note_chiffree)
        self.repo.save(note_chiffree)

        note_justification = NoteEtudiantJustificationFactory()
        self._create_save_necessary_data(note_justification)
        self.repo.save(note_justification)

        result = self.repo.search([note_chiffree.entity_id, note_justification.entity_id])
        self.assertCountEqual(result, [note_chiffree, note_justification])

    def test_should_search_notes_etudiant_by_nomas(self):
        note_chiffree = NoteEtudiantChiffreeFactory()
        self._create_save_necessary_data(note_chiffree)
        self.repo.save(note_chiffree)

        result = self.repo.search(nomas=[note_chiffree.noma])
        self.assertCountEqual(result, [note_chiffree])

    def test_should_search_notes_etudiant_by_noms_cohortes(self):
        note_chiffree = NoteEtudiantChiffreeFactory()
        self._create_save_necessary_data(note_chiffree)
        self.repo.save(note_chiffree)

        result = self.repo.search(noms_cohortes=[note_chiffree.nom_cohorte])
        self.assertCountEqual(result, [note_chiffree])

    def test_should_search_notes_etudiant_by_note_manquante(self):
        note_chiffree = NoteEtudiantChiffreeFactory()
        self._create_save_necessary_data(note_chiffree)
        self.repo.save(note_chiffree)

        note_manquante = NoteManquanteEtudiantFactory()
        self._create_save_necessary_data(note_manquante)
        self.repo.save(note_manquante)

        result = self.repo.search(note_manquante=True)
        self.assertCountEqual(result, [note_manquante])

    def test_should_search_notes_etudiant_by_justification(self):
        note_chiffree = NoteEtudiantChiffreeFactory()
        self._create_save_necessary_data(note_chiffree)
        self.repo.save(note_chiffree)

        note_justification = NoteEtudiantJustificationFactory()
        self._create_save_necessary_data(note_justification)
        self.repo.save(note_justification)

        result = self.repo.search(justification=note_justification.note.value)
        self.assertCountEqual(result, [note_justification])

    def _create_save_necessary_data(self, note_etudiant_to_save, for_class: bool = False):
        luy_acronym = note_etudiant_to_save.code_unite_enseignement
        if for_class:
            luy_acronym = luy_acronym[:-1]

        luy = LearningUnitYearFactory(
            acronym=luy_acronym,
            academic_year__year=note_etudiant_to_save.entity_id.annee_academique,
            credits=20 if note_etudiant_to_save.note_decimale_autorisee else 10,
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
            learning_unit_enrollment__offer_enrollment__education_group_year__acronym=note_etudiant_to_save.nom_cohorte,

            **class_attributes
        )
        SessionExamDeadlineFactory(
            offer_enrollment=enrollment.learning_unit_enrollment.offer_enrollment,
            number_session=note_etudiant_to_save.numero_session,
            deadline=note_etudiant_to_save.echeance_gestionnaire,
            deadline_tutor=0
        )
