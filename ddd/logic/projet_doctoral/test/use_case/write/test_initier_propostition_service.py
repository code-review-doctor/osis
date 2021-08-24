# ##############################################################################
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
# ##############################################################################
import mock
from django.test import SimpleTestCase

from ddd.logic.projet_doctoral.commands import InitierPropositionCommand
from ddd.logic.projet_doctoral.domain.model._financement import ChoixTypeFinancement
from ddd.logic.projet_doctoral.domain.model.proposition import ChoixTypeAdmission, Proposition
from ddd.logic.projet_doctoral.domain.validator.exceptions import MaximumPropositionsAtteintException
from ddd.logic.projet_doctoral.test.factory.proposition import (
    PropositionAdmissionSC3DPMinimaleAnnuleeFactory,
)
from infrastructure.messages_bus import message_bus_instance
from infrastructure.projet_doctoral.domain.service.in_memory.doctorat import DoctoratInMemoryTranslator
from infrastructure.projet_doctoral.repository.in_memory.proposition import PropositionInMemoryRepository


class TestInitierPropositionService(SimpleTestCase):
    def setUp(self) -> None:
        self.proposition_repository = PropositionInMemoryRepository()
        self.doctorat_translator = DoctoratInMemoryTranslator()
        message_bus_patcher = mock.patch.multiple(
            'infrastructure.messages_bus',
            PropositionRepository=lambda: self.proposition_repository,
            DoctoratTranslator=lambda: self.doctorat_translator,
        )
        message_bus_patcher.start()
        self.addCleanup(message_bus_patcher.stop)
        self.addCleanup(self.proposition_repository.reset)

        self.message_bus = message_bus_instance
        self.cmd = InitierPropositionCommand(
            type_admission=ChoixTypeAdmission.ADMISSION.name,
            sigle_formation='SC3DP',
            annee_formation=2020,
            matricule_candidat='01234567',
            bureau_CDE='',
            type_financement=ChoixTypeFinancement.SELF_FUNDING.name,
            type_contrat_travail='assistant_uclouvain',
            titre_projet='Mon projet',
            resume_projet='LE résumé de mon projet',
            documents_projet=[],
        )

    def test_should_initier(self):
        proposition_id = self.message_bus.invoke(self.cmd)
        proposition = self.proposition_repository.get(proposition_id)  # type: Proposition
        self.assertEqual(proposition_id, proposition.entity_id)
        self.assertEqual(ChoixTypeAdmission[self.cmd.type_admission], proposition.type_admission)
        self.assertEqual(self.cmd.sigle_formation, proposition.doctorat_id.sigle)
        self.assertEqual(self.cmd.annee_formation, proposition.doctorat_id.annee)
        self.assertEqual(self.cmd.matricule_candidat, proposition.matricule_candidat)
        self.assertEqual(self.cmd.bureau_CDE, proposition.bureau_CDE)
        self.assertEqual(ChoixTypeFinancement[self.cmd.type_financement], proposition.financement.type)
        self.assertEqual(self.cmd.type_contrat_travail, proposition.financement.type_contrat_travail)
        self.assertEqual(self.cmd.titre_projet, proposition.projet.titre)
        self.assertEqual(self.cmd.resume_projet, proposition.projet.resume)
        self.assertEqual(self.cmd.documents_projet, proposition.projet.documents)

    def test_should_empecher_si_maximum_propositions_autorisees(self):
        self.message_bus.invoke(self.cmd)
        with self.assertRaises(MaximumPropositionsAtteintException):
            self.message_bus.invoke(self.cmd)

    def test_should_initier_autre_proposition_si_premiere_annulee(self):
        # TODO This should be changed to the action that changes the status to cancelled
        self.proposition_repository.save(PropositionAdmissionSC3DPMinimaleAnnuleeFactory())
        proposition_id = self.message_bus.invoke(self.cmd)
        proposition = self.proposition_repository.get(proposition_id)  # type: Proposition
        self.assertEqual(proposition_id, proposition.entity_id)
