#############################################################################
#  OSIS stands for Open Student Information System. It's an application
#  designed to manage the core business of higher education institutions,
#  such as universities, faculties, institutes and professional schools.
#  The core business involves the administration of students, teachers,
#  courses, programs and so on.
#
#  Copyright (C) 2015-2022 Université catholique de Louvain (http://www.uclouvain.be)
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  A copy of this license - GNU General Public License - is available
#  at the root of the source code of this program.  If not,
#  see http://www.gnu.org/licenses/.
# ############################################################################
from decimal import Decimal

from django.test import SimpleTestCase

from ddd.logic.program_management.builder.contenu_noeud_dto_builder import _convertir_link_vers_unite_enseignement_DTO
from program_management.tests.ddd.factories.link import LinkFactory
from program_management.tests.ddd.factories.node import NodeGroupYearFactory, NodeLearningUnitYearFactory


class TestContenuNoeudDTOBuilder(SimpleTestCase):

    def setUp(self) -> None:
        noeud_contenant = NodeGroupYearFactory()

        self.unite_enseignement_volumes_non_nuls = NodeLearningUnitYearFactory(
            volume_total_lecturing=Decimal(40),
            volume_total_practical=Decimal(50)
        )
        unite_enseignement_volumes_nuls = NodeLearningUnitYearFactory(
            volume_total_lecturing=None,
            volume_total_practical=None
        )

        self.lien_ue_avec_volumes_non_nuls = LinkFactory(
            parent=noeud_contenant,
            child=self.unite_enseignement_volumes_non_nuls,
        )
        self.lien_ue_avec_volumes_nuls = LinkFactory(
            parent=noeud_contenant,
            child=unite_enseignement_volumes_nuls
        )

    def test_conversion_unite_enseignement_volumes_non_nuls_conversion_en_int(self):
        result = _convertir_link_vers_unite_enseignement_DTO(self.lien_ue_avec_volumes_non_nuls)

        self.assertEqual(result.volume_annuel_pm, int(self.unite_enseignement_volumes_non_nuls.volume_total_lecturing))
        self.assertEqual(result.volume_annuel_pp, int(self.unite_enseignement_volumes_non_nuls.volume_total_practical))

    def test_conversion_unite_enseignement_volumes_nuls_conversion_none_en_0(self):
        result = _convertir_link_vers_unite_enseignement_DTO(self.lien_ue_avec_volumes_nuls)

        self.assertEqual(result.volume_annuel_pm, 0)
        self.assertEqual(result.volume_annuel_pp, 0)


