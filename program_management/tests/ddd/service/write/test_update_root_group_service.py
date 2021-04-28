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
import mock
from django.test import TestCase

from ddd.logic.shared_kernel.academic_year.builder.academic_year_identity_builder import AcademicYearIdentityBuilder
from ddd.logic.shared_kernel.academic_year.domain.model.academic_year import AcademicYear
from education_group.ddd.factories.group import GroupFactory
from education_group.ddd.repository.group import GroupRepository
from education_group.tests.ddd.factories.group import GroupIdentityFactory
from infrastructure.shared_kernel.academic_year.repository.academic_year import AcademicYearRepository
from program_management.ddd.domain.program_tree_version import ProgramTreeVersionIdentity
from program_management.ddd.service.write import update_and_postpone_root_group_service
from program_management.tests.ddd.factories.commands.update_root_group_command import UpdateRootGroupCommandFactory


class TestUpdateRootGroup(TestCase):

    def setUp(self):
        self.cmd = UpdateRootGroupCommandFactory()
        self.identity_expected = ProgramTreeVersionIdentity(
            offer_acronym=self.cmd.offer_acronym,
            year=self.cmd.year,
            version_name=self.cmd.version_name,
            transition_name=self.cmd.transition_name,
        )
        self.mock_anac_repository = mock.create_autospec(AcademicYearRepository)
        current_anac = AcademicYear(
            entity_id=AcademicYearIdentityBuilder.build_from_year(year=self.cmd.year - 1),
            start_date=None,
            end_date=None
        )
        self.mock_anac_repository.get_current.return_value = current_anac

        self.mock_group_repository = mock.create_autospec(GroupRepository)
        self.mock_group_repository.get.return_value = GroupFactory()

    @mock.patch(
        "program_management.ddd.service.write.postpone_tree_specific_version_service.postpone_program_tree_version")
    @mock.patch("program_management.ddd.service.write.postpone_program_tree_service.postpone_program_tree")
    @mock.patch(
        "program_management.ddd.domain.service.identity_search.GroupIdentitySearch.get_from_tree_version_identity")
    @mock.patch("program_management.ddd.service.write.update_program_tree_version_service.update_program_tree_version")
    @mock.patch("program_management.ddd.service.write.update_and_postpone_group_version_service."
                "update_and_postpone_group_version")
    def test_should_call_update_group_service_and_update_tree_version_service(
            self,
            mock_postpone_group_version_service,
            mock_update_tree_version_service,
            mock_identity_converter,
            mock_postpone_program_tree,
            mock_postpone_program_tree_version,
    ):
        mock_update_tree_version_service.return_value = self.identity_expected
        mock_identity_converter.return_value = GroupIdentityFactory()
        mock_postpone_group_version_service.return_value = []

        result = update_and_postpone_root_group_service.update_and_postpone_root_group(
            self.cmd,
            self.mock_anac_repository,
            self.mock_group_repository
        )

        self.assertTrue(mock_postpone_group_version_service.called)
        self.assertTrue(mock_update_tree_version_service.called)
        self.assertTrue(mock_postpone_program_tree.called)
        self.assertTrue(mock_postpone_program_tree_version.called)

        self.assertEqual(result, [self.identity_expected])

    @mock.patch("education_group.ddd.service.write.update_group_service.update_group")
    @mock.patch(
        "program_management.ddd.service.write.postpone_tree_specific_version_service.postpone_program_tree_version")
    @mock.patch("program_management.ddd.service.write.postpone_program_tree_service.postpone_program_tree")
    @mock.patch(
        "program_management.ddd.domain.service.identity_search.GroupIdentitySearch.get_from_tree_version_identity")
    @mock.patch("program_management.ddd.service.write.update_program_tree_version_service.update_program_tree_version")
    @mock.patch("program_management.ddd.service.write.update_and_postpone_group_version_service."
                "update_and_postpone_group_version")
    def test_should_not_call_postponement_service_if_in_past(
            self,
            mock_postpone_group_version_service,
            mock_update_tree_version_service,
            mock_identity_converter,
            mock_postpone_program_tree,
            mock_postpone_program_tree_version,
            mock_update_group,
    ):
        current_anac = AcademicYear(
            entity_id=AcademicYearIdentityBuilder.build_from_year(year=self.cmd.year + 1),
            start_date=None,
            end_date=None
        )
        self.mock_anac_repository.get_current.return_value = current_anac
        mock_update_tree_version_service.return_value = self.identity_expected
        mock_identity_converter.return_value = GroupIdentityFactory()
        mock_postpone_group_version_service.return_value = []

        result = update_and_postpone_root_group_service.update_and_postpone_root_group(
            self.cmd,
            self.mock_anac_repository,
            self.mock_group_repository
        )

        self.assertFalse(mock_postpone_group_version_service.called)
        self.assertFalse(mock_postpone_program_tree.called)
        self.assertFalse(mock_postpone_program_tree_version.called)

        self.assertTrue(mock_update_tree_version_service.called)
        self.assertTrue(mock_update_group.called)

        self.assertEqual(result, [self.identity_expected])

    @mock.patch(
        "program_management.ddd.service.write.postpone_tree_specific_version_service.postpone_program_tree_version")
    @mock.patch("program_management.ddd.service.write.postpone_program_tree_service.postpone_program_tree")
    @mock.patch(
        "program_management.ddd.domain.service.identity_search.GroupIdentitySearch.get_from_tree_version_identity")
    @mock.patch("program_management.ddd.service.write.update_program_tree_version_service.update_program_tree_version")
    @mock.patch("program_management.ddd.service.write.update_and_postpone_group_version_service."
                "update_and_postpone_group_version")
    def test_should_call_postponement_service_if_in_past_but_is_extended(
            self,
            mock_postpone_group_version_service,
            mock_update_tree_version_service,
            mock_identity_converter,
            mock_postpone_program_tree,
            mock_postpone_program_tree_version,
    ):
        current_anac = AcademicYear(
            entity_id=AcademicYearIdentityBuilder.build_from_year(year=self.cmd.year + 1),
            start_date=None,
            end_date=None
        )
        self.mock_anac_repository.get_current.return_value = current_anac
        mock_update_tree_version_service.return_value = self.identity_expected
        mock_identity_converter.return_value = GroupIdentityFactory()
        mock_postpone_group_version_service.return_value = []
        self.mock_group_repository.get.return_value = GroupFactory(end_year=2020)

        result = update_and_postpone_root_group_service.update_and_postpone_root_group(
            self.cmd,
            self.mock_anac_repository,
            self.mock_group_repository
        )

        self.assertTrue(mock_postpone_group_version_service.called)
        self.assertTrue(mock_postpone_program_tree.called)
        self.assertTrue(mock_postpone_program_tree_version.called)

        self.assertTrue(mock_update_tree_version_service.called)

        self.assertEqual(result, [self.identity_expected])
