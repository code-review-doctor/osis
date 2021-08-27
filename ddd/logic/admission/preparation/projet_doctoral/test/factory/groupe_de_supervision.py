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
import uuid

import factory

from ddd.logic.admission.preparation.projet_doctoral.domain.model._cotutelle import pas_de_cotutelle
from ddd.logic.admission.preparation.projet_doctoral.domain.model.groupe_de_supervision import (
    GroupeDeSupervisionIdentity, GroupeDeSupervision,
)
from ddd.logic.admission.preparation.projet_doctoral.test.factory.proposition import (
    _PropositionIdentityFactory,
)


class _GroupeDeSupervisionIdentityFactory(factory.Factory):
    class Meta:
        model = GroupeDeSupervisionIdentity
        abstract = False

    uuid = factory.LazyFunction(lambda: str(uuid.uuid4()))


class _GroupeDeSupervisionFactory(factory.Factory):
    class Meta:
        model = GroupeDeSupervision
        abstract = False

    entity_id = factory.SubFactory(_GroupeDeSupervisionIdentityFactory)
    proposition_id = factory.SubFactory(_PropositionIdentityFactory)
    signatures_promoteurs = factory.LazyFunction(list)
    signatures_membres_CA = factory.LazyFunction(list)
    cotutelle = pas_de_cotutelle


class GroupeDeSupervisionSC3DPFactory(_GroupeDeSupervisionFactory):
    proposition_id = factory.SubFactory(_PropositionIdentityFactory, uuid='uuid-SC3DP')
