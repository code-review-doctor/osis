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
from ddd.logic.encodage_des_notes.tests.factory.feuille_de_notes import FeuilleDeNotesAvecNotesManquantes, \
    FeuilleDeNotesAvecNotesEncodees, FeuilleDeNotesAvecNotesSoumises
from infrastructure.encodage_de_notes.soumission.repository.feuille_de_notes import FeuilleDeNotesRepository
from learning_unit.tests.factories.learning_class_year import LearningClassYearFactory
from testing.assertions import assert_attrs_instances_are_equal


class FeuilleDeNotesRepositoryTest(TestCase):
    def setUp(self) -> None:
        self.feuille_de_notes_repository = FeuilleDeNotesRepository()

    def test_should_save_feuille_de_notes_avec_notes_manquantes(self):
        feuille_de_notes = FeuilleDeNotesAvecNotesManquantes()
        self._create_save_necessary_data(feuille_de_notes)

        self.feuille_de_notes_repository.save(feuille_de_notes)
        feuille_de_notes_retrieved_from_repo = self.feuille_de_notes_repository.get(feuille_de_notes.entity_id)

        assert_attrs_instances_are_equal(feuille_de_notes, feuille_de_notes_retrieved_from_repo)

    def test_should_save_feuille_de_notes_avec_notes_encodees(self):
        feuille_de_notes = FeuilleDeNotesAvecNotesEncodees()
        self._create_save_necessary_data(feuille_de_notes)

        self.feuille_de_notes_repository.save(feuille_de_notes)
        feuille_de_notes_retrieved_from_repo = self.feuille_de_notes_repository.get(feuille_de_notes.entity_id)

        assert_attrs_instances_are_equal(feuille_de_notes, feuille_de_notes_retrieved_from_repo)

    def test_should_save_feuille_de_notes_avec_notes_soumises(self):
        feuille_de_notes = FeuilleDeNotesAvecNotesSoumises()
        self._create_save_necessary_data(feuille_de_notes)

        self.feuille_de_notes_repository.save(feuille_de_notes)
        feuille_de_notes_retrieved_from_repo = self.feuille_de_notes_repository.get(feuille_de_notes.entity_id)

        assert_attrs_instances_are_equal(feuille_de_notes, feuille_de_notes_retrieved_from_repo)

    def test_should_save_feuille_de_notes_for_class(self):
        feuille_de_notes = FeuilleDeNotesAvecNotesSoumises(for_class=True)
        self._create_save_necessary_data(feuille_de_notes, for_class=True)

        self.feuille_de_notes_repository.save(feuille_de_notes)
        feuille_de_notes_retrieved_from_repo = self.feuille_de_notes_repository.get(feuille_de_notes.entity_id)

        assert_attrs_instances_are_equal(feuille_de_notes, feuille_de_notes_retrieved_from_repo)

    def test_should_raise_exception_if_no_feuille_de_notes(self):
        feuille_de_notes_not_persisted = FeuilleDeNotesAvecNotesSoumises()

        with self.assertRaises(IndexError):
            self.feuille_de_notes_repository.get(feuille_de_notes_not_persisted.entity_id)

    def test_should_search_feuilles_de_notes_by_entity_ids(self):
        feuilles_de_notes = [FeuilleDeNotesAvecNotesEncodees(), FeuilleDeNotesAvecNotesSoumises()]
        for feuille in feuilles_de_notes:
            self._create_save_necessary_data(feuille)
            self.feuille_de_notes_repository.save(feuille)

        feuilles_de_notes_retrieved = self.feuille_de_notes_repository.search(
            [feuilles_de_note.entity_id for feuilles_de_note in feuilles_de_notes]
        )

        for feuille in feuilles_de_notes:
            self.assertIn(feuille, feuilles_de_notes_retrieved)

    def test_should_(self):
        feuille_de_notes = FeuilleDeNotesAvecNotesEncodees()
        self._create_save_necessary_data(feuille_de_notes)
        FeuilleDeNotesRepository().get_progression_generale(feuille_de_notes.entity_id)

    def _create_save_necessary_data(self, feuille_de_notes_to_save, for_class: bool = False):
        luy_acronym = feuille_de_notes_to_save.entity_id.code_unite_enseignement
        if for_class:
            luy_acronym = luy_acronym[:-1]

        luy = LearningUnitYearFactory(
            acronym=luy_acronym,
            academic_year__year=feuille_de_notes_to_save.entity_id.annee_academique,
            credits=feuille_de_notes_to_save.credits_unite_enseignement,
        )

        class_attributes = {
            "learning_unit_enrollment__learning_class_year": LearningClassYearFactory(
                learning_component_year__learning_unit_year=luy,
                acronym=feuille_de_notes_to_save.entity_id.code_unite_enseignement[-1]
            )
        } if for_class else {}

        for note in feuille_de_notes_to_save.notes:
            enrollment = ExamEnrollmentFactory(
                session_exam__number_session=feuille_de_notes_to_save.entity_id.numero_session,
                session_exam__learning_unit_year=luy,
                learning_unit_enrollment__learning_unit_year=luy,
                learning_unit_enrollment__offer_enrollment__student__registration_id=note.entity_id.noma,
                learning_unit_enrollment__offer_enrollment__student__person__email=note.email,
                **class_attributes
            )
            SessionExamDeadlineFactory(
                offer_enrollment=enrollment.learning_unit_enrollment.offer_enrollment,
                deadline=note.date_limite_de_remise,
                deadline_tutor=0
            )
