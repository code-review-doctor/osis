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
from django.utils.translation import gettext_lazy as _

from ddd.logic.encodage_des_notes.encodage.domain.model.note_etudiant import IdentiteNoteEtudiant
from osis_common.ddd.interface import BusinessException


class PasGestionnaireParcoursExceptionException(BusinessException):
    def __init__(self, **kwargs):
        message = _("You're not a program manager (no assigned formations found)")
        super().__init__(message, **kwargs)


class NoteIncorrecteException(BusinessException):
    def __init__(self, note_incorrecte: str, **kwargs):
        message = _(
            "{note} isn't a valid score. Valid scores : 0 - 20 "
            "(0=Score of presence), A=Absent, T=Cheating, M=Absence justified"
        ).format(note=note_incorrecte)
        super().__init__(message, **kwargs)


class EncoderNotesEnLotLigneBusinessExceptions(BusinessException):
    def __init__(self, note_id: IdentiteNoteEtudiant, exception: BusinessException):
        self.note_id = note_id
        super().__init__(exception.message)
