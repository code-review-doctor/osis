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

from django.db import transaction

from education_group.ddd.business_types import *
from education_group.ddd.command import PostponeGroupModificationCommand
from education_group.ddd.domain.exception import GroupCopyConsistencyException
from education_group.ddd.service.write import postpone_orphan_group_modification_service
from program_management.ddd.business_types import *
from program_management.ddd.command import UpdateProgramTreeVersionCommand, UpdateMiniTrainingVersionCommand, \
    PostponeProgramTreeVersionCommand
from program_management.ddd.domain.service.identity_search import GroupIdentitySearch
from program_management.ddd.service.write import update_program_tree_version_service, postpone_tree_version_service


@transaction.atomic
def update_and_postpone_mini_training_version(
        command: 'UpdateMiniTrainingVersionCommand',
) -> List['ProgramTreeVersionIdentity']:
    tree_version_identity = update_program_tree_version_service.update_program_tree_version(
        __convert_to_update_tree_version_command(command)
    )
    group_identity = GroupIdentitySearch().get_from_tree_version_identity(tree_version_identity)

    exception_raised = None
    try:
        postpone_orphan_group_modification_service.postpone_orphan_group_modification_service(
            __convert_to_postpone_group_modification_command(command, group_identity)
        )
    except GroupCopyConsistencyException as e:
        exception_raised = e

    postponed_tree_version_identities = postpone_tree_version_service.postpone_program_tree_version(
        __convert_to_postpone_program_tree_version(command, group_identity)
    )

    if exception_raised:
        raise exception_raised

    return [tree_version_identity] + postponed_tree_version_identities


def __convert_to_postpone_group_modification_command(
        cmd: 'UpdateMiniTrainingVersionCommand',
        group_identity: 'GroupIdentity'
) -> 'PostponeGroupModificationCommand':
    return PostponeGroupModificationCommand(
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
    )


def __convert_to_update_tree_version_command(command: 'UpdateMiniTrainingVersionCommand'):
    return UpdateProgramTreeVersionCommand(
        end_year=command.end_year,
        offer_acronym=command.offer_acronym,
        version_name=command.version_name,
        year=command.year,
        is_transition=command.is_transition,
        title_en=command.title_en,
        title_fr=command.title_fr,
    )


def __convert_to_postpone_program_tree_version(
        cmd: 'UpdateMiniTrainingVersionCommand',
        group_identity: 'GroupIdentity'
) -> 'PostponeProgramTreeVersionCommand':

    return PostponeProgramTreeVersionCommand(
        from_offer_acronym=cmd.offer_acronym,
        from_version_name=cmd.version_name,
        from_year=cmd.year,
        from_is_transition=cmd.is_transition,
        from_code=group_identity.code
    )
