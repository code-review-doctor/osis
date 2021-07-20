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
import attr
from django.test import SimpleTestCase

from ddd.logic.encodage_des_notes.soumission.commands import AssignerResponsableDeNotesCommand
from ddd.logic.encodage_des_notes.soumission.domain.validator.exceptions import \
    EnseignantNonAttribueUniteEnseignementException
from ddd.logic.encodage_des_notes.soumission.dtos import AttributionEnseignantDTO
from ddd.logic.encodage_des_notes.soumission.use_case.write.assigner_responsable_de_notes_service import \
    assigner_responsable_de_notes
from ddd.logic.encodage_des_notes.tests.factory.responsable_de_notes import \
    ResponsableDeNotesPourUneUniteEnseignement, \
    ResponsableDeNotesPourMultipleUniteEnseignements
from infrastructure.encodage_de_notes.soumission.domain.service.attribution_enseignant import \
    AttributionEnseignantTranslator
from infrastructure.encodage_de_notes.soumission.repository.in_memory.responsable_de_notes import \
    ResponsableDeNotesInMemoryRepository


class TestAssignerResponsableDeNotes(SimpleTestCase):

    def setUp(self) -> None:
        self.responsable = ResponsableDeNotesPourUneUniteEnseignement()

        self.repo = ResponsableDeNotesInMemoryRepository()
        self.repo.save(self.responsable)

        self.cmd = AssignerResponsableDeNotesCommand(
            code_unite_enseignement="LOSIS1254",
            annee_unite_enseignement=2020,
            matricule_fgs_enseignant="25987111"
        )

        self.attribution_dto = AttributionEnseignantDTO(
            code_unite_enseignement=self.cmd.code_unite_enseignement,
            annee=self.cmd.annee_unite_enseignement,
        )
        self.attribution_translator = AttributionEnseignantTranslator()
        self.attribution_translator.search_attributions_enseignant = lambda **kwargs: {self.attribution_dto}

        self.addCleanup(lambda *args, **kwargs: self.repo.entities.clear())

    def test_cannot_assigner_enseignant_en_tant_que_responsable_de_notes_pour_unite_enseignement_non_attribuee(self):
        cmd = attr.evolve(self.cmd, code_unite_enseignement='LOSIS7896')

        with self.assertRaises(EnseignantNonAttribueUniteEnseignementException):
            assigner_responsable_de_notes(cmd, self.repo, self.attribution_translator)

    def test_should_desassigner_responsable_de_notes_actuelle_de_unite_enseignement(self):
        assigner_responsable_de_notes(self.cmd, self.repo, self.attribution_translator)

        self.assertSetEqual(self.responsable.unites_enseignements, set())

    def test_should_assigner_responsable_de_notes_pour_enseignant_non_encore_responsable_de_notes(self):
        entity_id = assigner_responsable_de_notes(self.cmd, self.repo, self.attribution_translator)

        responsable_retrieved = self.repo.get(entity_id)
        self.assertTrue(
            responsable_retrieved.est_responsable_de(
                self.cmd.code_unite_enseignement,
                self.cmd.annee_unite_enseignement
            )
        )

    def test_should_assigner_responsable_de_notes_pour_enseignant_deja_responsable_de_notes(self):
        responsable = ResponsableDeNotesPourMultipleUniteEnseignements()
        self.repo.save(responsable)
        cmd = attr.evolve(self.cmd, matricule_fgs_enseignant=responsable.matricule_fgs_enseignant)

        entity_id = assigner_responsable_de_notes(cmd, self.repo, self.attribution_translator)

        responsable_retrieved = self.repo.get(entity_id)
        self.assertTrue(responsable, responsable_retrieved)
        self.assertTrue(
            responsable_retrieved.est_responsable_de(
                self.cmd.code_unite_enseignement,
                self.cmd.annee_unite_enseignement
            )
        )
