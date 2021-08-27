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

from ddd.logic.admission.preparation.projet_doctoral.commands import (
    SearchDoctoratCommand, CompleterPropositionCommand,
    InitierPropositionCommand, IdentifierPromoteurCommand, IdentifierMembreCACommand,
)
from ddd.logic.admission.preparation.projet_doctoral.use_case.read.rechercher_doctorats_service import \
    rechercher_doctorats
from ddd.logic.admission.preparation.projet_doctoral.use_case.write.completer_proposition_service import \
    completer_proposition
from ddd.logic.admission.preparation.projet_doctoral.use_case.write.identifier_membre_CA_service import \
    identifier_membre_CA
from ddd.logic.admission.preparation.projet_doctoral.use_case.write.identifier_promoteur_service import \
    identifier_promoteur
from ddd.logic.admission.preparation.projet_doctoral.use_case.write.initier_proposition_service import \
    initier_proposition
from infrastructure.admission.preparation.projet_doctoral.domain.service.in_memory.doctorat import \
    DoctoratInMemoryTranslator
from infrastructure.admission.preparation.projet_doctoral.domain.service.in_memory.membre_CA import \
    MembreCAInMemoryTranslator
from infrastructure.admission.preparation.projet_doctoral.domain.service.in_memory.promoteur import \
    PromoteurInMemoryTranslator
from infrastructure.admission.preparation.projet_doctoral.repository.in_memory.groupe_de_supervision import \
    GroupeDeSupervisionInMemoryRepository
from infrastructure.admission.preparation.projet_doctoral.repository.in_memory.proposition import \
    PropositionInMemoryRepository
from osis_common.ddd.interface import CommandRequest, ApplicationServiceResult


class MessageBusInMemory:
    command_handlers = {
        InitierPropositionCommand: lambda cmd: initier_proposition(
            cmd,
            PropositionInMemoryRepository(),
            DoctoratInMemoryTranslator(),
        ),
        SearchDoctoratCommand: lambda cmd: rechercher_doctorats(
            cmd,
            DoctoratInMemoryTranslator(),
        ),
        CompleterPropositionCommand: lambda cmd: completer_proposition(
            cmd,
            PropositionInMemoryRepository(),
            DoctoratInMemoryTranslator(),
        ),
        IdentifierPromoteurCommand: lambda cmd: identifier_promoteur(
            cmd,
            PropositionInMemoryRepository(),
            GroupeDeSupervisionInMemoryRepository(),
            PromoteurInMemoryTranslator(),
        ),
        IdentifierMembreCACommand: lambda cmd: identifier_membre_CA(
            cmd,
            PropositionInMemoryRepository(),
            GroupeDeSupervisionInMemoryRepository(),
            MembreCAInMemoryTranslator(),
        ),
    }  # type: Dict[CommandRequest, Callable[[CommandRequest], ApplicationServiceResult]]

    def invoke(self, command: CommandRequest) -> ApplicationServiceResult:
        return self.command_handlers[command.__class__](command)

    def invoke_multiple(self, commands: List['CommandRequest']) -> List[ApplicationServiceResult]:
        return [self.invoke(command) for command in commands]


message_bus_in_memory_instance = MessageBusInMemory()
