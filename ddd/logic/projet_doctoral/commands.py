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
from typing import List, Optional

import attr

from ddd.logic.projet_doctoral.domain.model._experience_precedente_recherche import ChoixDoctoratDejaRealise
from osis_common.ddd import interface

UUID = str


@attr.s(frozen=True, slots=True)
class InitierPropositionCommand(interface.CommandRequest):
    type_admission = attr.ib(type=str)
    sigle_formation = attr.ib(type=str)
    annee_formation = attr.ib(type=int)
    matricule_candidat = attr.ib(type=str)
    bureau_CDE = attr.ib(type=Optional[str], default='')  # CDE = Comission Doctorale du domaine Sciences Economique et de Gestion
    type_financement = attr.ib(type=Optional[str], default='')
    type_contrat_travail = attr.ib(type=Optional[str], default='')
    titre_projet = attr.ib(type=Optional[str], default='')
    resume_projet = attr.ib(type=Optional[str], default='')
    documents_projet = attr.ib(type=List[UUID], factory=list)
    doctorat_deja_realise = attr.ib(type=str, default=ChoixDoctoratDejaRealise.NO.name)
    institution = attr.ib(type=Optional[str], default='')


@attr.s(frozen=True, slots=True)
class CompleterPropositionCommand(interface.CommandRequest):
    uuid = attr.ib(type=str)
    type_admission = attr.ib(type=str)
    bureau_CDE = attr.ib(type=Optional[str], default='')  # CDE = Comission Doctorale du domaine Sciences Economique et de Gestion
    type_financement = attr.ib(type=Optional[str], default='')
    type_contrat_travail = attr.ib(type=Optional[str], default='')
    titre_projet = attr.ib(type=Optional[str], default='')
    resume_projet = attr.ib(type=Optional[str], default='')
    documents_projet = attr.ib(type=List[UUID], factory=list)
    doctorat_deja_realise = attr.ib(type=str, default=ChoixDoctoratDejaRealise.NO.name)
    institution = attr.ib(type=Optional[str], default='')


@attr.s(frozen=True, slots=True)
class SearchDoctoratCommand(interface.CommandRequest):
    sigle_secteur_entite_gestion = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class IdentifierPromoteurCommand(interface.CommandRequest):
    uuid_proposition = attr.ib(type=str)
    matricule = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class IdentifierMembreCACommand(interface.CommandRequest):
    uuid_proposition = attr.ib(type=str)
    matricule = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class DemanderSignatureCommand(interface.CommandRequest):
    uuid_proposition = attr.ib(type=str)
    matricule_signataire = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class SupprimerPromoteurCommand(interface.CommandRequest):
    uuid_proposition = attr.ib(type=str)
    matricule = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class SupprimerMembreCACommand(interface.CommandRequest):
    uuid_proposition = attr.ib(type=str)
    matricule = attr.ib(type=str)
