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
from datetime import date

import attr

from ddd.logic.encodage_des_notes.shared_kernel.dtos import DateDTO
from ddd.logic.encodage_des_notes.soumission.domain.model._note import Note
from ddd.logic.encodage_des_notes.soumission.domain.model._note import NoteBuilder
from ddd.logic.encodage_des_notes.soumission.domain.validator.validators_by_business_action import \
    EncoderNoteEtudiantValidatorList
from osis_common.ddd import interface

Noma = str

CREDITS_MIN_POUR_NOTE_DECIMALE = 15.0


@attr.s(frozen=True, slots=True)
class IdentiteNoteEtudiant(interface.EntityIdentity):
    noma = attr.ib(type=Noma)
    code_unite_enseignement = attr.ib(type=str)
    annee_academique = attr.ib(type=int)
    numero_session = attr.ib(type=int)


@attr.s(slots=True, eq=False)
class NoteEtudiant(interface.Entity):
    entity_id = attr.ib(type=IdentiteNoteEtudiant)
    note = attr.ib(type=Note)
    nom_cohorte = attr.ib(type=str)
    credits_unite_enseignement = attr.ib(type=float)
    date_limite_de_remise = attr.ib(type=DateDTO)
    email = attr.ib(type=str)
    est_soumise = attr.ib(type=bool)

    @property
    def noma(self) -> str:
        return self.entity_id.noma

    @property
    def code_unite_enseignement(self) -> str:
        return self.entity_id.code_unite_enseignement

    @property
    def annee(self) -> int:
        return self.entity_id.annee_academique

    @property
    def numero_session(self) -> int:
        return self.entity_id.numero_session

    @property
    def is_chiffree(self) -> bool:
        return type(self.note.value) in (float, int)

    @property
    def is_manquant(self) -> bool:
        return self.note.is_manquant

    @property
    def is_justification(self) -> bool:
        return not self.is_manquant and not self.is_chiffree

    def encoder(self, email: str, note_encodee: str) -> None:
        EncoderNoteEtudiantValidatorList(email=email, note_encodee=note_encodee, note_etudiant=self).validate()
        self.note = NoteBuilder.build(note_encodee)

    def note_decimale_est_autorisee(self) -> bool:
        return self.credits_unite_enseignement >= CREDITS_MIN_POUR_NOTE_DECIMALE

    def get_date_limite_de_remise(self) -> 'date':
        return self.date_limite_de_remise.to_date()

    def soumettre(self) -> None:
        if not self.is_manquant:
            self.est_soumise = True
