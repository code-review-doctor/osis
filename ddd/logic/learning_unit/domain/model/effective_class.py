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
from ddd.logic.learning_unit.commands import UpdateEffectiveClassCommand
from ddd.logic.learning_unit.domain.model._class_titles import ClassTitles
from ddd.logic.learning_unit.domain.model._volumes_repartition import ClassVolumes
from ddd.logic.learning_unit.domain.model.learning_unit import LearningUnitIdentity
from ddd.logic.learning_unit.domain.validator.validators_by_business_action import UpdateEffectiveClassValidatorList
from ddd.logic.shared_kernel.campus.domain.model.uclouvain_campus import UclouvainCampusIdentity
from osis_common.ddd import interface


class EffectiveClassCode(str):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert len(self) == 1


@attr.s(frozen=True, slots=True)
class EffectiveClassIdentity(interface.EntityIdentity):
    class_code = attr.ib(type=EffectiveClassCode)
    learning_unit_identity = attr.ib(type=LearningUnitIdentity)

    def __str__(self):
        return "{} - ({})".format(self.class_code, str(self.learning_unit_identity.academic_year))


@attr.s(slots=True, hash=False, eq=False)
class EffectiveClass(interface.RootEntity, abc.ABC):
    entity_id = attr.ib(type=EffectiveClassIdentity)
    titles = attr.ib(type=ClassTitles)
    teaching_place = attr.ib(type=UclouvainCampusIdentity)
    derogation_quadrimester = attr.ib(type=DerogationQuadrimester)
    session_derogation = attr.ib(type=DerogationSession)
    volumes = attr.ib(type=ClassVolumes)

    @property
    def complete_acronym(self):
        return "{}{}{}".format(
            self.entity_id.learning_unit_identity.code,
            '-' if isinstance(self, LecturingEffectiveClass) else '_',
            self.entity_id.class_code
        )

    def update(self, cmd: UpdateEffectiveClassCommand) -> None:
        UpdateEffectiveClassValidatorList(command=cmd).validate()
        self.entity_id.class_code = cmd.class_code
        self.titles.fr = cmd.title_fr
        self.titles.en = cmd.title_en
        self.teaching_place.uuid = cmd.teaching_place_uuid
        self.derogation_quadrimester.uuid = cmd.teaching_place_uuid
        quadri = cmd.derogation_quadrimester
        self.derogation_quadrimester = DerogationQuadrimester[quadri] if quadri else None
        self.session_derogation = DerogationSession[cmd.session_derogation] if cmd.session_derogation else None
        self.volumes.volume_first_quadrimester = cmd.volume_first_quadrimester
        self.volumes.volume_second_quadrimester = cmd.volume_second_quadrimester


class PracticalEffectiveClass(EffectiveClass):
    pass


class LecturingEffectiveClass(EffectiveClass):
    pass
