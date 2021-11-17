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
from typing import Set

from django.utils.translation import gettext_lazy as _

from ddd.logic.encodage_des_notes.encodage.domain.model.note_etudiant import IdentiteNoteEtudiant
from osis_common.ddd.interface import BusinessException


class EnseignantNonAttribueUniteEnseignementException(BusinessException):
    def __init__(self, code_unite_enseignement: str, **kwargs):
        message = _("You're not attributed to the learning unit {}").format(code_unite_enseignement)
        super().__init__(message, **kwargs)


class AucunEtudiantTrouveException(BusinessException):
    def __init__(self, learning_unit_code: str, **kwargs):
        message = _("The enrollment to the learning unit {learning_unit_code} doesn't exist").format(
            learning_unit_code=learning_unit_code,
        )
        super().__init__(message, **kwargs)


class NoteIncorrecteException(BusinessException):
    def __init__(self, note_incorrecte: str, **kwargs):
        message = _(
            "{note} isn't a valid score. Valid scores : 0 - 20 (0=Score of presence), A=Absent, T=Cheating"
        ).format(note=note_incorrecte)
        super().__init__(message, **kwargs)


class NoteDejaSoumiseException(BusinessException):
    def __init__(self, **kwargs):
        message = _("Score already submitted")
        super().__init__(message, **kwargs)


class PasResponsableDeNotesException(BusinessException):
    def __init__(self, code_unite_enseignement: str, **kwargs):
        message = _("You must be score responsible of {code_unite_enseignement} to submit the scores").format(
            code_unite_enseignement=code_unite_enseignement
        )
        super().__init__(message, **kwargs)


class PasGestionnaireParcoursException(BusinessException):
    def __init__(self, **kwargs):
        message = _("You're not a program manager (no assigned formations found)")
        super().__init__(message, **kwargs)


class PasGestionnaireParcoursCohorteException(BusinessException):
    def __init__(self, cohortes_non_geres: Set[str], **kwargs):
        message = _("You're not a program manager of {}").format(','.join(cohortes_non_geres))
        super().__init__(message, **kwargs)


class AdresseSpecifiquePremiereAnneeDeBachelierIdentiqueAuBachlierException(BusinessException):
    def __init__(self, **kwargs):
        message = _("The address cannot be the same between bachelor and first year bachelor")
        super().__init__(message, **kwargs)


class EntiteAdressePremiereAnneeDeBachelierIdentiqueAuBachlierException(BusinessException):
    def __init__(self, **kwargs):
        message = _("The entity cannot be the same between bachelor and first year bachelor")
        super().__init__(message, **kwargs)


class EntiteNonValidePourAdresseException(BusinessException):
    def __init__(self, **kwargs):
        message = _("The entity is not valid for the score sheet address")
        super().__init__(message, **kwargs)


class EncoderNotesEtudiantEnLotLigneBusinessExceptions(BusinessException):
    def __init__(self, note_id: IdentiteNoteEtudiant, exception: BusinessException):
        self.note_id = note_id
        super().__init__(exception.message)


class EtudiantNonInscritAExamenException(BusinessException):
    def __init__(self, **kwargs):
        message = _("Student not registered for exam")
        super().__init__(message, **kwargs)
