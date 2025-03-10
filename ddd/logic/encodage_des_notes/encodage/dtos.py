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
class ProprietesGestionnaireCohorteDTO(interface.DTO):
    est_principal = attr.ib(type=bool)
    nom_cohorte = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class GestionnaireCohortesDTO(interface.DTO):
    matricule_gestionnaire = attr.ib(type=str)
    nom = attr.ib(type=str)
    prenom = attr.ib(type=str)
    cohortes_gerees = attr.ib(type=List[ProprietesGestionnaireCohorteDTO], default=[])


@attr.s(frozen=True, slots=True)
class NoteEtudiantFromRepositoryDTO(interface.DTO):
    noma = attr.ib(type=str)
    email = attr.ib(type=str)
    note = attr.ib(type=str)
    echeance_gestionnaire = attr.ib(type=str)
    echeance_enseignant = attr.ib(type=str)
    numero_session = attr.ib(type=int)
    code_unite_enseignement = attr.ib(type=str)
    annee_academique = attr.ib(type=int)
    note_decimale_autorisee = attr.ib(type=bool)
    nom_cohorte = attr.ib(type=str)
