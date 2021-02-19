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

from program_management.ddd.command import GetStandardProgramTreeVersionFromTransitionVersionCommand
from program_management.ddd.domain.program_tree_version import ProgramTreeVersion
from program_management.ddd.repositories import program_tree_version as tree_version_repository


def get_standard_program_tree_version_from_transition_version(
        cmd: 'GetStandardProgramTreeVersionFromTransitionVersionCommand'
) -> Optional['ProgramTreeVersion']:
    result = tree_version_repository.ProgramTreeVersionRepository().search(
        offer_acronym=cmd.offer_acronym,
        year=cmd.year,
    )
    return result[0] if result else None
