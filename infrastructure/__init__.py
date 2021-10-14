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
