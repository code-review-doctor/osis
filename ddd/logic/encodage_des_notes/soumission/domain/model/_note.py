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
import abc
from typing import Any

import attr

from base.models.enums.exam_enrollment_justification_type import TutorJustificationTypes, JustificationTypes
from osis_common.ddd import interface

NOTE_MIN = 0
NOTE_MAX = 20
ABSENCE_INJUSTIFIEE = 'A'
ABSENCE_JUSTIFIEE = 'M'
TRICHERIE = 'T'
LETTRES_AUTORISEES = [ABSENCE_INJUSTIFIEE, TRICHERIE]
JUSTIFICATIONS_AUTORISEES = LETTRES_AUTORISEES + TutorJustificationTypes.get_names()


class NoteBuilder:
    @staticmethod
    def build(value: str) -> 'Note':
        if value in LETTRES_AUTORISEES:
            map_to_enum = {
                ABSENCE_INJUSTIFIEE: JustificationTypes.ABSENCE_UNJUSTIFIED,
                TRICHERIE: JustificationTypes.CHEATING,
            }
            return Justification(value=map_to_enum[value])
        if value in JustificationTypes.get_names():
            return Justification(value=JustificationTypes[value])
        if NoteBuilder.__is_float(value):
            return NoteChiffree(value=float(value))
        return NoteManquante()

    @staticmethod
    def __is_float(value) -> bool:
        try:
            float(value)
            return True
        except ValueError:
            return False


@attr.s(slots=True, frozen=True)
class Note(interface.ValueObject, abc.ABC):
    value = attr.ib(type=Any)

    @property
    def is_manquant(self) -> bool:
        return False

    def __str__(self) -> str:
        return str(self.value)


@attr.s(slots=True, frozen=True)
class NoteChiffree(Note):
    value = attr.ib(type=float)

    def __str__(self):
        if self.value:
            return str(self.value)
        return ""


@attr.s(slots=True, frozen=True)
class NoteManquante(Note):
    value = attr.ib(init=False, default='', type=str)

    @property
    def is_manquant(self) -> bool:
        return True

    def __str__(self):
        return ""


@attr.s(slots=True, frozen=True)
class Justification(Note):
    value = attr.ib(type=JustificationTypes)

    def __str__(self) -> str:
        if self.value:
            return {
                JustificationTypes.ABSENCE_UNJUSTIFIED.name: ABSENCE_INJUSTIFIEE,
                JustificationTypes.CHEATING.name: TRICHERIE,
                JustificationTypes.ABSENCE_JUSTIFIED.name: ABSENCE_JUSTIFIEE
            }[self.value.name]
        return ""
