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

import factory.fuzzy
import uuid

from attribution.models.enums.function import Functions
from base.models.enums.learning_unit_year_session import DerogationSession
from base.models.enums.quadrimesters import DerogationQuadrimester
from ddd.logic.attribution.domain.model._attribution import LearningUnitAttributionIdentity, LearningUnitAttribution
from ddd.logic.attribution.domain.model._class_volume_repartition import ClassVolumeRepartition
from ddd.logic.attribution.domain.model.tutor import TutorIdentity
from ddd.logic.learning_unit.domain.model._class_titles import ClassTitles
from ddd.logic.learning_unit.domain.model.effective_class import EffectiveClass
from ddd.logic.learning_unit.tests.factory.effective_class import _EffectiveClassIdentityFactory
from ddd.logic.learning_unit.tests.factory.learning_unit import _LearningUnitFactory, _UclouvainCampusIdentityFactory


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


class _ClassTitlesFactory(factory.Factory):
    class Meta:
        model = ClassTitles
        abstract = False

    fr = factory.fuzzy.FuzzyText(length=240)
    en = factory.fuzzy.FuzzyText(length=240)


class _ClassVolumeRepartitionFactory(factory.Factory):
    class Meta:
        model = ClassVolumeRepartition
        abstract = False

    effective_class = factory.SubFactory(_EffectiveClassIdentityFactory)
    distributed_volume = 0


class _LearningUnitAttributionFactory(factory.Factory):
    class Meta:
        model = LearningUnitAttribution
        abstract = False

    entity_id = factory.SubFactory(_LearningUnitAttributionIdentityFactory)
    function = factory.fuzzy.FuzzyChoice(choices=Functions)
    learning_unit = factory.SubFactory(_LearningUnitFactory)
    distributed_effective_classes = [factory.SubFactory(_ClassVolumeRepartitionFactory)]


class _EffectiveClassFactory(factory.Factory):
    class Meta:
        model = EffectiveClass
        abstract = False

    entity_id = factory.SubFactory(_EffectiveClassIdentityFactory)
    titles = factory.SubFactory(_ClassTitlesFactory)
    teaching_place = factory.SubFactory(_UclouvainCampusIdentityFactory)
    derogation_quadrimester = factory.fuzzy.FuzzyChoice(choices=DerogationQuadrimester)
    session_derogation = factory.fuzzy.FuzzyChoice(choices=DerogationSession)
    volumes = factory.SubFactory(_LearningUnitAttributionFactory)
