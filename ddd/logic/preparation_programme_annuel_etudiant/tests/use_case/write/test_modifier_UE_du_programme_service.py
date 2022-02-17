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

from django.test import SimpleTestCase

from ddd.logic.preparation_programme_annuel_etudiant.commands import ModifierUEDuGroupementCommand, \
    ModifierUniteEnseignementCommand
from infrastructure.messages_bus import message_bus_instance
from infrastructure.preparation_programme_annuel_etudiant.repository.in_memory.groupement_ajuste_inscription_cours import \
    GroupementAjusteInscriptionCoursInMemoryRepository


class TestModifierUEDuProgramme(SimpleTestCase):

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

    def test_should_modifier_bloc_UE_cas_nominal(self):
        groupement_ajuste_id = self.message_bus.invoke(
            ModifierUEDuGroupementCommand(
                annee=self.annee,
                code_programme=self.code_programme,
                ajuster_dans='LECGE100R',
                unites_enseignements=[
                    ModifierUniteEnseignementCommand(
                        code='LESPO1113',
                        annee=self.annee,
                        bloc=2
                    )
                ],
            )
        )
        groupement_ajuste = self.repository.get(groupement_ajuste_id)
        self.assertEqual(
            'LESPO1113',
            groupement_ajuste.unites_enseignement_modifiees[0].unite_enseignement_identity.code
        )
        self.assertEqual(
            self.annee,
            groupement_ajuste.unites_enseignement_modifiees[0].unite_enseignement_identity.year
        )
        self.assertEqual(2, groupement_ajuste.unites_enseignement_modifiees[0].bloc)

    def test_should_modifier_bloc_UE_deja_modifie(self):
        groupement_ajuste_id = self.message_bus.invoke(
            ModifierUEDuGroupementCommand(
                annee=self.annee,
                code_programme=self.code_programme,
                ajuster_dans='LECGE100R',
                unites_enseignements=[
                    ModifierUniteEnseignementCommand(
                        code='LESPO1113',
                        annee=self.annee,
                        bloc=3
                    )
                ],
            )
        )
        groupement_ajuste = self.repository.get(groupement_ajuste_id)
        self.assertEqual(3, groupement_ajuste.unites_enseignement_modifiees[0].bloc)

        groupement_ajuste_id = self.message_bus.invoke(
            ModifierUEDuGroupementCommand(
                annee=self.annee,
                code_programme=self.code_programme,
                ajuster_dans='LECGE100R',
                unites_enseignements=[
                    ModifierUniteEnseignementCommand(
                        code='LESPO1113',
                        annee=self.annee,
                        bloc=2
                    )
                ],
            )
        )
        groupement_ajuste = self.repository.get(groupement_ajuste_id)
        self.assertEqual(len(groupement_ajuste.unites_enseignement_modifiees), 1)
        self.assertEqual(2, groupement_ajuste.unites_enseignement_modifiees[0].bloc)
