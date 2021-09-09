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
from typing import List, Optional

import attr

from osis_common.ddd import interface


@attr.s(frozen=True, slots=True)
class AdresseDTO(interface.DTO):
    code_postal = attr.ib(type=str)
    ville = attr.ib(type=str)
    rue_numero_boite = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class DetailContactDTO(interface.DTO):
    matricule_fgs = attr.ib(type=str)
    email = attr.ib(type=str)
    adresse_professionnelle = attr.ib(type=Optional[AdresseDTO])
    langue = attr.ib(type=str)


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
    code_unite_enseignement = attr.ib(type=str)
    annee_unite_enseignement = attr.ib(type=int)
    intitule_complet_unite_enseignement = attr.ib(type=str)
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

    def est_en_attente_de_soumission(self) -> bool:
        return self.note != '' and not self.est_soumise


@attr.s(frozen=True, slots=True)
class FeuilleDeNotesDTO(interface.DTO):
    code_unite_enseignement = attr.ib(type=str)
    intitule_complet_unite_enseignement = attr.ib(type=str)  # unite enseignement
    responsable_note = attr.ib(type=EnseignantDTO)  # responsables notes + signaletique enseignant ?
    contact_responsable_notes = attr.ib(type=DetailContactDTO)
    autres_enseignants = attr.ib(type=List[EnseignantDTO])  # attributions
    annee_academique = attr.ib(type=int)
    numero_session = attr.ib(type=int)
    note_decimale_est_autorisee = attr.ib(type=bool)
    notes_etudiants = attr.ib(type=List[NoteEtudiantDTO])

    @property
    def encodage_est_complet(self) -> bool:
        return self.quantite_notes_soumises == self.quantite_total_notes

    @property
    def quantite_notes_soumises(self) -> int:
        return sum(1 for note in self.notes_etudiants if note.note is not None and note.est_soumise)

    @property
    def quantite_notes_en_attente_de_soumission(self) -> int:
        return sum(1 for note in self.notes_etudiants if note.est_en_attente_de_soumission())

    @property
    def quantite_total_notes(self) -> int:
        return len(self.notes_etudiants)

    @property
    def nombre_inscriptions(self) -> int:
        return self.quantite_total_notes

    def get_email_for_noma(self, noma: str) -> str:
        return next(note_etudiant.email for note_etudiant in self.notes_etudiants if note_etudiant.noma == noma)

    def get_notes_en_attente_de_soumission(self) -> List[NoteEtudiantDTO]:
        return [note for note in self.notes_etudiants if note.est_en_attente_de_soumission()]


@attr.s(frozen=True, slots=True)
class PeriodeEncodageNotesDTO(interface.DTO):
    annee_concernee = attr.ib(type=int)
    session_concernee = attr.ib(type=int)
    debut_periode_soumission = attr.ib(type=DateDTO)
    fin_periode_soumission = attr.ib(type=DateDTO)


@attr.s(frozen=True, slots=True)
class DateEcheanceDTO(interface.DTO):
    jour = attr.ib(type=int)
    mois = attr.ib(type=int)
    annee = attr.ib(type=int)
    quantite_notes_soumises = attr.ib(type=int)
    quantite_total_notes = attr.ib(type=int)

    def to_date(self) -> date:
        return date(day=self.jour, month=self.mois, year=self.annee)

    @property
    def est_atteinte(self) -> bool:
        aujourdhui = datetime.date.today()
        return aujourdhui > self.to_date()

    @property
    def quantite_notes_manquantes(self) -> int:
        return self.quantite_total_notes - self.quantite_notes_soumises

    @property
    def encodage_est_complet(self) -> bool:
        return self.quantite_notes_manquantes == 0


@attr.s(frozen=True, slots=True)
class ProgressionEncodageNotesUniteEnseignementDTO(interface.DTO):
    code_unite_enseignement = attr.ib(type=str)
    intitule_complet_unite_enseignement = attr.ib(type=str)  # unite enseignement
    dates_echeance = attr.ib(type=List[DateEcheanceDTO])
    responsable_note = attr.ib(type=EnseignantDTO)  # responsables notes
    a_etudiants_peps = attr.ib(type=bool)  # signaletique

    @property
    def quantite_notes_soumises(self) -> int:
        return sum(date.quantite_notes_soumises for date in self.dates_echeance)

    @property
    def quantite_totale_notes(self) -> int:
        return sum(date.quantite_total_notes for date in self.dates_echeance)

    @property
    def encodage_est_complet(self) -> bool:
        return self.quantite_notes_soumises == self.quantite_totale_notes


@attr.s(frozen=True, slots=True)
class ProgressionGeneraleEncodageNotesDTO(interface.DTO):
    annee_academique = attr.ib(type=int)
    numero_session = attr.ib(type=int)
    progression_generale = attr.ib(type=List[ProgressionEncodageNotesUniteEnseignementDTO])
