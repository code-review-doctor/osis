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
from ddd.logic.encodage_des_notes.business_types import FeuilleDeNotes
from ddd.logic.encodage_des_notes.soumission.domain.validator._should_date_soumission_pas_etre_atteinte import \
    ShouldDateSoumissionPasEtreAtteinte
from ddd.logic.encodage_des_notes.soumission.domain.validator._should_email_correspondre_noma import \
    ShouldEmailCorrespondreNoma
from ddd.logic.encodage_des_notes.soumission.domain.validator._should_etudiant_etre_present_feuille_de_notes import \
    ShouldEtudiantEtrePresentFeuilleDeNotes
from ddd.logic.encodage_des_notes.soumission.domain.validator._should_note_etre_choix_valide import \
    ShouldNoteEtreChoixValide
from ddd.logic.encodage_des_notes.soumission.domain.validator._should_note_pas_etre_soumise import \
    ShouldNotePasEtreSoumise


@attr.s(frozen=True, slots=True)
class EncoderFeuilleDeNotesValidatorList(TwoStepsMultipleBusinessExceptionListValidator):

    noma = attr.ib(type=str)
    email = attr.ib(type=str)
    note = attr.ib(type=str)
    feuille_de_notes = attr.ib(type=FeuilleDeNotes)

    def get_data_contract_validators(self) -> List[BusinessValidator]:
        return []

    def get_invariants_validators(self) -> List[BusinessValidator]:
        return [
            ShouldEtudiantEtrePresentFeuilleDeNotes(self.noma, self.feuille_de_notes),
            ShouldEmailCorrespondreNoma(self.noma, self.email, self.feuille_de_notes),
            ShouldDateSoumissionPasEtreAtteinte(self.feuille_de_notes),
            ShouldNotePasEtreSoumise(self.note),
            ShouldNoteEtreChoixValide(self.note),
        ]
