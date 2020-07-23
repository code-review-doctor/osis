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
from education_group.ddd.service.write import create_orphan_mini_training_service
from program_management.ddd import command as command_program_mangement
from education_group.ddd import command as command_education_group
from education_group.ddd.domain.mini_training import MiniTrainingIdentity
from program_management.ddd.service.write import paste_element_service


def create_mini_training_and_paste(
        cmd: command_program_mangement.CreateMiniTrainingAndPasteCommand) -> 'MiniTrainingIdentity':
    cmd_create = _get_create_orphan_mini_training_command_from_create_mini_training_and_attach_command(cmd)
    mini_training_identity = create_orphan_mini_training_service.create_and_postpone_orphan_mini_training(cmd_create)

    cmd_paste = _get_paste_element_command_from_create_mini_training_and_paste_command(cmd)
    paste_element_service.paste_element(cmd_paste)
    return mini_training_identity


def _get_create_orphan_mini_training_command_from_create_mini_training_and_attach_command(
        cmd: command_program_mangement.CreateMiniTrainingAndPasteCommand
) -> command_education_group.CreateMiniTrainingCommand:
    return command_education_group.CreateMiniTrainingCommand(
        code=cmd.code,
        year=cmd.year,
        type=cmd.type,
        abbreviated_title=cmd.abbreviated_title,
        title_fr=cmd.title_fr,
        title_en=cmd.title_en,
        status=cmd.status,
        schedule_type=cmd.schedule_type,
        credits=cmd.credits,
        constraint_type=cmd.constraint_type,
        min_constraint=cmd.min_constraint,
        max_constraint=cmd.max_constraint,
        management_entity_acronym=cmd.management_entity_acronym,
        teaching_campus_name=cmd.teaching_campus_name,
        organization_name=cmd.organization_name,
        remark_fr=cmd.remark_fr,
        remark_en=cmd.remark_en,
        start_year=cmd.start_year,
        end_year=cmd.end_year
    )


def _get_paste_element_command_from_create_mini_training_and_paste_command(
        cmd: command_program_mangement.CreateMiniTrainingAndPasteCommand
) -> command_program_mangement.PasteElementCommand:
    return command_program_mangement.PasteElementCommand(
        node_to_paste_code=cmd.code,
        node_to_paste_year=cmd.year,
        path_where_to_paste=cmd.path_to_paste
    )
