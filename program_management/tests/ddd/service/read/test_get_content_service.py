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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from decimal import Decimal

import mock
from django.test import TestCase

from education_group.tests.ddd.factories.domain.training import TrainingFactory
from infrastructure.messages_bus import message_bus_instance
from program_management.ddd.command import GetContenuGroupementCatalogueCommand
from program_management.ddd.domain.program_tree_version import NOT_A_TRANSITION
from program_management.ddd.domain.program_tree_version import ProgramTreeVersionIdentity
from program_management.tests.ddd.factories.link import LinkFactory
from program_management.tests.ddd.factories.node import NodeLearningUnitYearFactory, NodeGroupYearFactory
from program_management.tests.ddd.factories.program_tree import ProgramTreeFactory
from program_management.tests.ddd.factories.program_tree_version import ProgramTreeVersionFactory


class GetContentServiceTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.training = TrainingFactory(entity_identity__year=2025, persist=False)
        cls.code_programme = 'LDROI1200M'
        cls.root_node = NodeGroupYearFactory(year=cls.training.year, code=cls.code_programme)
        cls.program_tree_version = ProgramTreeVersionFactory(
            entity_id=ProgramTreeVersionIdentity(
                offer_acronym=cls.training.acronym,
                year=cls.training.year,
                version_name="",
                transition_name=NOT_A_TRANSITION
            ),
            tree=ProgramTreeFactory(root_node=cls.root_node)
        )
        cls.unite_enseignement_volumes_non_nuls = NodeLearningUnitYearFactory(
            volume_total_lecturing=Decimal(40),
            volume_total_practical=Decimal(50)
        )
        unite_enseignement_volumes_nuls = NodeLearningUnitYearFactory(
            volume_total_lecturing=None,
            volume_total_practical=None
        )

        cls.lien_ue_avec_volumes_non_nuls = LinkFactory(
            parent=cls.root_node,
            child=cls.unite_enseignement_volumes_non_nuls,
        )
        cls.lien_ue_avec_volumes_nuls = LinkFactory(
            parent=cls.root_node,
            child=unite_enseignement_volumes_nuls
        )

    def setUp(self) -> None:
        message_bus_patcher = mock.patch(
            'infrastructure.messages_bus',
        )
        message_bus_patcher.start()
        self.addCleanup(message_bus_patcher.stop)

        self.message_bus = message_bus_instance

    @mock.patch("program_management.ddd.repositories.program_tree_version.ProgramTreeVersionRepository.get")
    @mock.patch(
        "program_management.ddd.domain.service.identity_search.ProgramTreeVersionIdentitySearch.get_from_node_identity"
    )
    def test_conversion_unite_enseignement_volumes_non_nuls_conversion_en_int(
            self,
            mock_get_from_node_identity,
            mock_get_tree
    ):
        cmd = GetContenuGroupementCatalogueCommand(
            annee=self.training.year,
            code_groupement=self.code_programme,
            code_programme=self.code_programme
        )

        mock_get_tree.return_value = self.program_tree_version
        results = self.message_bus.invoke(cmd)

        resultat_ue_avec_volumes = results.contenu_ordonne[0]
        self.assertEqual(
            resultat_ue_avec_volumes.volume_annuel_pm,
            int(self.unite_enseignement_volumes_non_nuls.volume_total_lecturing)
        )
        self.assertEqual(
            resultat_ue_avec_volumes.volume_annuel_pp,
            int(self.unite_enseignement_volumes_non_nuls.volume_total_practical)
        )

        resultat_ue_volumes_none = results.contenu_ordonne[1]
        self.assertEqual(resultat_ue_volumes_none.volume_annuel_pm, 0)
        self.assertEqual(resultat_ue_volumes_none.volume_annuel_pp, 0)
