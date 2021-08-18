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
from typing import List, Set, Optional

import attr

from ddd.logic.encodage_des_notes.shared_kernel.dtos import DateDTO, EtudiantPepsDTO
from osis_common.ddd import interface


def none2emptystr(value) -> str:
    return value or ''


@attr.s(frozen=True, slots=True)
class DateEcheanceDTO(interface.DTO):
    jour = attr.ib(type=int)
    mois = attr.ib(type=int)
    annee = attr.ib(type=int)
    quantite_notes_soumises = attr.ib(type=int)
    quantite_total_notes = attr.ib(type=int)

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
    a_etudiants_peps = attr.ib(type=bool)  # signaletique

    @property
    def quantite_notes_soumises(self) -> int:
        return sum(date.quantite_notes_soumises for date in self.dates_echeance)

    @property
    def quantite_totale_notes(self) -> int:
        return sum(date.quantite_total_notes for date in self.dates_echeance)

    @property
    def encodage_est_complet(self) -> bool:
        return self.quantite_notes_soumises / self.quantite_totale_notes == 0


@attr.s(frozen=True, slots=True)
class ProgressionGeneraleEncodageNotesDTO(interface.DTO):
    annee_academique = attr.ib(type=int)
    numero_session = attr.ib(type=int)
    progression_generale = attr.ib(type=List[ProgressionEncodageNotesUniteEnseignementDTO])


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


@attr.s(frozen=True, slots=True)
class AdresseFeuilleDeNotesDTO(interface.DTO):
    nom_cohorte = attr.ib(type=str)
    destinataire = attr.ib(type=str, converter=none2emptystr)
    rue_et_numero = attr.ib(type=str, converter=none2emptystr)
    code_postal = attr.ib(type=str, converter=none2emptystr)
    ville = attr.ib(type=str, converter=none2emptystr)
    pays = attr.ib(type=str, converter=none2emptystr)
    telephone = attr.ib(type=str, converter=none2emptystr)
    fax = attr.ib(type=str, converter=none2emptystr)
    email = attr.ib(type=str, converter=none2emptystr)


@attr.s(frozen=True, slots=True)
class DonneesAdministrativesFeuilleDeNotesDTO(interface.DTO):
    sigle_formation = attr.ib(type=str)
    code_unite_enseignement = attr.ib(type=str)
    date_deliberation = attr.ib(type=DateDTO)
    contact_responsable_notes = attr.ib(type=DetailContactDTO)  # FIXME :: déplacer dans FeuilleDeNotesEnseignantDTO ?
    contact_feuille_de_notes = attr.ib(type=AdresseFeuilleDeNotesDTO)


@attr.s(frozen=True, slots=True)
class AttributionEnseignantDTO(interface.DTO):
    matricule_fgs_enseignant = attr.ib(type=str)
    code_unite_enseignement = attr.ib(type=str)
    annee = attr.ib(type=int)
    nom = attr.ib(type=str)
    prenom = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class NoteEtudiantFromRepositoryDTO(interface.DTO):
    noma = attr.ib(type=str)
    email = attr.ib(type=str)
    note = attr.ib(type=str)
    date_limite_de_remise = attr.ib(type=date)
    est_soumise = attr.ib(type=bool)
    numero_session = attr.ib(type=int)
    code_unite_enseignement = attr.ib(type=str)
    annee_academique = attr.ib(type=int)
    credits_unite_enseignement = attr.ib(type=float)


@attr.s(frozen=True, slots=True)
class FeuilleDeNotesFromRepositoryDTO(interface.DTO):
    numero_session = attr.ib(type=int)
    code_unite_enseignement = attr.ib(type=str)
    annee_academique = attr.ib(type=int)
    credits_unite_enseignement = attr.ib(type=float)
    notes = attr.ib(type=Set[NoteEtudiantFromRepositoryDTO])


@attr.s(frozen=True, slots=True)
class SignaletiqueEtudiantDTO(interface.DTO):
    noma = attr.ib(type=str)
    nom = attr.ib(type=str)
    prenom = attr.ib(type=int)
    peps = attr.ib(type=Optional[EtudiantPepsDTO])


@attr.s(frozen=True, slots=True)
class InscriptionExamenDTO(interface.DTO):
    annee = attr.ib(type=int)
    noma = attr.ib(type=str)
    code_unite_enseignement = attr.ib(type=str)
    nom_cohorte = attr.ib(type=str)
    date_inscription = attr.ib(type=DateDTO)


@attr.s(frozen=True, slots=True)
class InscriptionCohorteDTO(interface.DTO):
    annee = attr.ib(type=int)
    noma = attr.ib(type=str)
    nom_cohorte = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class DeliberationDTO(interface.DTO):
    annee = attr.ib(type=int)
    session = attr.ib(type=int)
    nom_cohorte = attr.ib(type=str)
    date = attr.ib(type=DateDTO)


@attr.s(frozen=True, slots=True)
class DesinscriptionExamenDTO(interface.DTO):
    annee = attr.ib(type=int)
    noma = attr.ib(type=str)
    code_unite_enseignement = attr.ib(type=str)
    nom_cohorte = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class UniteEnseignementDTO(interface.DTO):
    annee = attr.ib(type=int)
    code = attr.ib(type=str)
    intitule_complet = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class UniteEnseignementIdentiteFromRepositoryDTO(interface.DTO):
    code_unite_enseignement = attr.ib(type=str)
    annee_academique = attr.ib(type=int)


@attr.s(frozen=True, slots=True)
class ResponsableDeNotesFromRepositoryDTO(interface.DTO):
    matricule_fgs_enseignant = attr.ib(type=str)
    unites_enseignements = attr.ib(type=Set[UniteEnseignementIdentiteFromRepositoryDTO])
