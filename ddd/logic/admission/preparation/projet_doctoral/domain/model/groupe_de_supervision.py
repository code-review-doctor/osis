# ##############################################################################
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
# ##############################################################################
from typing import List, Union

import attr

from ddd.logic.admission.preparation.projet_doctoral.domain.model._cotutelle import Cotutelle, pas_de_cotutelle
from ddd.logic.admission.preparation.projet_doctoral.domain.model._membre_CA import MembreCAIdentity
from ddd.logic.admission.preparation.projet_doctoral.domain.model._promoteur import PromoteurIdentity
from ddd.logic.admission.preparation.projet_doctoral.domain.model._signature_membre_CA import SignatureMembreCA
from ddd.logic.admission.preparation.projet_doctoral.domain.model._signature_promoteur import (
    SignaturePromoteur,
    ChoixEtatSignature,
)
from ddd.logic.admission.preparation.projet_doctoral.domain.model.proposition import PropositionIdentity
from ddd.logic.admission.preparation.projet_doctoral.domain.validator.validator_by_business_action import (
    IdentifierPromoteurValidatorList,
    IdentifierMembreCAValidatorList,
)
from osis_common.ddd import interface


@attr.s(slots=True)
class GroupeDeSupervisionIdentity(interface.EntityIdentity):
    uuid = attr.ib(type=str)


@attr.s(slots=True)
class GroupeDeSupervision(interface.Entity):
    entity_id = attr.ib(type=GroupeDeSupervisionIdentity)
    proposition_id = attr.ib(type=PropositionIdentity)
    signatures_promoteurs = attr.ib(type=List[SignaturePromoteur], factory=list)
    signatures_membres_CA = attr.ib(type=List[SignatureMembreCA], factory=list)
    cotutelle = attr.ib(type=Cotutelle, default=pas_de_cotutelle)

    def identifier_promoteur(self, promoteur_id: 'PromoteurIdentity') -> None:
        IdentifierPromoteurValidatorList(
            groupe_de_supervision=self,
            promoteur_id=promoteur_id,
        ).validate()
        self.signatures_promoteurs.append(
            SignaturePromoteur(promoteur_id=promoteur_id, etat=ChoixEtatSignature.NOT_INVITED)
        )

    def identifier_membre_CA(self, membre_CA_id: 'MembreCAIdentity') -> None:
        IdentifierMembreCAValidatorList(
            groupe_de_supervision=self,
            membre_CA_id=membre_CA_id,
        ).validate()
        self.signatures_membres_CA.append(
            SignatureMembreCA(membre_CA_id=membre_CA_id, etat=ChoixEtatSignature.NOT_INVITED)
        )

    def get_signataire(self, matricule_signataire: str) -> Union['PromoteurIdentity', 'MembreCAIdentity']:
        pass

    def inviter_a_signer(self, signataire_id: Union['PromoteurIdentity', 'MembreCAIdentity']) -> None:
        # TODO :: verifier si signataire dans membres_CA ou promoteurs
        # TODO :: appeler ValidatorList
        # TODO set etat to ChoixEtatSignature.INVITED
        raise NotImplementedError

    def supprimer_promoteur(self, promoteur_id: 'PromoteurIdentity') -> None:
        # TODO :: verifier si signataire dans membres_CA ou promoteurs
        # TODO :: appeler ValidatorList
        raise NotImplementedError

    def supprimer_membre_CA(self, membre_CA_id: 'MembreCAIdentity') -> None:
        # TODO :: verifier si signataire dans membres_CA ou promoteurs
        # TODO :: appeler ValidatorList
        raise NotImplementedError

    def approuver(self, signataire_id: Union['PromoteurIdentity', 'MembreCAIdentity']) -> None:
        # TODO :: verifier si signataire dans membres_CA ou promoteurs
        # TODO :: appeler ValidatorList
        raise NotImplementedError

    def verifier_tout_le_monde_a_approuve(self):
        raise NotImplementedError

    def verifier_cotutelle(self):
        raise NotImplementedError

    def definir_cotutelle(self, motivation: str, institution: str, demande_ouverture: str):
        self.cotutelle = Cotutelle(
            motivation=motivation,
            institution=institution,
            demande_ouverture=demande_ouverture,
        )
