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
from django.db import transaction

from program_management.ddd.command import CopyTreeVersionFromPastYearCommand, \
    CopyProgramTreeVersionContentFromSourceTreeVersionCommand
from program_management.ddd.domain.program_tree_version import ProgramTreeVersionIdentity
from program_management.ddd.service.write.copy_program_tree_version_content_from_source_tree_version_service import \
    fill_program_tree_version_content_from_source


@transaction.atomic()
def copy_tree_version_from_past_year(copy_cmd: CopyTreeVersionFromPastYearCommand) -> 'ProgramTreeVersionIdentity':
    return fill_program_tree_version_content_from_source(
        CopyProgramTreeVersionContentFromSourceTreeVersionCommand(
            from_year=copy_cmd.to_year-1,
            from_offer_acronym=copy_cmd.to_offer_acronym,
            from_version_name=copy_cmd.to_version_name,
            from_transition_name=copy_cmd.to_transition_name,
            to_year=copy_cmd.to_year,
            to_offer_acronym=copy_cmd.to_offer_acronym,
            to_version_name=copy_cmd.to_version_name,
            to_transition_name=copy_cmd.to_transition_name
        )
    )

