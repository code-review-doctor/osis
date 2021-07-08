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
import factory.fuzzy

from base.models.enums.learning_unit_year_session import DerogationSession
from base.models.enums.quadrimesters import DerogationQuadrimester
from ddd.logic.learning_unit.domain.model._class_titles import ClassTitles
from ddd.logic.learning_unit.domain.model._volumes_repartition import ClassVolumes
from ddd.logic.shared_kernel.campus.domain.model.uclouvain_campus import UclouvainCampusIdentity
from ddd.logic.learning_unit.domain.model.effective_class import EffectiveClass, EffectiveClassIdentity, \
    LecturingEffectiveClass, PracticalEffectiveClass
from ddd.logic.learning_unit.tests.factory.learning_unit import _LearningUnitIdentityFactory, \
    _UclouvainCampusIdentityFactory


class _ClassTitlesFactory(factory.Factory):
    class Meta:
        model = ClassTitles
        abstract = False

    fr = factory.fuzzy.FuzzyText(length=240)
    en = factory.fuzzy.FuzzyText(length=240)


class _ClassVolumesFactory(factory.Factory):
    class Meta:
        model = ClassVolumes
        abstract = False

    volume_first_quadrimester = factory.fuzzy.FuzzyDecimal(low=1, high=60)
    volume_second_quadrimester = factory.fuzzy.FuzzyDecimal(low=1, high=60)


class _EffectiveClassIdentityFactory(factory.Factory):
    class Meta:
        model = EffectiveClassIdentity
        abstract = False

    class_code = factory.fuzzy.FuzzyText(length=1)
    learning_unit_identity = factory.SubFactory(_LearningUnitIdentityFactory)


class _EffectiveClassFactory(factory.Factory):
    class Meta:
        model = EffectiveClass
        abstract = False

    entity_id = factory.SubFactory(_EffectiveClassIdentityFactory)
    titles = factory.SubFactory(_ClassTitlesFactory)
    teaching_place = factory.SubFactory(_UclouvainCampusIdentityFactory)
    derogation_quadrimester = factory.fuzzy.FuzzyChoice(choices=DerogationQuadrimester)
    session_derogation = factory.fuzzy.FuzzyChoice(choices=DerogationSession)
    volumes = factory.SubFactory(_ClassVolumesFactory)


class _LecturingEffectiveClassFactory(_EffectiveClassFactory):
    class Meta:
        model = LecturingEffectiveClass
        abstract = False


class _PracticalEffectiveClassFactory(_EffectiveClassFactory):
    class Meta:
        model = PracticalEffectiveClass
        abstract = False


class LecturingEffectiveClassFactory(_LecturingEffectiveClassFactory):
    session_derogation = DerogationSession.DEROGATION_SESSION_1XX
    derogation_quadrimester = DerogationQuadrimester.Q1
    volumes = _ClassVolumesFactory(
        volume_first_quadrimester=1,
        volume_second_quadrimester=0
    )
