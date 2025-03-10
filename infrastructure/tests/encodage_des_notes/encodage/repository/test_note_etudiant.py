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

    def test_should_save_note_manquante(self):
        note_manquante = NoteManquanteEtudiantFactory()
        self._create_save_necessary_data(note_manquante)
        self.repo.save(note_manquante)

        assert_attrs_instances_are_equal(note_manquante, self.repo.get(note_manquante.entity_id))

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

    def test_should_search_notes_etudiant_by_entity_id(self):
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

    def test_should_search_notes_etudiant_by_code_unite_enseignement_annee_session(self):
        note_chiffree = NoteEtudiantChiffreeFactory()
        self._create_save_necessary_data(note_chiffree)
        self.repo.save(note_chiffree)

        result = self.repo.search_by_code_unite_enseignement_annee_session(
            {(note_chiffree.code_unite_enseignement, note_chiffree.annee_academique, note_chiffree.numero_session)}
        )
        self.assertCountEqual(result, [note_chiffree])

    def test_should_ordonne_par_code_unite_enseignement_nom_cohorte_annee_academique_session_noma(self):
        note_chiffree_1 = NoteEtudiantChiffreeFactory(
            entity_id__code_unite_enseignement='LAGRO1200',
            entity_id__annee_academique=2021,
            entity_id__numero_session=2,
            entity_id__noma="987654321",
            nom_cohorte='DROI1BA'
        )
        note_chiffree_2 = NoteEtudiantChiffreeFactory(
            entity_id__code_unite_enseignement='LAGRO1200',
            entity_id__annee_academique=2021,
            entity_id__numero_session=2,
            entity_id__noma="654987321",
            nom_cohorte='DROI1BA'
        )

        self._create_save_necessary_data(note_chiffree_1)
        self._create_save_necessary_data(note_chiffree_2)

        results = self.repo.search(noms_cohortes=['DROI1BA'])
        self.assertEqual(len(results), 2)

        # Noma "654987321" < "987654321"
        self.assertEqual(results[0].noma, note_chiffree_2.entity_id.noma)
        self.assertEqual(results[1].noma, note_chiffree_1.entity_id.noma)

    def test_should_search_notes_identites(self):
        note_chiffree = NoteEtudiantChiffreeFactory(
            entity_id__code_unite_enseignement='LAGRO1200',
            entity_id__annee_academique=2021,
            entity_id__numero_session=2,
            entity_id__noma="987654321",
            nom_cohorte='DROI11BA'
        )

        self._create_save_necessary_data(note_chiffree)

        results = self.repo.search_notes_identites(noms_cohortes=['DROI11BA'])
        self.assertSetEqual({note_chiffree.entity_id}, results)

    def test_should_not_return_identite_of_11ba_when_searching_for_1ba(self):
        note_chiffree = NoteEtudiantChiffreeFactory(
            entity_id__code_unite_enseignement='LAGRO1200',
            entity_id__annee_academique=2021,
            entity_id__numero_session=2,
            entity_id__noma="987654321",
            nom_cohorte='DROI11BA'
        )

        self._create_save_necessary_data(note_chiffree)

        results = self.repo.search_notes_identites(noms_cohortes=['DROI1BA'])
        self.assertSetEqual(set(), results)

    def _create_save_necessary_data(self, note_etudiant_to_save, for_class: bool = False):
        luy_acronym = note_etudiant_to_save.code_unite_enseignement
        if for_class:
            luy_acronym = luy_acronym[:-2]

        luy = LearningUnitYearFactory(
            acronym=luy_acronym,
            academic_year__year=note_etudiant_to_save.entity_id.annee_academique,
            credits=20 if note_etudiant_to_save.note_decimale_autorisee else 10,
        )

        class_attributes = {
            "learning_unit_enrollment__learning_class_year": LearningClassYearFactory(
                learning_component_year__learning_unit_year=luy,
                learning_component_year__lecturing=True,
                acronym=note_etudiant_to_save.entity_id.code_unite_enseignement[-1]
            )
        } if for_class else {}

        offer_enrollment_attributes = {
            'learning_unit_enrollment__offer_enrollment__education_group_year__acronym':
                note_etudiant_to_save.nom_cohorte.replace('11BA', '1BA'),
            'learning_unit_enrollment__offer_enrollment__for_11ba': '11BA' in note_etudiant_to_save.nom_cohorte
        }

        enrollment = ExamEnrollmentFactory(
            session_exam__number_session=note_etudiant_to_save.entity_id.numero_session,
            learning_unit_enrollment__learning_unit_year=luy,
            learning_unit_enrollment__offer_enrollment__student__registration_id=note_etudiant_to_save.noma,
            learning_unit_enrollment__offer_enrollment__student__person__email=note_etudiant_to_save.email,
            **offer_enrollment_attributes,
            **class_attributes
        )
        SessionExamDeadlineFactory(
            offer_enrollment=enrollment.learning_unit_enrollment.offer_enrollment,
            number_session=note_etudiant_to_save.numero_session,
            deadline=note_etudiant_to_save.echeance_gestionnaire.to_date(),
            deadline_tutor=0
        )
