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

from ddd.logic.encodage_des_notes.shared_kernel.dtos import EnseignantDTO, NoteEtudiantDTO, DetailContactDTO
from osis_common.ddd import interface


@attr.s(frozen=True, slots=True)
class CohorteGestionnaireDTO(interface.DTO):
    matricule_gestionnaire = attr.ib(type=str)
    nom_cohorte = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class FeuilleDeNotesParCohorteDTO(interface.DTO):
    code_unite_enseignement = attr.ib(type=str)
    intitule_complet_unite_enseignement = attr.ib(type=str)  # unite enseignement
    responsable_note = attr.ib(type=EnseignantDTO)  # responsables notes + signaletique enseignant ?
    contact_responsable_notes = attr.ib(type=DetailContactDTO)
    autres_enseignants = attr.ib(type=List[EnseignantDTO])  # attributions
    annee_academique = attr.ib(type=int)
    numero_session = attr.ib(type=int)
    notes_etudiants = attr.ib(type=List[NoteEtudiantDTO])

    @property
    def encodage_est_complet(self) -> bool:
        return self.quantite_notes_soumises == self.quantite_total_notes

    @property
    def quantite_notes_soumises(self) -> int:
        return sum(1 for note in self.notes_etudiants if note.note is not None and note.est_soumise)

    @property
    def quantite_total_notes(self) -> int:
        return len(self.notes_etudiants)

    @property
    def nombre_inscriptions(self) -> int:
        return self.quantite_total_notes


@attr.s(frozen=True, slots=True)
class NoteEtudiantFromRepositoryDTO(interface.DTO):
    noma = attr.ib(type=str)
    email = attr.ib(type=str)
    note = attr.ib(type=str)
    echeance_gestionnaire = attr.ib(type=str)
    numero_session = attr.ib(type=int)
    code_unite_enseignement = attr.ib(type=str)
    annee_academique = attr.ib(type=int)
    note_decimale_autorisee = attr.ib(type=bool)
    nom_cohorte = attr.ib(type=str)
