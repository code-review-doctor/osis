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
import abc

import attr

from base.models.enums.learning_unit_year_session import DerogationSession
from base.models.enums.quadrimesters import DerogationQuadrimester
from ddd.logic.learning_unit.domain.model._campus import TeachingPlace
from ddd.logic.learning_unit.domain.model._class_titles import ClassTitles
from ddd.logic.learning_unit.domain.model._volumes_repartition import Volumes
from ddd.logic.learning_unit.domain.model.learning_unit import LearningUnitIdentity
from osis_common.ddd import interface


class EffectiveClassCode(str):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert len(self) == 1


class EffectiveClassIdentity(interface.EntityIdentity):
    class_code = attr.ib(type=EffectiveClassCode)
    learning_unit_identity = attr.ib(type=LearningUnitIdentity)


@attr.s(slots=True, hash=False, eq=False)
class EffectiveClass(interface.RootEntity, abc.ABC):
    entity_id = attr.ib(type=EffectiveClassIdentity)
    titles = attr.ib(type=ClassTitles)
    teaching_place = attr.ib(type=TeachingPlace)
    derogation_quadrimester = attr.ib(type=DerogationQuadrimester)
    session_derogation = attr.ib(type=DerogationSession)
    volumes = attr.ib(type=Volumes)


class PracticalEffectiveClass(EffectiveClass):
    pass


class LecturingEffectiveClass(EffectiveClass):
    pass
