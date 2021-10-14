# ##############################################################################
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
# ##############################################################################
import logging
from typing import List

from django.utils.module_loading import autodiscover_modules

from osis_common.ddd.interface import ApplicationServiceResult, CommandRequest


class AbstractMessageBusCommands:
    command_handlers = {}

    @classmethod
    def get_command_handlers(cls):
        return cls.command_handlers


class MessageBus:
    def __init__(self, command_handlers) -> None:
        super().__init__()
        self.command_handlers = command_handlers

    def invoke(self, command: CommandRequest) -> ApplicationServiceResult:
        return self.command_handlers[command.__class__](command)

    def invoke_multiple(self, commands: List['CommandRequest']) -> List[ApplicationServiceResult]:
        return [self.invoke(command) for command in commands]


def load_message_bus_instance(bus_type):
    # Load `bus_type` python files of installed apps
    autodiscover_modules(bus_type)

    command_handlers = {}
    for kls in AbstractMessageBusCommands.__subclasses__():
        add_handlers = kls.get_command_handlers()

        # Detect command conflicts
        for command in set(command_handlers.keys()) & set(add_handlers.keys()):
            logging.warning("Message bus conflict on command %s", command.__name__)

        command_handlers.update(add_handlers)
    return MessageBus(command_handlers)
