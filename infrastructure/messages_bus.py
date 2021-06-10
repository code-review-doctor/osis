##############################################################################
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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from typing import Dict, Callable, List

from ddd.logic.learning_unit.commands import CreateLearningUnitCommand, GetLearningUnitCommand, \
    CreateEffectiveClassCommand, CanCreateEffectiveClassCommand, GetEffectiveClassCommand
from ddd.logic.learning_unit.use_case.read.check_can_create_class_service import check_can_create_effective_class
from ddd.logic.learning_unit.use_case.read.get_effective_class_service import get_effective_class
from ddd.logic.learning_unit.use_case.read.get_learning_unit_service import get_learning_unit
from ddd.logic.learning_unit.use_case.write.create_effective_class_service import create_effective_class
from ddd.logic.learning_unit.use_case.write.create_learning_unit_service import create_learning_unit
from ddd.logic.shared_kernel.academic_year.commands import SearchAcademicYearCommand
from ddd.logic.shared_kernel.academic_year.use_case.read.search_academic_years_service import search_academic_years
from ddd.logic.shared_kernel.campus.commands import SearchUclouvainCampusesCommand
from ddd.logic.shared_kernel.campus.use_case.read.search_uclouvain_campuses_service import search_uclouvain_campuses
from ddd.logic.shared_kernel.language.commands import SearchLanguagesCommand
from ddd.logic.shared_kernel.language.use_case.read.search_languages_service import search_languages
from infrastructure.learning_unit.repository.effective_class import EffectiveClassRepository
from infrastructure.learning_unit.repository.entity import UclEntityRepository
from infrastructure.learning_unit.repository.learning_unit import LearningUnitRepository
from infrastructure.shared_kernel.academic_year.repository.academic_year import AcademicYearRepository
from infrastructure.shared_kernel.campus.repository.uclouvain_campus import UclouvainCampusRepository
from infrastructure.shared_kernel.language.repository.language import LanguageRepository
from osis_common.ddd.interface import CommandRequest, ApplicationServiceResult
from program_management.ddd.command import BulkUpdateLinkCommand, GetReportCommand
from program_management.ddd.repositories import program_tree as program_tree_repo
from program_management.ddd.repositories.report import ReportRepository
from program_management.ddd.service.read.get_report_service import get_report
from program_management.ddd.service.write.bulk_update_link_service import bulk_update_and_postpone_links


class MessageBus:
    command_handlers = {
        CreateLearningUnitCommand: lambda cmd: create_learning_unit(
            cmd, LearningUnitRepository(), UclEntityRepository()
        ),
        SearchLanguagesCommand: lambda cmd: search_languages(cmd, LanguageRepository()),
        SearchAcademicYearCommand: lambda cmd: search_academic_years(cmd, AcademicYearRepository()),
        GetReportCommand: lambda cmd: get_report(cmd),
        BulkUpdateLinkCommand: lambda cmd: bulk_update_and_postpone_links(
            cmd, program_tree_repo.ProgramTreeRepository(), ReportRepository()
        ),
        GetLearningUnitCommand: lambda cmd: get_learning_unit(cmd, LearningUnitRepository()),
        CreateEffectiveClassCommand: lambda cmd: create_effective_class(
            cmd, LearningUnitRepository(), EffectiveClassRepository()
        ),
        CanCreateEffectiveClassCommand: lambda cmd: check_can_create_effective_class(cmd, LearningUnitRepository()),
        SearchUclouvainCampusesCommand: lambda cmd: search_uclouvain_campuses(cmd, UclouvainCampusRepository()),
        GetEffectiveClassCommand: lambda cmd: get_effective_class(cmd, EffectiveClassRepository()),
    }  # type: Dict[CommandRequest, Callable[[CommandRequest], ApplicationServiceResult]]

    def invoke(self, command: CommandRequest) -> ApplicationServiceResult:
        return self.command_handlers[command.__class__](command)

    def invoke_multiple(self, commands: List['CommandRequest']) -> List[ApplicationServiceResult]:
        return [self.invoke(command) for command in commands]


message_bus_instance = MessageBus()
