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
from typing import Optional

from program_management.ddd.command import GetProgramTreeVersionCommand
from program_management.ddd.domain import program_tree_version, exception
from program_management.ddd.domain.program_tree_version import ProgramTreeVersion
from program_management.ddd.repositories import program_tree_version as program_tree_version_repository


def get_program_tree_version(cmd: GetProgramTreeVersionCommand) -> Optional['ProgramTreeVersion']:
    identity = program_tree_version.ProgramTreeVersionIdentity(
        offer_acronym=cmd.acronym,
        year=cmd.year,
        version_name=cmd.version_name,
        transition_name=cmd.transition_name
    )

    try:
        return program_tree_version_repository.ProgramTreeVersionRepository().get(entity_id=identity)
    except exception.ProgramTreeVersionNotFoundException:
        return None
