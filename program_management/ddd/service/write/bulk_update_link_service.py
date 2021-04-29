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

from education_group.ddd.domain.exception import LinkCopyConsistencyException
from education_group.ddd.domain.service.conflicted_fields import ConflictedFields
from program_management.ddd.command import BulkUpdateLinkCommand, UpdateLinkCommand
from program_management.ddd.business_types import *
from base.ddd.utils.business_validator import MultipleBusinessExceptions
from program_management.ddd.domain.exception import BulkUpdateLinkException
from program_management.ddd.domain.program_tree import ProgramTreeIdentity
from program_management.ddd.domain.service.calculate_end_postponement import CalculateEndPostponement
from program_management.ddd.repositories import load_authorized_relationship


# TODO :: rename to bulk_update_and_postpone_links
@transaction.atomic()
def bulk_update_links(
        cmd: BulkUpdateLinkCommand,
        repository: 'ProgramTreeRepository',
        version_repo: 'ProgramTreeVersionRepository'
) -> List['Link']:
    # GIVEN
    tree_id = ProgramTreeIdentity(code=cmd.parent_node_code, year=cmd.parent_node_year)
    trees_through_years = repository.search(code=tree_id.code)
    current_tree = next(tree for tree in trees_through_years if tree.entity_id == tree_id)
    trees_in_future = [current_tree] + list(filter(lambda t: t.year >= tree_id.year, trees_through_years))  # FIXME :: DomainService ?
    links_to_update = [current_tree.get_link_from_identity(cmd.link_identity) for cmd in cmd.update_link_cmds]
    authorized_relationships = load_authorized_relationship.load()
    conflicted_fields = ConflictedFields.get_conflicted_links(links_to_update, tree_id, trees_in_future)
    end_postponement_year = CalculateEndPostponement.calculate_end_postponement_year_program_tree(
        tree_id,
        version_repo
    )

    # WHEN
    links_updated = []
    exceptions = dict()
    for update_cmd in cmd.update_link_cmds:
        try:
            link_updated = current_tree.update_link(update_cmd)
            links_updated.append(link_updated)
            if authorized_relationships.is_mandatory_child_type(link_updated.child.node_type):
                _postpone_link(trees_in_future, link_updated, conflicted_fields, end_postponement_year)
        except (MultipleBusinessExceptions, LinkCopyConsistencyException) as e:
            exceptions[update_cmd] = e
    if exceptions:
        raise BulkUpdateLinkException(exceptions=exceptions)

    # THEN
    for tree in trees_through_years:
        repository.update(tree)

    return links_updated


# FIXME :: should be a DomainService ?!
def _postpone_link(
        trees_through_years: List['ProgramTree'],
        current_link: 'Link',
        conflicted_fields,
        end_postponement_year
) -> List['Link']:
    updated_links = []
    for next_year in range(current_link.parent.year + 1, end_postponement_year):
        if next_year + 1 in conflicted_fields:
            break  # Do not copy info from year to N+1 because conflict detected
        next_year_tree = next(tree for tree in trees_through_years if tree.year == next_year)
        cmd = UpdateLinkCommand(
            parent_node_code=current_link.parent.code,
            parent_node_year=next_year,
            child_node_code=current_link.child.code,
            child_node_year=next_year,
            access_condition=current_link.access_condition,
            is_mandatory=current_link.is_mandatory,
            block=current_link.block,
            link_type=current_link.link_type,
            comment=current_link.comment,
            comment_english=current_link.comment_english,
            relative_credits=current_link.relative_credits,
        )
        next_year_updated_link = next_year_tree.update_link(cmd)
        updated_links.append(next_year_updated_link)
        current_link = next_year_updated_link
    if conflicted_fields:
        first_conflict_year = min(conflicted_fields.keys())
        raise LinkCopyConsistencyException(first_conflict_year, conflicted_fields[first_conflict_year])
    return updated_links
