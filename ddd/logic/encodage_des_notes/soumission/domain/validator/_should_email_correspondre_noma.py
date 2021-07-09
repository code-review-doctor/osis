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

import attr

from base.ddd.utils.business_validator import BusinessValidator
from ddd.logic.encodage_des_notes.business_types import FeuilleDeNotes
from ddd.logic.encodage_des_notes.soumission.domain.validator.exceptions import NomaNeCorrespondPasEmailException


@attr.s(frozen=True, slots=True)
class ShouldEmailCorrespondreNoma(BusinessValidator):
    noma_etudiant = attr.ib(type=str)
    email_etudiant = attr.ib(type=str)
    feuille_de_note = attr.ib(type=FeuilleDeNotes)

    def validate(self, *args, **kwargs):
        correspondance_existe = any(
            note for note in self.feuille_de_note.notes
            if note.email == self.email_etudiant and note.entity_id.noma == self.noma_etudiant
        )
        if not correspondance_existe:
            raise NomaNeCorrespondPasEmailException()
