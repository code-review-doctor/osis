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

from attribution.tests.factories.attribution_charge_new import AttributionChargeNewFactory
from base.tests.factories.tutor import TutorFactory
from ddd.logic.encodage_des_notes.soumission.domain.model.responsable_de_notes import ResponsableDeNotes
from ddd.logic.encodage_des_notes.tests.factory.responsable_de_notes import ResponsableDeNotesPourUnCours, \
    ResponsableDeNotesPourMultipleCours
from infrastructure.encodage_de_notes.soumission.repository.responsable_de_notes import ResponsableDeNotesRepository
from testing.assertions import assert_attrs_instances_are_equal


class ResponsableDeNotesRepositoryTest(TestCase):
    def setUp(self) -> None:
        self.responsable_de_notes_repository = ResponsableDeNotesRepository()

    def test_should_save_responsable_de_notes_pour_un_cours(self):
        responsable = ResponsableDeNotesPourUnCours()
        self._create_necessary_data(responsable)

        self.responsable_de_notes_repository.save(responsable)

        responsable_retrieved = self.responsable_de_notes_repository.get(responsable.entity_id)

        assert_attrs_instances_are_equal(responsable, responsable_retrieved)

    def test_should_save_responsable_de_notes_pour_plusieurs_cours(self):
        responsable = ResponsableDeNotesPourMultipleCours()
        self._create_necessary_data(responsable)

        self.responsable_de_notes_repository.save(responsable)

        responsable_retrieved = self.responsable_de_notes_repository.get(responsable.entity_id)

        assert_attrs_instances_are_equal(responsable, responsable_retrieved)

    def _create_necessary_data(self, responsable: 'ResponsableDeNotes'):
        tutor = TutorFactory(person__global_id=responsable.entity_id.matricule_fgs_enseignant)
        for identite_ue in responsable.unites_enseignements:
            AttributionChargeNewFactory(
                attribution__tutor=tutor,
                learning_component_year__learning_unit_year__acronym=identite_ue.code_unite_enseignement,
                learning_component_year__learning_unit_year__academic_year__year=identite_ue.annee_academique
            )
