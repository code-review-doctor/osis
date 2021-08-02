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
from ddd.logic.learning_unit.domain.model._financial_volumes_repartition import DurationUnit
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
    volumes = attr.ib(type=ClassVolumes)
    derogation_quadrimester = attr.ib(type=DerogationQuadrimester, default=None)
    session_derogation = attr.ib(type=DerogationSession, default=None)

    def __str__(self):
        return "{} ({})".format(self.complete_acronym, self.entity_id.learning_unit_identity.academic_year)

    @property
    def class_code(self):
        return self.entity_id.class_code

    @property
    def learning_unit_identity(self):
        return self.entity_id.learning_unit_identity

    @property
    def complete_acronym(self) -> str:
        return "{}{}{}".format(
            self.learning_unit_code,
            '-' if isinstance(self, LecturingEffectiveClass) else '_',
            self.class_code
        )

    @property
    def learning_unit_code(self) -> str:
        return self.entity_id.learning_unit_identity.code

    @property
    def year(self) -> int:
        return self.entity_id.learning_unit_identity.academic_year.year

    def update(self, cmd: UpdateEffectiveClassCommand) -> None:
        UpdateEffectiveClassValidatorList(command=cmd).validate()
        self.titles = ClassTitles(fr=cmd.title_fr, en=cmd.title_en)
        self.teaching_place = UclouvainCampusIdentity(uuid=cmd.teaching_place_uuid)
        quadri = cmd.derogation_quadrimester
        self.derogation_quadrimester = DerogationQuadrimester[quadri] if quadri else None
        self.session_derogation = DerogationSession(cmd.session_derogation) if cmd.session_derogation else None
        self.volumes = ClassVolumes(
            volume_first_quadrimester=cmd.volume_first_quadrimester,
            volume_second_quadrimester=cmd.volume_second_quadrimester
        )

    def is_volume_first_quadrimester_greater_than(self, volume: DurationUnit) -> bool:
        return self.volumes.volume_first_quadrimester and self.volumes.volume_first_quadrimester > volume

    def is_volume_second_quadrimester_greater_than(self, volume: DurationUnit) -> bool:
        return self.volumes.volume_second_quadrimester and self.volumes.volume_second_quadrimester > volume

    @property
    def is_practical(self):
        return False

    @property
    def is_lecturing(self):
        return False


class PracticalEffectiveClass(EffectiveClass):

    @property
    def is_practical(self):
        return True


class LecturingEffectiveClass(EffectiveClass):

    @property
    def is_lecturing(self):
        return True
