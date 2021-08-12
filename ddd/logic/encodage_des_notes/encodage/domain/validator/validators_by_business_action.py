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
from typing import List

import attr

from base.ddd.utils.business_validator import TwoStepsMultipleBusinessExceptionListValidator, BusinessValidator
from ddd.logic.encodage_des_notes.business_types import *
from ddd.logic.encodage_des_notes.encodage.domain.validator._should_date_echeance_non_atteinte import \
    ShouldDateEcheanceNonAtteinte
from ddd.logic.encodage_des_notes.encodage.domain.validator._should_email_correspondre_noma import \
    ShouldEmailCorrespondreNoma
from ddd.logic.encodage_des_notes.encodage.domain.validator._should_note_etre_choix_valide import \
    ShouldNoteEtreChoixValide
from ddd.logic.encodage_des_notes.encodage.domain.validator._should_verifier_note_decimale import \
    ShouldVerifierNoteDecimaleAutorisee


@attr.s(frozen=True, slots=True)
class EncoderNotesValidatorList(TwoStepsMultipleBusinessExceptionListValidator):

    note_etudiant = attr.ib(type='NoteEtudiant')  # type: NoteEtudiant
    email = attr.ib(type=str)
    note = attr.ib(type=str)

    def get_data_contract_validators(self) -> List[BusinessValidator]:
        return []

    def get_invariants_validators(self) -> List[BusinessValidator]:
        return [
            ShouldEmailCorrespondreNoma(self.note_etudiant, self.email),
            ShouldDateEcheanceNonAtteinte(self.note_etudiant),
            ShouldNoteEtreChoixValide(self.note),
            ShouldVerifierNoteDecimaleAutorisee(self.note, self.note_etudiant),
        ]
