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
from django.utils.translation import gettext_lazy as _

from base.models.utils.utils import ChoiceEnum
from ddd.logic.projet_doctoral.domain.model._detail_projet import DetailProjet
from ddd.logic.projet_doctoral.domain.model._experience_precedente_recherche import (
    ExperiencePrecedenteRecherche,
    aucune_experience_precedente_recherche, ChoixDoctoratDejaRealise,
)
from ddd.logic.projet_doctoral.domain.model._financement import (
    Financement,
    financement_non_rempli, ChoixTypeFinancement,
)
from ddd.logic.projet_doctoral.domain.model.doctorat import DoctoratIdentity
from ddd.logic.projet_doctoral.domain.model.membre_CA import MembreCAIdentity
from ddd.logic.projet_doctoral.domain.model.promoteur import PromoteurIdentity
from ddd.logic.projet_doctoral.domain.validator.validator_by_business_action import CompletionPropositionValidatorList
from osis_common.ddd import interface


class ChoixStatusProposition(ChoiceEnum):
    CANCELLED = _('CANCELLED')
    IN_PROGRESS = _('IN_PROGRESS')


class ChoixBureauCDE(ChoiceEnum):
    ECONOMY = _('ECONOMY')
    MANAGEMENT = _('MANAGEMENT')


class ChoixTypeAdmission(ChoiceEnum):
    ADMISSION = _('ADMISSION')
    PRE_ADMISSION = _('PRE_ADMISSION')


@attr.s(frozen=True, slots=True)
class PropositionIdentity(interface.EntityIdentity):
    uuid = attr.ib(type=str)


@attr.s(slots=True, hash=False, eq=False)
class Proposition(interface.RootEntity):
    entity_id = attr.ib(type=PropositionIdentity)
    type_admission = attr.ib(type=ChoixTypeAdmission)
    doctorat_id = attr.ib(type=DoctoratIdentity)
    matricule_candidat = attr.ib(type=str)
    projet = attr.ib(type=DetailProjet)
    status = attr.ib(type=ChoixStatusProposition, default=ChoixStatusProposition.IN_PROGRESS)
    bureau_CDE = attr.ib(
        type=ChoixBureauCDE,
        default=None,
    )  # CDE = Comission Doctorale du domaine Sciences Economique et de Gestion
    financement = attr.ib(type=Financement, default=financement_non_rempli)
    experience_precedente_recherche = attr.ib(
        type=ExperiencePrecedenteRecherche,
        default=aucune_experience_precedente_recherche,
    )

    @property
    def sigle_formation(self):
        return self.doctorat_id.sigle

    @property
    def annee(self):
        return self.doctorat_id.annee

    def est_en_cours(self):
        return self.status == ChoixStatusProposition.IN_PROGRESS

    def completer(
            self,
            type_admission: str,
            bureau_CDE: str,
            type_financement: str,
            type_contrat_travail: str,
            titre: str,
            resume: str,
            doctorat_deja_realise: str,
            institution: str,
            documents: List[str] = None,
    ) -> None:
        CompletionPropositionValidatorList(
            type_financement=type_financement,
            type_contrat_travail=type_contrat_travail,
            doctorat_deja_realise=doctorat_deja_realise,
            institution=institution,
        ).validate()
        self._completer_proposition(type_admission, bureau_CDE)
        self._completer_financement(type_financement, type_contrat_travail)
        self._completer_projet(titre, resume, documents)
        self._completer_experience_precedente(doctorat_deja_realise, institution)

    def _completer_proposition(self, type_admission: str, bureau_CDE: str):
        self.type_admission = ChoixTypeAdmission[type_admission]
        self.bureau_CDE = ChoixBureauCDE[bureau_CDE] if bureau_CDE else ''

    def _completer_financement(self, type: str, type_contrat_travail: str):
        if type:
            self.financement = Financement(
                type=ChoixTypeFinancement[type],
                type_contrat_travail=type_contrat_travail,
            )
        else:
            self.financement = financement_non_rempli

    def _completer_projet(self, titre: str, resume: str, documents: List[str] = None):
        self.projet = DetailProjet(
            titre=titre,
            resume=resume,
            documents=documents,
        )

    def _completer_experience_precedente(self, doctorat_deja_realise: str, institution: str):
        if doctorat_deja_realise == ChoixDoctoratDejaRealise.NO.name:
            self.experience_precedente_recherche = aucune_experience_precedente_recherche
        else:
            self.experience_precedente_recherche = ExperiencePrecedenteRecherche(
                doctorat_deja_realise=ChoixDoctoratDejaRealise[doctorat_deja_realise],
                institution=institution,
            )

    def identifier_promoteur(self, promoteur_id: 'PromoteurIdentity') -> None:
        raise NotImplementedError

    def identifier_membre_CA(self, membre_CA_id: 'MembreCAIdentity') -> None:
        raise NotImplementedError
