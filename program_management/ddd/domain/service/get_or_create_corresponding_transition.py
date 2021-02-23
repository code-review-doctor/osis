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
from program_management.ddd.command import CreateProgramTreeTransitionVersionCommand
from program_management.ddd.domain import exception
from program_management.ddd.domain import program_tree_version, node
from program_management.ddd.repositories import node as node_repository, program_tree_version as tree_version_repository
from program_management.ddd.service.write.create_program_tree_transition_version_service import \
    create_program_tree_transition_version


def get_or_create_transition_node(offer_acronym, year, version_name, transition_name, end_year):
    identity = program_tree_version.ProgramTreeVersionIdentity(
        offer_acronym=offer_acronym,
        year=year,
        version_name=version_name,
        transition_name=transition_name
    )
    try:
        tree_version = tree_version_repository.ProgramTreeVersionRepository().get(identity)
        return node_repository.NodeRepository().get(
            node.NodeIdentity(code=tree_version.program_tree_identity.code, year=year)
        )
    except exception.ProgramTreeVersionNotFoundException:
        cmd = CreateProgramTreeTransitionVersionCommand(
            end_year=end_year,
            offer_acronym=offer_acronym,
            version_name=version_name,
            start_year=year,
            transition_name=transition_name,
            title_en="",
            title_fr=""
        )
        create_program_tree_transition_version(cmd)
        tree_version = tree_version_repository.ProgramTreeVersionRepository().get(identity)
        return node_repository.NodeRepository().get(
            node.NodeIdentity(code=tree_version.program_tree_identity.code, year=year)
        )
