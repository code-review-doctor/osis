##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)
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
from typing import List

from ddd.logic.shared_kernel.academic_year.repository.i_academic_year import IAcademicYearRepository
from education_group.ddd.business_types import *
from education_group.ddd.command import UpdateGroupCommand
from education_group.ddd.repository.group import GroupRepository
from education_group.ddd.service.write import update_group_service
from program_management.ddd.command import UpdateRootGroupCommand, UpdateProgramTreeVersionCommand, \
    PostponeGroupVersionCommand, PostponeProgramTreeCommand, PostponeProgramTreeVersionCommand
from program_management.ddd.domain.program_tree_version import ProgramTreeVersionIdentity
from program_management.ddd.domain.service.identity_search import GroupIdentitySearch
from program_management.ddd.domain.service.is_academic_year_in_past import IsAcademicYearInPast
from program_management.ddd.service.write import update_program_tree_version_service, \
    update_and_postpone_group_version_service, postpone_program_tree_service, postpone_tree_specific_version_service


def update_and_postpone_root_group(
        command: 'UpdateRootGroupCommand',
        academic_year_repository: 'IAcademicYearRepository',
        group_repository: 'GroupRepository'
) -> List['ProgramTreeVersionIdentity']:
    is_in_past = IsAcademicYearInPast().is_in_past(command.year, academic_year_repository)
    tree_version_identity = ProgramTreeVersionIdentity(
        version_name=command.version_name,
        transition_name=command.transition_name,
        year=command.year,
        offer_acronym=command.offer_acronym
    )
    group_identity = GroupIdentitySearch().get_from_tree_version_identity(tree_version_identity)
    group = group_repository.get(group_identity)
    has_end_year_changed = group.end_year != command.end_year

    # FIXME: Service appelé uniquement pour remplir les champs EducationGroupVersion du groupement racine
    update_program_tree_version_service.update_program_tree_version(
        __convert_to_update_tree_version_command(command)
    )
    postpone_cmd = __convert_to_postpone_group_version(command, group_identity)
    postponed_tree_version_identities = []

    if not is_in_past or has_end_year_changed:
        postponed_tree_version_identities = update_and_postpone_group_version_service.update_and_postpone_group_version(
            postpone_cmd
        )

        postpone_program_tree_service.postpone_program_tree(
            PostponeProgramTreeCommand(
                from_code=group_identity.code,
                from_year=group_identity.year,
                offer_acronym=command.offer_acronym
            )
        )

        postpone_tree_specific_version_service.postpone_program_tree_version(
            PostponeProgramTreeVersionCommand(
                from_offer_acronym=command.offer_acronym,
                from_version_name=command.version_name,
                from_year=command.year,
                from_transition_name=command.transition_name,
            )
        )
    else:
        update_group_service.update_group(__convert_to_update_group_command(postpone_cmd))

    return [tree_version_identity] + postponed_tree_version_identities


def __convert_to_update_group_command(postpone_cmd: 'PostponeGroupVersionCommand') -> 'UpdateGroupCommand':
    return UpdateGroupCommand(
        code=postpone_cmd.code,
        year=postpone_cmd.postpone_from_year,
        abbreviated_title=postpone_cmd.abbreviated_title,
        title_fr=postpone_cmd.title_fr,
        title_en=postpone_cmd.title_en,
        credits=postpone_cmd.credits,
        constraint_type=postpone_cmd.constraint_type,
        min_constraint=postpone_cmd.min_constraint,
        max_constraint=postpone_cmd.max_constraint,
        management_entity_acronym=postpone_cmd.management_entity_acronym,
        teaching_campus_name=postpone_cmd.teaching_campus_name,
        organization_name=postpone_cmd.organization_name,
        remark_fr=postpone_cmd.remark_fr,
        remark_en=postpone_cmd.remark_en,
        end_year=postpone_cmd.end_year,
    )


def __convert_to_update_tree_version_command(command: 'UpdateRootGroupCommand'):
    return UpdateProgramTreeVersionCommand(
        end_year=command.end_year,
        offer_acronym=command.offer_acronym,
        version_name=command.version_name,
        year=command.year,
        transition_name=command.transition_name,
        title_en=command.title_en,
        title_fr=command.title_fr,
    )


def __convert_to_postpone_group_version(
        cmd: 'UpdateRootGroupCommand',
        group_identity: 'GroupIdentity'
) -> 'PostponeGroupVersionCommand':
    return PostponeGroupVersionCommand(
        code=group_identity.code,
        postpone_from_year=cmd.year,
        abbreviated_title=cmd.offer_acronym,
        title_fr=cmd.title_fr,
        title_en=cmd.title_en,
        credits=cmd.credits,
        constraint_type=cmd.constraint_type,
        min_constraint=cmd.min_constraint,
        max_constraint=cmd.max_constraint,
        management_entity_acronym=cmd.management_entity_acronym,
        teaching_campus_name=cmd.teaching_campus_name,
        organization_name=cmd.teaching_campus_organization_name,
        remark_fr=cmd.remark_fr,
        remark_en=cmd.remark_en,
        end_year=cmd.end_year,
        from_offer_acronym=cmd.offer_acronym,
        from_version_name=cmd.version_name,
        from_transition_name=cmd.transition_name,
    )
