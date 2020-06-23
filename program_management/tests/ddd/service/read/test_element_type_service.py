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
from unittest import mock

from django.test import SimpleTestCase

from base.models.enums.education_group_categories import Categories
from base.models.enums.education_group_types import GroupType, TrainingType, MiniTrainingType
from osis_common.ddd.interface import BusinessExceptions
from program_management.ddd import command
from program_management.ddd.service.read import element_type_service


class TestGetAllowedChildTypes(SimpleTestCase):
    def test_get_allowed_type_with_only_group_category_on_command(self):
        cmd = command.GetAllowedChildTypeCommand(category=Categories.GROUP)

        result = element_type_service.get_allowed_child_types(cmd)
        self.assertIsInstance(result, set)

        self.assertSetEqual(
            result,
            {child_type for child_type in GroupType}
        )

    def test_get_allowed_type_with_only_training_category_on_command(self):
        cmd = command.GetAllowedChildTypeCommand(category=Categories.TRAINING)

        result = element_type_service.get_allowed_child_types(cmd)
        self.assertIsInstance(result, set)

        self.assertSetEqual(
            result,
            {child_type for child_type in TrainingType}
        )

    def test_get_allowed_type_with_only_mini_training_category_on_command(self):
        cmd = command.GetAllowedChildTypeCommand(category=Categories.MINI_TRAINING)

        result = element_type_service.get_allowed_child_types(cmd)
        self.assertIsInstance(result, set)

        self.assertSetEqual(
            result,
            {child_type for child_type in MiniTrainingType}
        )

    @mock.patch('program_management.ddd.service.read.element_type_service.NodeIdentitySearch.get_from_element_id')
    @mock.patch('program_management.ddd.service.read.element_type_service.NodeRepository.get')
    @mock.patch('program_management.ddd.service.read.element_type_service.ProgramTreeRepository.get')
    @mock.patch('program_management.ddd.service.read.element_type_service.PasteAuthorizedRelationshipValidator')
    def test_get_allowed_type_with_path_to_paste_assert_validator_called(
            self,
            mock_validator,
            mock_program_tree_repo,
            mock_node_repo,
            mock_identity_search
    ):
        mock_validator.return_value.validate.side_effect = BusinessExceptions(messages=[])

        cmd = command.GetAllowedChildTypeCommand(category=Categories.GROUP, path_to_paste='4656|5656')

        result = element_type_service.get_allowed_child_types(cmd)
        self.assertIsInstance(result, set)
        self.assertSetEqual(result, set())

        mock_program_tree_repo.assert_called_once()
        mock_node_repo.assert_called_once()
        mock_identity_search.assert_called_once()
