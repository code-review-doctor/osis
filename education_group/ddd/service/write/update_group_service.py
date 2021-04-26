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
from typing import List

from django.db import transaction

from base.models.enums.constraint_type import ConstraintTypeEnum
from education_group.ddd import command
from education_group.ddd.domain._campus import Campus
from education_group.ddd.domain._content_constraint import ContentConstraint
from education_group.ddd.domain._entity import Entity
from education_group.ddd.domain._remark import Remark
from education_group.ddd.domain._titles import Titles
from education_group.ddd.domain.exception import GroupCopyConsistencyException
from education_group.ddd.domain.group import GroupIdentity, Group
from education_group.ddd.domain.service.conflicted_fields import ConflictedFields
from education_group.ddd.repository import group as group_repository
from education_group.ddd.service.write import copy_group_service
from program_management.ddd.domain.service.calculate_end_postponement import CalculateEndPostponement
from program_management.ddd.repositories import load_authorized_relationship


# DO NOT SET @transaction.atomic() because it breaks the update in case of GroupCopyConsistencyException
def update_group(cmd: command.UpdateGroupCommand) -> List['GroupIdentity']:

    # GIVEN
    group_identity = GroupIdentity(code=cmd.code, year=cmd.year)
    grp = group_repository.GroupRepository.get(group_identity)
    authorized_relationships = load_authorized_relationship.load()
    conflicted_fields = ConflictedFields.get_group_conflicted_fields(grp.entity_id)

    # WHEN
    grp = _update_group(grp, cmd)

    # THEN
    group_repository.GroupRepository.update(grp)
    updated_identities = [grp.entity_id]

    if authorized_relationships.is_mandatory_child_type(grp.type):
        # means that this group has been automatically created by the system
        # behind 'trainings' and 'minitrainings' Nodes/groups in ProgramTree
        updated_identities = _postpone_group(grp, conflicted_fields)

    return updated_identities


# FIXME :: should be a DomainService ?!
def _postpone_group(grp, conflicted_fields) -> List['GroupIdentity']:
    identities = []
    end_postponement_year = CalculateEndPostponement.calculate_end_postponement_year_for_orphan_group(group=grp)
    for year in range(grp.year, end_postponement_year):
        if year + 1 in conflicted_fields:
            break  # Do not copy info from year to N+1 because conflict detected
        identity_next_year = copy_group_service.copy_group(
            cmd=command.CopyGroupCommand(
                from_code=grp.code,
                from_year=year
            )
        )
        identities.append(identity_next_year)
    if conflicted_fields:
        first_conflict_year = min(conflicted_fields.keys())
        raise GroupCopyConsistencyException(first_conflict_year, conflicted_fields[first_conflict_year])
    return identities


def _update_group(group_obj: 'Group', cmd: command.UpdateGroupCommand) -> 'Group':
    group_obj.update(
        abbreviated_title=cmd.abbreviated_title,
        titles=Titles(title_fr=cmd.title_fr, title_en=cmd.title_en),
        credits=cmd.credits,
        content_constraint=ContentConstraint(
            type=ConstraintTypeEnum[cmd.constraint_type] if cmd.constraint_type else None,
            minimum=cmd.min_constraint,
            maximum=cmd.max_constraint
        ),
        management_entity=Entity(acronym=cmd.management_entity_acronym),
        teaching_campus=Campus(
            name=cmd.teaching_campus_name,
            university_name=cmd.organization_name
        ),
        remark=Remark(text_fr=cmd.remark_fr, text_en=cmd.remark_en),
        end_year=cmd.end_year
    )
    return group_obj
