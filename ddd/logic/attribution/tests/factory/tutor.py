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
import string
from decimal import Decimal

import factory.fuzzy
import uuid

from ddd.logic.attribution.domain.model._class_volume_repartition import ClassVolumeRepartition
from ddd.logic.attribution.domain.model._learning_unit_attribution import LearningUnitAttributionIdentity
from ddd.logic.attribution.domain.model.tutor import TutorIdentity, Tutor
from ddd.logic.learning_unit.tests.factory.effective_class import LDROI1001XEffectiveClassIdentityFactory


class _LearningUnitAttributionIdentityFactory(factory.Factory):
    class Meta:
        model = LearningUnitAttributionIdentity
        abstract = False

    uuid = uuid.uuid4()


class _TutorIdentityFactory(factory.Factory):
    class Meta:
        model = TutorIdentity
        abstract = False

    personal_id_number = factory.fuzzy.FuzzyText(length=10, chars=string.digits)


class _ClassVolumeRepartitionFactory(factory.Factory):
    class Meta:
        model = ClassVolumeRepartition
        abstract = False

    effective_class = factory.SubFactory(LDROI1001XEffectiveClassIdentityFactory)
    distributed_volume = Decimal(0.0)
    attribution = factory.SubFactory(_LearningUnitAttributionIdentityFactory)


class _TutorFactory(factory.Factory):
    class Meta:
        model = Tutor
        abstract = False

    entity_id = factory.SubFactory(_TutorIdentityFactory)
    distributed_effective_classes = factory.List([factory.SubFactory(_ClassVolumeRepartitionFactory)])


class TutorWithDistributedEffectiveClassesFactory(_TutorFactory):
    pass


class TutorWithoutDistributedEffectiveClassesFactory(_TutorFactory):
    distributed_effective_classes = []


class Tutor9999IdentityFactory(_TutorIdentityFactory):
    personal_id_number = "9999"
