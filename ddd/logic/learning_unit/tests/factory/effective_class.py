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
from ddd.logic.learning_unit.domain.model.effective_class import EffectiveClassIdentity, EffectiveClass
from ddd.logic.learning_unit.tests.factory.learning_unit import LearningUnitIdentityFactory, \
    LDROI1001LearningUnitIdentityFactory
from ddd.logic.shared_kernel.campus.domain.model.uclouvain_campus import UclouvainCampusIdentity


class EffectiveClassIdentityFactory(factory.Factory):
    class Meta:
        model = EffectiveClassIdentity
        abstract = False

    class_code = factory.fuzzy.FuzzyText(length=1)
    learning_unit_identity = factory.SubFactory(LearningUnitIdentityFactory)


class _EffectiveClassFactory(factory.Factory):
    class Meta:
        model = EffectiveClass
        abstract = False

    entity_id = factory.SubFactory(EffectiveClassIdentityFactory)
    titles = ClassTitles(
        fr="Intitulé en français de la classe effective",
        en="English title",
    )
    teaching_place = UclouvainCampusIdentity(uuid='33afea7a-9e80-4384-86df-392e3fb171c6')
    volumes = ClassVolumes(
        volume_first_quadrimester=10.0,
        volume_second_quadrimester=10.0,
    )
    derogation_quadrimester = factory.fuzzy.FuzzyChoice(DerogationQuadrimester)
    session_derogation = factory.fuzzy.FuzzyChoice(DerogationSession)


class LecturingEffectiveClassFactory(_EffectiveClassFactory):
    pass


class PracticalEffectiveClassFactory(_EffectiveClassFactory):
    pass


class LDROI1001XEffectiveClassIdentityFactory(EffectiveClassIdentityFactory):
    class_code = 'X'
    learning_unit_identity = factory.SubFactory(LDROI1001LearningUnitIdentityFactory)
