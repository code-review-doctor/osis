# ############################################################################
#  OSIS stands for Open Student Information System. It's an application
#  designed to manage the core business of higher education institutions,
#  such as universities, faculties, institutes and professional schools.
#  The core business involves the administration of students, teachers,
#  courses, programs and so on.
#
#  Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)
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
from unittest.mock import patch

from django.test import TestCase

from base.models.enums.constraint_type import ConstraintTypeEnum
from education_group.ddd import command
from education_group.ddd.domain import group
from education_group.ddd.service.write import update_group_service
from education_group.tests.ddd.factories.group import GroupFactory
from education_group.tests.ddd.factories.repository.group import get_fake_group_repository
from testing.mocks import MockPatcherMixin


@patch('education_group.ddd.service.write.update_group_service.'
       'CalculateEndPostponement.calculate_year_of_postponement', return_value=2021)
class TestUpdateGroup(TestCase, MockPatcherMixin):
    @classmethod
    def setUpTestData(cls):
        cls.cmd = command.UpdateGroupCommand(
            year=2018,
            code="LTRONC1",
            abbreviated_title="TRONC-COMMUN",
            title_fr="Tronc commun",
            title_en="Common core",
            credits=20,
            constraint_type=ConstraintTypeEnum.CREDITS.name,
            min_constraint=0,
            max_constraint=10,
            management_entity_acronym="DRT",
            teaching_campus_name="Mons Fucam",
            organization_name="UCLouvain",
            remark_fr="Remarque en français",
            remark_en="Remarque en anglais",
            end_year=None
        )

    def setUp(self) -> None:
        self.group_2018 = GroupFactory(entity_identity__code=self.cmd.code, entity_identity__year=2018)
        self.group_2019 = GroupFactory(entity_identity__code=self.cmd.code, entity_identity__year=2019)
        self.groups = [self.group_2018, self.group_2019]
        self.fake_group_repo = get_fake_group_repository(self.groups)
        self.mock_repo("education_group.ddd.repository.group.GroupRepository", self.fake_group_repo)

    def test_should_return_entity_id_of_updated_group(self, mock_end_year_postponement):
        result = update_group_service.update_group(self.cmd)

        expected_result = group.GroupIdentity(code=self.cmd.code, year=self.cmd.year)
        self.assertEqual(expected_result, result)

    def test_should_update_value_of_group_based_on_command_value(self, mock_end_year_postponement):
        entity_id = update_group_service.update_group(self.cmd)

        group_updated = self.fake_group_repo.get(entity_id)
        self.assert_has_same_value_as_update_command(group_updated)

    def test_should_postpone_update(self, mock_end_year_postponement):
        identities = [group.GroupIdentity(code=self.cmd.code, year=year) for year in range(2018, 2021)]

        update_group_service.update_group(self.cmd)

        base_group = self.fake_group_repo.get(identities[0])
        for identity in identities[1:]:
            with self.subTest(year=identity.year):
                postponed_group = self.fake_group_repo.get(identity)
                self.assertTrue(postponed_group.has_same_values_as(base_group))

    def assert_has_same_value_as_update_command(self, update_group: 'group.Group'):
        self.assertEqual(update_group.titles.title_fr, self.cmd.title_fr)
        self.assertEqual(update_group.titles.title_en, self.cmd.title_en)
        self.assertEqual(update_group.credits, self.cmd.credits)
        self.assertEqual(update_group.titles.title_en, self.cmd.title_en)
        self.assertEqual(update_group.content_constraint.type.name, self.cmd.constraint_type)
        self.assertEqual(update_group.content_constraint.maximum, self.cmd.max_constraint)
        self.assertEqual(update_group.content_constraint.minimum, self.cmd.min_constraint)
        self.assertEqual(update_group.management_entity.acronym, self.cmd.management_entity_acronym)
        self.assertEqual(update_group.teaching_campus.name, self.cmd.teaching_campus_name)
        self.assertEqual(update_group.teaching_campus.university_name, self.cmd.organization_name)
        self.assertEqual(update_group.remark.text_fr, self.cmd.remark_fr)
        self.assertEqual(update_group.remark.text_en, self.cmd.remark_en)
        self.assertEqual(update_group.end_year, self.cmd.end_year)
        self.assertEqual(update_group.abbreviated_title, self.cmd.abbreviated_title)
