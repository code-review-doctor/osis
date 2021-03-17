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

import attr
from django.db import transaction

from education_group.ddd.service.write import create_group_service
from program_management.ddd.command import CreateProgramTreeTransitionVersionCommand, \
    CopyProgramTreePrerequisitesFromProgramTreeCommand, FillProgramTreeTransitionContentFromProgramTreeVersionCommand, \
    CopyTreeCmsFromTree
from program_management.ddd.domain import program_tree
from program_management.ddd.domain.program_tree_version import ProgramTreeVersionIdentity, ProgramTreeVersionBuilder
from program_management.ddd.domain.service import generate_node_code
from program_management.ddd.repositories import program_tree_version as program_tree_version_repository, \
    program_tree as program_tree_repository, node as node_repository
from program_management.ddd.service.write import copy_program_tree_prerequisites_from_program_tree_service, \
    create_and_postpone_tree_transition_version_service, copy_program_tree_cms_from_program_tree_service


@transaction.atomic()
def fill_program_tree_transition_content_from_program_tree_version(
        cmd: 'FillProgramTreeTransitionContentFromProgramTreeVersionCommand'
) -> 'ProgramTreeVersionIdentity':
    tree_version_repository = program_tree_version_repository.ProgramTreeVersionRepository()
    tree_repository = program_tree_repository.ProgramTreeRepository()
    node_repo = node_repository.NodeRepository()

    from_tree_version = tree_version_repository.get(
        entity_id=ProgramTreeVersionIdentity(
            offer_acronym=cmd.from_offer_acronym,
            year=cmd.from_year,
            version_name=cmd.from_version_name,
            transition_name=cmd.from_transition_name
        )
    )
    to_tree_version = tree_version_repository.get(
        entity_id=ProgramTreeVersionIdentity(
            offer_acronym=cmd.to_offer_acronym,
            year=cmd.to_year,
            version_name=cmd.to_version_name,
            transition_name=cmd.to_transition_name
        )
    )

    training_nodes = [
        node for node in from_tree_version.get_tree().root_node.get_all_children_as_nodes() if node.is_training()
    ]
    for training in training_nodes:
        # TODO Should create from to_tree_year
        create_and_postpone_tree_transition_version_service.create_and_postpone_program_tree_transition_version(
            CreateProgramTreeTransitionVersionCommand(
                end_year=to_tree_version.end_year_of_existence,
                offer_acronym=training.title,
                version_name=to_tree_version.version_name,
                start_year=from_tree_version.program_tree_identity.year,
                transition_name=to_tree_version.transition_name,
                title_fr="",
                title_en=""
            )
        )

    transition_tree_versions = tree_version_repository.search(
        version_name=to_tree_version.version_name,
        transition_name=to_tree_version.transition_name,
        year=cmd.to_year
    )
    transition_trees = [tree_version.get_tree() for tree_version in transition_tree_versions]

    existing_trees = tree_repository.search(
        entity_ids=[
            program_tree.ProgramTreeIdentity(code=node.code, year=cmd.to_year)
            for node in from_tree_version.get_tree().root_node.get_all_children_as_nodes().union()
        ]
    )

    existing_learning_unit_nodes = node_repo.search(
        [
            attr.evolve(node.entity_id, year=cmd.to_year)
            for node in from_tree_version.get_tree().root_node.get_all_children_as_learning_unit_nodes()
        ]
    )

    existing_nodes = [tree.root_node for tree in existing_trees] + existing_learning_unit_nodes + [tree.root_node for tree in transition_trees]

    existing_codes = tree_repository.get_all_codes()
    node_code_generator = generate_node_code.BGenerateNodeCode(existing_codes=existing_codes)

    ProgramTreeVersionBuilder().fill_transition_from_program_tree_version(
        from_tree_version,
        to_tree_version,
        set(existing_nodes),
        node_code_generator
    )

    identity = tree_version_repository.update(to_tree_version)
    tree_repository.create(
        to_tree_version.get_tree(),
        create_orphan_group_service=create_group_service.create_orphan_group
    )

    copy_program_tree_prerequisites_from_program_tree_service.copy_program_tree_prerequisites_from_program_tree(
        CopyProgramTreePrerequisitesFromProgramTreeCommand(
            from_code=from_tree_version.program_tree_identity.code,
            from_year=from_tree_version.program_tree_identity.year,
            to_code=to_tree_version.program_tree_identity.code,
            to_year=to_tree_version.program_tree_identity.year
        )
    )

    copy_program_tree_cms_from_program_tree_service.copy_program_tree_cms_from_program_tree(
        CopyTreeCmsFromTree(
            from_code=from_tree_version.program_tree_identity.code,
            from_year=from_tree_version.program_tree_identity.year,
            to_code=to_tree_version.program_tree_identity.code,
            to_year=to_tree_version.program_tree_identity.year
        )
    )

    return identity
