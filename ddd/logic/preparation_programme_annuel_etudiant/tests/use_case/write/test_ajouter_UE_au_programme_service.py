##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2022 Université catholique de Louvain (http://www.uclouvain.be)
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
##############################################################################
from unittest import mock

import attr
from django.test import SimpleTestCase

from base.ddd.utils.business_validator import MultipleBusinessExceptions
from ddd.logic.preparation_programme_annuel_etudiant.commands import AjouterUEAuProgrammeCommand
from ddd.logic.preparation_programme_annuel_etudiant.domain.validator.exceptions import \
    UniteEnseignementDejaAjouteeException
from infrastructure.messages_bus import message_bus_instance
from infrastructure.preparation_programme_annuel_etudiant.repository.in_memory.groupement_ajuste_inscription_cours import \
    GroupementAjusteInscriptionCoursInMemoryRepository
from program_management.ddd.domain.program_tree_version import STANDARD


class TestAjouterUeAuProgramme(SimpleTestCase):

    def setUp(self) -> None:
        self.annee = 2021
        self.code_programme = 'LECGE100T'
        self.version_formation = STANDARD
        self.transition_formation = ''
        self.repository = GroupementAjusteInscriptionCoursInMemoryRepository()
        self.__mock_service_bus()

    def __mock_service_bus(self):
        message_bus_patcher = mock.patch.multiple(
            'infrastructure.messages_bus',
            GroupementAjusteInscriptionCoursInMemoryRepository=lambda: self.repository,
        )
        message_bus_patcher.start()
        self.addCleanup(message_bus_patcher.stop)
        self.message_bus = message_bus_instance

    def test_should_ajouter_UE_cas_nominal(self):
        groupement_ajuste_id = self.message_bus.invoke(
            AjouterUEAuProgrammeCommand(
                annee=self.annee,
                code_programme=self.code_programme,
                ajouter_dans='LECGE100T',
                unites_enseignements=['LINGE1125', 'LINGE1122'],
            )
        )
        groupement_ajuste = self.repository.get(groupement_ajuste_id)
        self.assertEqual('LINGE1125', groupement_ajuste.unites_enseignement_ajoutees[0].code)
        self.assertEqual('LINGE1122', groupement_ajuste.unites_enseignement_ajoutees[1].code)
        self.assertEqual('LECGE100T', groupement_ajuste.groupement_id.code)

    def test_should_empecher_ajouter_UE_deja_ajoutee(self):
        cmd = AjouterUEAuProgrammeCommand(
            annee=self.annee,
            code_programme=self.code_programme,
            ajouter_dans='LECGE100T',
            unites_enseignements=['LINGE1125', 'LINGE1122'],
        )
        self.message_bus.invoke(cmd)
        with self.assertRaises(MultipleBusinessExceptions) as class_exceptions:
            cmd = attr.evolve(cmd, unites_enseignements=['LINGE1125'])
            self.message_bus.invoke(cmd)
        exception = class_exceptions.exception.exceptions.pop()
        self.assertIsInstance(exception, UniteEnseignementDejaAjouteeException)
