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

from base.models.enums.exam_enrollment_justification_type import TutorJustificationTypes
from osis_common.ddd import interface

NOTE_MIN = 0
NOTE_MAX = 20
ABSENCE_INJUSTIFIEE = 'A'
TRICHERIE = 'T'
LETTRES_AUTORISEES = [ABSENCE_INJUSTIFIEE, TRICHERIE]


class NoteBuilder:
    @staticmethod
    def build(value: str) -> 'Note':
        if value in LETTRES_AUTORISEES:
            map_to_enum = {
                ABSENCE_INJUSTIFIEE: TutorJustificationTypes.ABSENCE_UNJUSTIFIED,
                TRICHERIE: TutorJustificationTypes.CHEATING,
            }
            return Justification(value=map_to_enum[value])
        if value in TutorJustificationTypes.get_names():
            return Justification(value=TutorJustificationTypes[value])
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


@attr.s(slots=True, frozen=True)
class NoteChiffree(Note):
    value = attr.ib(type=float)


@attr.s(slots=True, frozen=True)
class NoteManquante(Note):
    value = attr.ib(init=False, default='', type=str)


@attr.s(slots=True, frozen=True)
class Justification(Note):
    value = attr.ib(type=TutorJustificationTypes)
