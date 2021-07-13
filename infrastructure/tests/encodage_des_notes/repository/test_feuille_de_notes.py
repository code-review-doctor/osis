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
from ddd.logic.encodage_des_notes.tests.factory.feuille_de_notes import EmptyFeuilleDeNotesFactory, \
    FeuilleDeNotesSansNotesEncodees, FeuilleDeNotesAvecNotesEncodees, FeuilleDeNotesAvecNotesSoumises
from infrastructure.encodage_de_notes.soumission.repository.feuille_de_notes import FeuilleDeNotesRepository
from testing.assertions import assert_attrs_instances_are_equal


class FeuilleDeNotesRepositoryTest(TestCase):
    def setUp(self) -> None:
        self.feuille_de_notes_repository = FeuilleDeNotesRepository()

    def test_should_save_feuille_de_notes_vide(self):
        feuille_de_notes = EmptyFeuilleDeNotesFactory()
        self._create_save_necessary_data(feuille_de_notes)

        self.feuille_de_notes_repository.save(feuille_de_notes)
        feuille_de_notes_retrieved_from_repo = self.feuille_de_notes_repository.get(feuille_de_notes.entity_id)

        assert_attrs_instances_are_equal(feuille_de_notes, feuille_de_notes_retrieved_from_repo)

    def test_should_save_feuille_de_notes_sans_notes_encodees(self):
        feuille_de_notes = FeuilleDeNotesSansNotesEncodees()
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

    def test_should_return_empty_feuille_de_notes_if_no_matching_feuille_de_notes(self):
        feuille_de_notes_not_persisted = FeuilleDeNotesAvecNotesSoumises()

        retrieved_feuille_de_notes = self.feuille_de_notes_repository.get(feuille_de_notes_not_persisted.entity_id)

        self.assertEqual(retrieved_feuille_de_notes.entity_id, feuille_de_notes_not_persisted.entity_id)
        self.assertSetEqual(retrieved_feuille_de_notes.notes, set())

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

    def _create_save_necessary_data(self, feuille_de_notes_to_save):
        luy = LearningUnitYearFactory(
            acronym=feuille_de_notes_to_save.entity_id.code_unite_enseignement,
            academic_year__year=feuille_de_notes_to_save.entity_id.annee_academique
        )

        for note in feuille_de_notes_to_save.notes:
            enrollment = ExamEnrollmentFactory(
                session_exam__number_session=feuille_de_notes_to_save.entity_id.numero_session,
                session_exam__learning_unit_year=luy,
                learning_unit_enrollment__learning_unit_year=luy,
                learning_unit_enrollment__offer_enrollment__student__registration_id=note.entity_id.noma
            )
            SessionExamDeadlineFactory(
                offer_enrollment=enrollment.learning_unit_enrollment.offer_enrollment,
                deadline=note.date_limite_de_remise,
                deadline_tutor=0
            )
