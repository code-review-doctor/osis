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
from typing import List

import attr

from ddd.logic.projet_doctoral.domain.model._membre_CA import MembreCAIdentity
from ddd.logic.projet_doctoral.domain.model._promoteur import PromoteurIdentity
from ddd.logic.projet_doctoral.domain.model._signature_membre_CA import SignatureMembreCA
from ddd.logic.projet_doctoral.domain.model._signature_promoteur import SignaturePromoteur
from ddd.logic.projet_doctoral.domain.model.proposition import PropositionIdentity
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

    def identifier_promoteur(self, promoteur_id: 'PromoteurIdentity') -> None:
        # TODO :: verifier si pas deja présent
        # TODO :: verifier si pas deja dans membres_CA
        # TODO :: appeler ValidatorList
        raise NotImplementedError

    def identifier_membre_CA(self, membre_CA_id: 'MembreCAIdentity') -> None:
        # TODO :: verifier si pas deja présent
        # TODO :: verifier si pas deja dans promoteurs
        # TODO :: appeler ValidatorList
        raise NotImplementedError

    def inviter_a_signer(self, matricule_signataire):
        # TODO :: verifier si signataire dans membres_CA ou promoteurs
        # TODO :: appeler ValidatorList
        # TODO set etat to ChoixEtatSignature.INVITED
        raise NotImplementedError

    def supprimer_promoteur(self, promoteur_id: 'PromoteurIdentity'):
        # TODO :: verifier si signataire dans membres_CA ou promoteurs
        # TODO :: appeler ValidatorList
        raise NotImplementedError

    def supprimer_membre_CA(self, membre_CA_id: 'MembreCAIdentity'):
        # TODO :: verifier si signataire dans membres_CA ou promoteurs
        # TODO :: appeler ValidatorList
        raise NotImplementedError
