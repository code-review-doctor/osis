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
import string

import factory
import uuid

from ddd.logic.projet_doctoral.domain.model._detail_projet import DetailProjet
from ddd.logic.projet_doctoral.domain.model._experience_precedente_recherche import \
    aucune_experience_precedente_recherche
from ddd.logic.projet_doctoral.domain.model._financement import financement_non_rempli
from ddd.logic.projet_doctoral.domain.model.proposition import (
    PropositionIdentity,
    Proposition,
    ChoixTypeAdmission,
    ChoixStatusProposition,
)
from education_group.tests.ddd.factories.domain.training import TrainingIdentityFactory


class _PropositionIdentityFactory(factory.Factory):
    class Meta:
        model = PropositionIdentity
        abstract = False

    uuid = uuid.uuid4()


class _DetailProjetFactory(factory.Factory):
    class Meta:
        model = DetailProjet
        abstract = False

    titre = 'Mon projet'
    resume = factory.Faker('sentence')
    documents = factory.LazyFunction(list)


class _PropositionFactory(factory.Factory):
    class Meta:
        model = Proposition
        abstract = False

    entity_id = factory.SubFactory(_PropositionIdentityFactory)
    matricule_candidat = factory.fuzzy.FuzzyText(length=10, chars=string.digits)
    formation_id = factory.SubFactory(TrainingIdentityFactory)
    status = ChoixStatusProposition.IN_PROGRESS
    projet = factory.SubFactory(_DetailProjetFactory)
    financement = financement_non_rempli
    experience_precedente_recherche = aucune_experience_precedente_recherche


class PropositionAdmissionSC3DPMinimaleFactory(_PropositionFactory):
    type_admission = ChoixTypeAdmission.ADMISSION
    formation_id = factory.SubFactory(TrainingIdentityFactory, acronym='SC3DP')


class PropositionAdmissionSC3DPMinimaleAnnuleeFactory(PropositionAdmissionSC3DPMinimaleFactory):
    status = ChoixStatusProposition.CANCELLED


class PropositionPreAdmissionSC3DPMinimaleFactory(_PropositionFactory):
    type_admission = ChoixTypeAdmission.PRE_ADMISSION
    formation_id = factory.SubFactory(TrainingIdentityFactory, acronym='SC3DP')
