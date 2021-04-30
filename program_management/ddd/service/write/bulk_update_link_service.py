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
from copy import copy
from typing import List, Tuple, Union

from django.db import transaction

from base.ddd.utils.business_validator import MultipleBusinessExceptions
from ddd.logic.shared_kernel.academic_year.builder.academic_year_identity_builder import AcademicYearIdentityBuilder
from education_group.ddd.domain.exception import LinkCopyConsistencyException
from education_group.ddd.domain.service.conflicted_fields import ConflictedFields
from program_management.ddd.business_types import *
from program_management.ddd.command import BulkUpdateLinkCommand, UpdateLinkCommand
from program_management.ddd.domain.exception import BulkUpdateLinkException
from program_management.ddd.domain.program_tree import ProgramTreeIdentity


# TODO :: rename to bulk_update_and_postpone_links
def bulk_update_links(
        cmd: BulkUpdateLinkCommand,
        repository: 'ProgramTreeRepository',
        version_repo: 'ProgramTreeVersionRepository'
) -> List['Link']:
    # GIVEN
    working_tree_id = ProgramTreeIdentity(code=cmd.parent_node_code, year=cmd.parent_node_year)
    trees_through_years = repository.search(code=working_tree_id.code)
    working_tree = next(tree for tree in trees_through_years if tree.entity_id == working_tree_id)

    # WHEN
    links_updated = []  # FIXME :: Used in the view to display success messages... should be refactored because it's not the responsibility of the ApplicationService
    trees_updated = [working_tree]  # Links are updated only in the context of a ProgramTree
    exceptions = dict()
    for update_cmd in cmd.update_link_cmds:  # FIXME :: Bulk update should be a DomainService like BulkUpateLinksOfSameParentNode ?
        try:
            link_before_update = copy(working_tree.get_link_from_identity(update_cmd.link_identity))
            link_updated = working_tree.update_link(update_cmd)
            links_updated.append(link_updated)
            updated_links_in_future, update_trees_in_future = _postpone_link(
                working_tree,
                link_before_update,
                trees_through_years
            )
            links_updated += updated_links_in_future
            trees_updated += update_trees_in_future
        except (MultipleBusinessExceptions, LinkCopyConsistencyException) as e:  # FIXME :: remove LinkCopyConsistencyException and use Report instead
            exceptions[update_cmd] = e
    if exceptions:
        raise BulkUpdateLinkException(exceptions=exceptions)

    # THEN
    for tree in trees_updated:
        repository.update(tree)

    return links_updated


# FIXME :: should be a DomainService ?!
def _postpone_link(
        working_tree: 'ProgramTree',
        link_before_update: 'Link',
        trees_through_years: List['ProgramTree']
) -> Tuple[List['Link'], List['ProgramTree']]:
    updated_links = []
    updated_program_trees = []
    if working_tree.authorized_relationships.is_mandatory_child_type(link_before_update.child.node_type):
        working_year = AcademicYearIdentityBuilder.build_from_year(working_tree.year)
        ordered_trees_in_future = list(
            sorted(
                filter(lambda t: t.year > working_year.year, trees_through_years),
                key=lambda t: t.year
            )
        )  # FIXME :: should be DomainService like SearchTreesInFutureYears? Or Repository.search_trees_in_future_years ? WARNING :: performance !

        conflicted_fields = ConflictedFields.get_conflicted_links(
            link_before_update,
            working_year,
            ordered_trees_in_future
        )

        current_link = link_before_update
        for next_year_tree in ordered_trees_in_future:
            if next_year_tree.year in conflicted_fields:
                break  # Do not copy info from year to N+1 because conflict detected
            cmd = UpdateLinkCommand(
                parent_node_code=current_link.parent.code,
                parent_node_year=next_year_tree.year,
                child_node_code=current_link.child.code,
                child_node_year=next_year_tree.year,
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
            updated_program_trees.append(next_year_tree)
            current_link = next_year_updated_link
        if conflicted_fields:
            first_conflict_year = min(conflicted_fields.keys())
            raise LinkCopyConsistencyException(first_conflict_year, conflicted_fields[first_conflict_year])
    return updated_links, updated_program_trees
