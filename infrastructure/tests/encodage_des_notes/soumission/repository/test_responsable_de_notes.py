#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    unite_enseignementses, programs and so on.
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
import string

from django.test import TestCase

from assessments.models.score_responsible import ScoreResponsible
from assessments.tests.factories.score_responsible import ScoreResponsibleFactory, ScoreResponsibleOfClassFactory
from base.models.person import Person
from base.tests.factories.tutor import TutorFactory
from ddd.logic.encodage_des_notes.soumission.domain.model.responsable_de_notes import ResponsableDeNotes
from ddd.logic.encodage_des_notes.soumission.dtos import ResponsableDeNotesDTO
from ddd.logic.encodage_des_notes.soumission.test.factory.responsable_de_notes import \
    ResponsableDeNotesPourUneUniteEnseignement, \
    ResponsableDeNotesPourMultipleUniteEnseignements, ResponsableDeNotesPourClasse
from infrastructure.encodage_de_notes.soumission.repository.responsable_de_notes import ResponsableDeNotesRepository
from testing.assertions import assert_attrs_instances_are_equal


class ResponsableDeNotesRepositoryTest(TestCase):
    def setUp(self) -> None:
        self.responsable_de_notes_repository = ResponsableDeNotesRepository()

    def test_should_save_responsable_de_notes_pour_une_unite_enseignement(self):
        responsable = ResponsableDeNotesPourUneUniteEnseignement()
        self._create_necessary_data(responsable)

        self.responsable_de_notes_repository.save(responsable)

        responsable_retrieved = self.responsable_de_notes_repository.get(responsable.entity_id)

        assert_attrs_instances_are_equal(responsable, responsable_retrieved)

    def test_should_save_responsable_de_notes_pour_plusieurs_unite_enseignements(self):
        responsable = ResponsableDeNotesPourMultipleUniteEnseignements()
        self._create_necessary_data(responsable)

        self.responsable_de_notes_repository.save(responsable)

        responsable_retrieved = self.responsable_de_notes_repository.get(responsable.entity_id)

        assert_attrs_instances_are_equal(responsable, responsable_retrieved)

    def test_should_save_responsable_de_notes_pour_unite_enseignements_de_type_classe(self):
        responsable = ResponsableDeNotesPourClasse()
        self._create_necessary_data(responsable)

        self.responsable_de_notes_repository.save(responsable)

        responsable_retrieved = self.responsable_de_notes_repository.get(responsable.entity_id)

        assert_attrs_instances_are_equal(responsable, responsable_retrieved)

    def test_should_save_desassignation_pour_responsable_de_notes(self):
        responsable = ResponsableDeNotesPourMultipleUniteEnseignements()
        self._create_necessary_data(responsable)

        self.responsable_de_notes_repository.save(responsable)

        responsable.unites_enseignements.pop()

        self.responsable_de_notes_repository.save(responsable)

        responsable_retrieved = self.responsable_de_notes_repository.get(responsable.entity_id)

        assert_attrs_instances_are_equal(responsable, responsable_retrieved)

    def test_should_save_desassignation_tout_les_responsable_de_notes_pour_une_unite_enseignements(self):
        responsable = ResponsableDeNotesPourClasse()
        self._create_necessary_data(responsable)

        self.responsable_de_notes_repository.save(responsable)

        responsable.unites_enseignements.pop()
        responsable.unites_enseignements.pop()

        self.responsable_de_notes_repository.save(responsable)

        self.assertIsNone(self.responsable_de_notes_repository.get(responsable.entity_id))

    def test_should_get_responsable_de_notes_par_cours(self):
        responsable = ResponsableDeNotesPourUneUniteEnseignement()
        self._create_necessary_data(responsable)

        self.responsable_de_notes_repository.save(responsable)

        responsable_retrieved = self.responsable_de_notes_repository.get_for_unite_enseignement("LDROI1001", 2020)

        assert_attrs_instances_are_equal(responsable, responsable_retrieved)

    def test_get_for_unite_enseignement_should_retouner_none_quand_pas_de_responsable(self):
        responsable_retrieved = self.responsable_de_notes_repository.get_for_unite_enseignement("LDROI1001", 2020)

        self.assertIsNone(responsable_retrieved)

    def test_should_search_responsable_de_notes_by_entity_ids(self):
        responsables = [
            ResponsableDeNotesPourUneUniteEnseignement(),
            ResponsableDeNotesPourMultipleUniteEnseignements()
        ]
        for responsable in responsables:
            self._create_necessary_data(responsable)
            self.responsable_de_notes_repository.save(responsable)

        responsables_retrieved = self.responsable_de_notes_repository.search(
            [responsable.entity_id for responsable in responsables]
        )
        self.assertCountEqual(responsables_retrieved, responsables)

    def test_search_responsable_de_notes_by_entity_ids_should_return_empty_list_when_no_matching_entity_id(self):
        responsable = ResponsableDeNotesPourUneUniteEnseignement()
        self._create_necessary_data(responsable)
        self.responsable_de_notes_repository.save(responsable)

        enseignant_dto = self.responsable_de_notes_repository.get_detail_enseignant(responsable.entity_id)
        responsable_db = ScoreResponsible.objects.get(
            tutor__person__global_id=responsable.entity_id.matricule_fgs_enseignant
        )
        self.assertEqual(enseignant_dto.prenom, responsable_db.tutor.person.first_name)
        self.assertEqual(enseignant_dto.nom, responsable_db.tutor.person.last_name)

    def test_should_renvoyer_details_enseignants(self):
        responsable_not_persisted = ResponsableDeNotesPourUneUniteEnseignement()

        responsables_retrieved = self.responsable_de_notes_repository.search([responsable_not_persisted.entity_id])

        self.assertListEqual(responsables_retrieved, [])

    def test_should_search_dto_renvoyer_responsable_dto(self):
        responsable = ResponsableDeNotesPourUneUniteEnseignement()
        self._create_necessary_data(responsable)
        self.responsable_de_notes_repository.save(responsable)

        unite_enseignement_identity = next(iter(responsable.unites_enseignements))
        responsable_notes_dto = self.responsable_de_notes_repository.search_dto(
            unite_enseignement_identities={unite_enseignement_identity}
        )

        person = Person.objects.get(global_id=responsable.entity_id.matricule_fgs_enseignant)
        self.assertListEqual(
            responsable_notes_dto,
            [
                ResponsableDeNotesDTO(
                    nom=person.last_name,
                    prenom=person.first_name,
                    matricule=person.global_id,
                    code_unite_enseignement=unite_enseignement_identity.code_unite_enseignement,
                    annee_unite_enseignement=unite_enseignement_identity.annee_academique,
                )
            ]
        )

    def test_should_search_dto_pas_de_resultat_renvoyer_liste_vide(self):
        responsable_not_persisted = ResponsableDeNotesPourUneUniteEnseignement()

        unite_enseignement_identity = next(iter(responsable_not_persisted.unites_enseignements))
        responsables_retrieved = self.responsable_de_notes_repository.search_dto(
            unite_enseignement_identities={unite_enseignement_identity}
        )

        self.assertListEqual(responsables_retrieved, [])

    def test_should_recomposer_responsable_avec_toutes_ses_UEs_si_recherche_sur_1_seule_UE(self):
        responsable = ResponsableDeNotesPourMultipleUniteEnseignements()
        self._create_necessary_data(responsable)
        self.responsable_de_notes_repository.save(responsable)

        responsable_retrieved_from_search = self.responsable_de_notes_repository.search(
            codes_unites_enseignement=["LOSIS1354"],
            annee_academique=2020
        )
        assert_attrs_instances_are_equal(responsable, responsable_retrieved_from_search[0])

        responsable_retrieved_from_get = self.responsable_de_notes_repository.get_for_unite_enseignement(
            "LOSIS1354",
            2020
        )
        assert_attrs_instances_are_equal(responsable, responsable_retrieved_from_get)

    def _create_necessary_data(self, responsable: 'ResponsableDeNotes'):
        tutor = TutorFactory(person__global_id=responsable.entity_id.matricule_fgs_enseignant)
        for identite_ue in responsable.unites_enseignements:
            if self._is_class_acronym(identite_ue.code_unite_enseignement):
                ScoreResponsibleOfClassFactory(
                    tutor=tutor,
                    learning_unit_year__acronym=identite_ue.code_unite_enseignement[:-2],
                    learning_unit_year__academic_year__year=identite_ue.annee_academique,
                    learning_class_year__acronym=identite_ue.code_unite_enseignement[-1]
                )
            else:
                ScoreResponsibleFactory(
                    tutor=tutor,
                    learning_unit_year__acronym=identite_ue.code_unite_enseignement,
                    learning_unit_year__academic_year__year=identite_ue.annee_academique
                )

    def _is_class_acronym(self, acronym) -> bool:
        return acronym[-1] in string.ascii_letters
