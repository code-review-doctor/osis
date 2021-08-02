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
from collections import Counter
from datetime import date
from typing import Set, Dict

import attr

from ddd.logic.encodage_des_notes.soumission.domain.model._note import NoteBuilder
from ddd.logic.encodage_des_notes.soumission.domain.model._note_etudiant import NoteEtudiant
from ddd.logic.encodage_des_notes.soumission.domain.validator.validators_by_business_action import \
    EncoderFeuilleDeNotesValidatorList
from osis_common.ddd import interface

CREDITS_MIN_POUR_NOTE_DECIMALE = 15.0


@attr.s(frozen=True, slots=True)
class IdentiteFeuilleDeNotes(interface.EntityIdentity):
    numero_session = attr.ib(type=int)
    code_unite_enseignement = attr.ib(type=str)
    annee_academique = attr.ib(type=int)


@attr.s(slots=True, eq=False)
class FeuilleDeNotes(interface.RootEntity):
    entity_id = attr.ib(type=IdentiteFeuilleDeNotes)
    credits_unite_enseignement = attr.ib(type=float)
    notes = attr.ib(type=Set[NoteEtudiant])  # type: Set[NoteEtudiant]

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
    def total_notes_soumises(self) -> int:
        return sum(1 for note in self.notes if note.est_soumise)

    def note_decimale_est_autorisee(self) -> bool:
        return self.credits_unite_enseignement >= CREDITS_MIN_POUR_NOTE_DECIMALE

    def get_all_nomas(self) -> Set[str]:
        return {note.noma for note in self.notes}

    def get_nombre_notes_soumises_par_echeance(self) -> Dict[date, int]:
        dates_limite_de_remise_pour_notes_soumises = [
            note.date_limite_de_remise
            for note in self.notes if note.est_soumise
        ]
        return dict(Counter(dates_limite_de_remise_pour_notes_soumises))

    def get_nombre_total_notes_par_echeance(self) -> Dict[date, int]:
        dates_limite_de_remise_pour_notes = [note.date_limite_de_remise for note in self.notes]
        return dict(Counter(dates_limite_de_remise_pour_notes))

    def encoder_note(
            self,
            noma: str,
            email: str,
            note_encodee: str,
    ) -> None:
        EncoderFeuilleDeNotesValidatorList(
            noma=noma,
            email=email,
            note=note_encodee,
            feuille_de_notes=self,
        ).validate()
        note_etudiant = self.__get_note_etudiant(noma)
        note_etudiant.note = NoteBuilder.build(note_encodee)

    def soumettre(self) -> None:
        for note in self.notes:
            if not note.est_soumise and not note.is_manquant:
                note.est_soumise = True

    def get_date_limite_de_remise(self, noma: str) -> date:
        note = self.__get_note_etudiant(noma)
        return note.date_limite_de_remise.to_date()

    def __get_note_etudiant(self, noma: str) -> 'NoteEtudiant':
        return next(note for note in self.notes if note.noma == noma)

    def note_est_soumise(self, noma: str) -> bool:
        return self.__get_note_etudiant(noma).est_soumise
