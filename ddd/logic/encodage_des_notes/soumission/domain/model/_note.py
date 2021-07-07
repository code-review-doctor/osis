import abc
from typing import Any

import attr

from osis_common.ddd import interface


class Note(interface.ValueObject, abc.ABC):
    value = attr.ib(type=Any)


class NoteChiffree(Note):
    value = attr.ib(type=int)


class NoteManquante(Note):
    value = ""


class Justification(Note):
    value = attr.ib(type=str)  # TODO : remplacer avec Enum (sans "absence justifiée")
