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
from ddd.logic.encodage_des_notes.soumission.builder.feuille_de_notes_identity_builder import \
    FeuilleDeNotesIdentityBuilder
from ddd.logic.encodage_des_notes.tests.factory.feuille_de_notes import EmptyFeuilleDeNotesFactory, \
    FeuilleDeNotesWithNoNotesEncoded, FeuilleDeNotesWithNotesEncoded, FeuilleDeNotesWithNotesSubmitted
from infrastructure.encodage_de_notes.soumission.repository.feuille_de_notes import FeuilleDeNotesRepository


class FeuilleDeNotesRepositoryTest(TestCase):
    def setUp(self) -> None:
        self.numero_session = 2

        self.luy = LearningUnitYearFactory()
        self.exam_enrollments = ExamEnrollmentFactory.build_batch(
            3,
            session_exam__number_session=self.numero_session,
            session_exam__learning_unit_year=self.luy,
            learning_unit_enrollment__learning_unit_year=self.luy
        )

        self.feuille_de_notes_repository = FeuilleDeNotesRepository()

    def test_save_empty_feuille_de_notes(self):
        empty_feuille_de_notes = EmptyFeuilleDeNotesFactory()
        self._create_save_necessary_datas(empty_feuille_de_notes)

        self.feuille_de_notes_repository.save(empty_feuille_de_notes)
        feuille_de_notes_retrived_from_repo = self.feuille_de_notes_repository.get(empty_feuille_de_notes.entity_id)

        self.assertEqual(empty_feuille_de_notes, feuille_de_notes_retrived_from_repo)

    def test_save_feuille_de_notes_with_no_notes_encoded(self):
        feuille_de_notes = FeuilleDeNotesWithNoNotesEncoded()
        self._create_save_necessary_datas(feuille_de_notes)

        self.feuille_de_notes_repository.save(feuille_de_notes)
        feuille_de_notes_retrived_from_repo = self.feuille_de_notes_repository.get(feuille_de_notes.entity_id)

        self.assertEqual(feuille_de_notes, feuille_de_notes_retrived_from_repo)

        for note in feuille_de_notes.notes:
            self.assertIn(note, feuille_de_notes_retrived_from_repo.notes)

    def test_save_feuille_de_notes_with_notes_encoded(self):
        feuille_de_notes = FeuilleDeNotesWithNotesEncoded()
        self._create_save_necessary_datas(feuille_de_notes)

        self.feuille_de_notes_repository.save(feuille_de_notes)
        feuille_de_notes_retrived_from_repo = self.feuille_de_notes_repository.get(feuille_de_notes.entity_id)

        self.assertEqual(feuille_de_notes, feuille_de_notes_retrived_from_repo)

        for note in feuille_de_notes.notes:
            self.assertIn(note, feuille_de_notes_retrived_from_repo.notes)

    def test_save_feuille_de_notes_with_notes_submitted(self):
        feuille_de_notes = FeuilleDeNotesWithNotesSubmitted()
        self._create_save_necessary_datas(feuille_de_notes)

        self.feuille_de_notes_repository.save(feuille_de_notes)
        feuille_de_notes_retrived_from_repo = self.feuille_de_notes_repository.get(feuille_de_notes.entity_id)

        self.assertEqual(feuille_de_notes, feuille_de_notes_retrived_from_repo)

        for note in feuille_de_notes.notes:
            self.assertIn(note, feuille_de_notes_retrived_from_repo.notes)

    def test_get_feuille_de_notes(self):
        entity_id = FeuilleDeNotesIdentityBuilder().build_from_session_and_unit_enseignement_datas(
            numero_session=self.numero_session,
            code_unite_enseignement=self.luy.acronym,
            annee_academique=self.luy.academic_year.year
        )
        result = self.feuille_de_notes_repository.get(
            entity_id=entity_id
        )

        self.assertEqual(result.entity_id, entity_id)

    def test_search_feuilles_de_notes(self):
        feuilles_de_notes = [FeuilleDeNotesWithNotesEncoded(), FeuilleDeNotesWithNotesSubmitted()]
        for feuille in feuilles_de_notes:
            self._create_save_necessary_datas(feuille)
            self.feuille_de_notes_repository.save(feuille)

        feuilles_de_notes_retrieved = self.feuille_de_notes_repository.search(
            [feuilles_de_note.entity_id for feuilles_de_note in feuilles_de_notes]
        )

        for feuille in feuilles_de_notes:
            self.assertIn(feuille, feuilles_de_notes_retrieved)

    def _create_save_necessary_datas(self, feuille_de_notes_to_save):
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
