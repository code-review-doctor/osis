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

from program_management.ddd.command import CopyProgramTreeVersionContentFromSourceTreeVersionCommand
from program_management.ddd.domain.program_tree_version import ProgramTreeVersionIdentity, ProgramTreeVersionBuilder
from program_management.ddd.repositories import program_tree_version as tree_version_repository,\
    program_tree as program_tree_repository


def copy_program_tree_version_content_from_source_tree_version(
        cmd: 'CopyProgramTreeVersionContentFromSourceTreeVersionCommand'
):
    repository = tree_version_repository.ProgramTreeVersionRepository()
    tree_repository = program_tree_repository.ProgramTreeRepository()

    source_tree_version = repository.get(
        entity_id=ProgramTreeVersionIdentity(
            offer_acronym=cmd.from_offer_acronym,
            year=cmd.from_year,
            version_name=cmd.from_version_name,
            transition_name=cmd.from_transition_name
        )
    )
    to_tree_version = repository.get(
        entity_id=ProgramTreeVersionIdentity(
            offer_acronym=cmd.to_offer_acronym,
            year=cmd.to_year,
            version_name=cmd.to_version_name,
            transition_name=cmd.to_transition_name
        )
    )

    resulted_tree = ProgramTreeVersionBuilder().copy_content_from_source_to(
        source_tree_version,
        to_tree_version
    )
    # TODO :: add report cms call for mandatory children

    identity = repository.update(resulted_tree)
    tree_repository.update(resulted_tree.get_tree())

    return identity
