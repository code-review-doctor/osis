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

from base.tests.factories.entity_version import EntityVersionFactory
from ddd.logic.shared_kernel.entite.builder.identite_entite_builder import IdentiteEntiteBuilder
from infrastructure.shared_kernel.entite.repository.entiteucl import EntiteUCLRepository


class TestEntiteRepository(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.ucl_entity = EntityVersionFactory(acronym="UCL", parent=None)
        cls.sst_entity = EntityVersionFactory(acronym="SST", parent=cls.ucl_entity.entity)
        cls.epl_entity = EntityVersionFactory(acronym="EPL", parent=cls.sst_entity.entity)

        cls.identite_builder = IdentiteEntiteBuilder()

    def setUp(self) -> None:
        self.repo = EntiteUCLRepository()

    def test_search_with_parents_should_return_empty_list_if_no_matching_entite(self):
        identite = self.identite_builder.build_from_sigle("INFO")

        result = self.repo.search_with_parents([identite])

        self.assertListEqual(result, [])

    def test_search_with_parents_should_return_entity_if_no_parent(self):
        identite = self.identite_builder.build_from_sigle("UCL")

        result = self.repo.search_with_parents([identite])

        self.assertListEqual(
            [entite.sigle for entite in result],
            ["UCL"]
        )

    def test_search_with_parents_should_return_entity_with_parents(self):
        identite = self.identite_builder.build_from_sigle("EPL")

        result = self.repo.search_with_parents([identite])

        self.assertCountEqual(
            [entite.sigle for entite in result],
            ["UCL", "SST", "EPL"]
        )

    def test_get_should_return_entite(self):
        identite = self.identite_builder.build_from_sigle('EPL')

        result = self.repo.get(identite)

        self.assertTrue(result)
