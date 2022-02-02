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
from ddd.logic.preparation_programme_annuel_etudiant.commands import SupprimerUEDuProgrammeCommand, \
    GetUniteEnseignementCommand, AjouterUEAuProgrammeCommand
from ddd.logic.preparation_programme_annuel_etudiant.domain.validator.exceptions import \
    UniteEnseignementDejaSupprimeeException
from infrastructure.messages_bus import message_bus_instance
from infrastructure.preparation_programme_annuel_etudiant.repository.in_memory.groupement_ajuste_inscription_cours import \
    GroupementAjusteInscriptionCoursInMemoryRepository


class TestSupprimerUeDuProgramme(SimpleTestCase):

    def setUp(self) -> None:
        self.annee = 2021
        self.code_programme = 'LECGE100T'
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

    def test_should_supprimer_UE_cas_nominal(self):
        to_delete = ['LINGE1125', 'LINGE1122']
        groupement_ajuste_id = self.message_bus.invoke(
            SupprimerUEDuProgrammeCommand(
                annee=self.annee,
                code_programme=self.code_programme,
                retirer_de='LECGE100T',
                unites_enseignements=[GetUniteEnseignementCommand(code=code) for code in to_delete],
            )
        )
        groupement_ajuste = self.repository.get(groupement_ajuste_id)
        self.assertEqual('LINGE1125', groupement_ajuste.unites_enseignement_supprimees[0].code)
        self.assertEqual('LINGE1122', groupement_ajuste.unites_enseignement_supprimees[1].code)
        self.assertEqual('LECGE100T', groupement_ajuste.groupement_id.code)

    def test_should_retirer_UE_ajoutee_si_deja_ajoutee(self):
        groupement_ajuste_id = self.message_bus.invoke(
            AjouterUEAuProgrammeCommand(
                annee=self.annee,
                code_programme=self.code_programme,
                ajouter_dans='LECGE100T',
                unites_enseignements=['LINGE1111'],
            )
        )
        groupement_ajuste = self.repository.get(groupement_ajuste_id)
        self.message_bus.invoke(
            SupprimerUEDuProgrammeCommand(
                annee=self.annee,
                code_programme=self.code_programme,
                retirer_de='LECGE100T',
                unites_enseignements=[GetUniteEnseignementCommand(code='LINGE1111')],
            )
        )
        self.assertListEqual(groupement_ajuste.unites_enseignement_ajoutees, [])

    def test_should_empecher_supprimer_UE_deja_supprimee(self):
        to_delete = ['LINGE1125', 'LINGE1122']
        cmd = SupprimerUEDuProgrammeCommand(
            annee=self.annee,
            code_programme=self.code_programme,
            retirer_de='LECGE100T',
            unites_enseignements=[GetUniteEnseignementCommand(code=code) for code in to_delete],
        )
        groupement_ajuste_id = self.message_bus.invoke(cmd)
        with self.assertRaises(MultipleBusinessExceptions) as class_exceptions:
            cmd = attr.evolve(cmd, unites_enseignements=[GetUniteEnseignementCommand(code='LINGE1125')])
            groupement_ajuste_id = self.message_bus.invoke(cmd)
        exception = class_exceptions.exception.exceptions.pop()
        self.assertIsInstance(exception, UniteEnseignementDejaSupprimeeException)
