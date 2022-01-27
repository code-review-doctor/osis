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

from ddd.logic.preparation_programme_annuel_etudiant.commands import GetProgrammeInscriptionCoursCommand
from infrastructure.messages_bus import message_bus_instance
from infrastructure.preparation_programme_annuel_etudiant.domain.service.in_memory.catalogue_formations import \
    CatalogueFormationsInMemoryTranslator
from infrastructure.preparation_programme_annuel_etudiant.repository.in_memory.groupement_ajuste_inscription_cours \
    import GroupementAjusteInscriptionCoursInMemoryRepository


class GetProgrammeInscriptionCoursTest(SimpleTestCase):

    def setUp(self) -> None:
        self.catalogue_formation_translator = CatalogueFormationsInMemoryTranslator()
        self.groupement_ajustes_repository = GroupementAjusteInscriptionCoursInMemoryRepository()
        self._mock_message_bus()

    def _mock_message_bus(self):
        message_bus_patcher = mock.patch.multiple(
            'infrastructure.messages_bus',
            CatalogueFormationsTranslator=lambda: self.catalogue_formation_translator,
            GroupementAjusteInscriptionCoursInMemoryRepository=lambda: self.groupement_ajustes_repository
        )
        message_bus_patcher.start()
        self.addCleanup(message_bus_patcher.stop)
        self.message_bus = message_bus_instance

    def test_should_visualiser_ECGE1BA_version_standard(self):
        cmd = GetProgrammeInscriptionCoursCommand(
            annee_formation=2021,
            sigle_formation='ECGE1BA',
            version_formation='',
            transition_formation='',
        )
        programme = self.message_bus.invoke(cmd)
        self.assertEqual(programme.code, 'LECGE100T')
        self.assertEqual(programme.annee, 2021)
        self.assertEqual(programme.version, '')
        self.assertEqual(programme.transition, '')
        self.assertEqual(programme.intitule_complet_formation, 'Bachelier en sciences économiques et de gestion')
        sous_programme = programme.sous_programme
        self.assertEqual(len(sous_programme), 1)
        groupement = sous_programme[0]
        self.assertEqual(groupement.intitule_complet, 'Content:')
        self.assertEqual(groupement.code, 'LECGE100T')
        self.assertTrue(groupement.obligatoire)
        unites_enseignements = groupement.unites_enseignements
        self.assertEqual(len(unites_enseignements), 1)
        unite_enseignement = unites_enseignements[0]
        self.assertEqual(unite_enseignement.code, 'LESPO1113')
        self.assertEqual(unite_enseignement.intitule, 'Sociologie et anthropologie des mondes contemporains')
        self.assertTrue(unite_enseignement.obligatoire)
        self.assertEqual(unite_enseignement.bloc, 1)
