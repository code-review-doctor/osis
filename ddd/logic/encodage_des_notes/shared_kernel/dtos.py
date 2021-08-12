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
import datetime
from datetime import date
from typing import List, Set, Optional

import attr

from osis_common.ddd import interface


@attr.s(frozen=True, slots=True)
class EnseignantDTO(interface.DTO):
    nom = attr.ib(type=str)
    prenom = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class DateDTO(interface.DTO):
    jour = attr.ib(type=int)
    mois = attr.ib(type=int)
    annee = attr.ib(type=int)

    def to_date(self) -> date:
        return date(day=self.jour, month=self.mois, year=self.annee)

    @staticmethod
    def build_from_date(d: date):
        return DateDTO(jour=d.day, mois=d.month, annee=d.year)


@attr.s(frozen=True, slots=True)
class EtudiantPepsDTO(interface.DTO):
    type_peps = attr.ib(type=str)
    tiers_temps = attr.ib(type=bool)
    copie_adaptee = attr.ib(type=bool)
    local_specifique = attr.ib(type=bool)
    autre_amenagement = attr.ib(type=bool)
    details_autre_amenagement = attr.ib(type=str)
    accompagnateur = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class NoteEtudiantDTO(interface.DTO):
    est_soumise = attr.ib(type=bool)
    date_remise_de_notes = attr.ib(type=DateDTO)  # TODO :: renommer en echeance_enseignant
    nom_cohorte = attr.ib(type=str)  # inscription examen
    noma = attr.ib(type=str)  # matricule
    nom = attr.ib(type=str)  # signaletique
    prenom = attr.ib(type=str)  # signaletique
    peps = attr.ib(type=Optional[EtudiantPepsDTO])  # signaletique
    email = attr.ib(type=str)
    note = attr.ib(type=str)
    inscrit_tardivement = attr.ib(type=bool)  # inscription examen
    desinscrit_tardivement = attr.ib(type=bool)  # inscription examen

    @property
    def date_echeance_atteinte(self) -> bool:
        date_dto = self.date_remise_de_notes
        date_de_remise = datetime.date(day=date_dto.jour, month=date_dto.mois, year=date_dto.annee)
        aujourdhui = datetime.date.today()
        return aujourdhui > date_de_remise


@attr.s(frozen=True, slots=True)
class FeuilleDeNotesDTO(interface.DTO):
    code_unite_enseignement = attr.ib(type=str)
    intitule_complet_unite_enseignement = attr.ib(type=str)  # unite enseignement
    responsable_note = attr.ib(type=EnseignantDTO)  # responsables notes + signaletique enseignant ?
    autres_enseignants = attr.ib(type=List[EnseignantDTO])  # attributions
    annee_academique = attr.ib(type=int)
    numero_session = attr.ib(type=int)
    note_decimale_est_autorisee = attr.ib(type=bool)
    notes_etudiants = attr.ib(type=List[NoteEtudiantDTO])

    @property
    def encodage_est_complet(self) -> bool:
        return self.quantite_notes_soumises / self.quantite_total_notes == 0

    @property
    def quantite_notes_soumises(self) -> int:
        return sum(1 for note in self.notes_etudiants if note.note is not None and note.est_soumise)

    @property
    def quantite_total_notes(self) -> int:
        return len(self.notes_etudiants)

    @property
    def nombre_inscriptions(self) -> int:
        return self.quantite_total_notes
