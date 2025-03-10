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
from decimal import Decimal
from typing import Set, Tuple

import attr

from ddd.logic.learning_unit.domain.model.responsible_entity import EntityCode
from osis_common.ddd import interface


@attr.s(frozen=True, slots=True)
class CreateLearningUnitCommand(interface.CommandRequest):
    code = attr.ib(type=str)
    academic_year = attr.ib(type=int)
    type = attr.ib(type=str)
    common_title_fr = attr.ib(type=str)
    specific_title_fr = attr.ib(type=str)
    common_title_en = attr.ib(type=str)
    specific_title_en = attr.ib(type=str)
    credits = attr.ib(type=int)
    internship_subtype = attr.ib(type=str)
    responsible_entity_code = attr.ib(type=EntityCode)
    periodicity = attr.ib(type=str)
    iso_code = attr.ib(type=str)
    remark_faculty = attr.ib(type=str)
    remark_publication_fr = attr.ib(type=str)
    remark_publication_en = attr.ib(type=str)

    # repartition_entity_2 = attr.ib(type=Optional[EntityCode])  # TODO :: to implement and unit test
    # repartition_entity_3 = attr.ib(type=Optional[EntityCode])  # TODO :: to implement and unit test

    practical_volume_q1 = attr.ib(type=Decimal)
    practical_volume_q2 = attr.ib(type=Decimal)
    practical_volume_annual = attr.ib(type=Decimal)
    # practical_volume_repartition_responsible_entity = attr.ib(type=Optional[Decimal])  # TODO :: implement + unit test
    # practical_volume_repartition_entity_2 = attr.ib(type=Optional[Decimal])  # TODO :: to implement and unit test
    # practical_volume_repartition_entity_3 = attr.ib(type=Optional[Decimal])  # TODO :: to implement and unit test

    lecturing_volume_q1 = attr.ib(type=Decimal)
    lecturing_volume_q2 = attr.ib(type=Decimal)
    lecturing_volume_annual = attr.ib(type=Decimal)
    # lecturing_volume_repartition_responsible_entity = attr.ib(type=Optional[Decimal])  # TODO :: implement + unit test
    # lecturing_volume_repartition_entity_2 = attr.ib(type=Optional[Decimal])  # TODO :: to implement and unit test
    # lecturing_volume_repartition_entity_3 = attr.ib(type=Optional[Decimal])  # TODO :: to implement and unit test

    derogation_quadrimester = attr.ib(type=str)
    teaching_place_uuid = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class CreatePartimCommand(interface.CommandRequest):
    learning_unit_code = attr.ib(type=str)
    learning_unit_year = attr.ib(type=int)
    subdivision = attr.ib(type=int)
    credits = attr.ib(type=int)
    periodicity = attr.ib(type=str)
    iso_code = attr.ib(type=str)
    title_fr = attr.ib(type=str, default="")
    title_en = attr.ib(type=str, default="")
    remark_faculty = attr.ib(type=str, default=None)
    remark_publication_fr = attr.ib(type=str, default=None)
    remark_publication_en = attr.ib(type=str, default=None)


@attr.s(frozen=True, slots=True)
class DeleteLearningUnitCommand(interface.CommandRequest):
    code = attr.ib(type=str)
    academic_year = attr.ib(type=int)


@attr.s(frozen=True, slots=True)
class CopyLearningUnitToNextYearCommand(interface.CommandRequest):
    copy_from_code = attr.ib(type=str)
    copy_from_year = attr.ib(type=int)


@attr.s(frozen=True, slots=True)
class CreateCommand(interface.CommandRequest):
    copy_from_code = attr.ib(type=str)
    copy_from_year = attr.ib(type=int)


@attr.s(frozen=True, slots=True)
class LearningUnitSearchCommand(interface.CommandRequest):
    code_annee_values = attr.ib(type=Set[Tuple[str, int]], default=None)
    annee_academique = attr.ib(type=int, default=None)
    code = attr.ib(type=str, default="")
    intitule = attr.ib(type=str, default="")


@attr.s(frozen=True, slots=True)
class CreateEffectiveClassCommand(interface.CommandRequest):
    class_code = attr.ib(type=str)
    learning_unit_code = attr.ib(type=str)
    year = attr.ib(type=int)
    teaching_place_uuid = attr.ib(type=str)
    title_fr = attr.ib(type=str, default="")
    title_en = attr.ib(type=str, default="")
    derogation_quadrimester = attr.ib(type=str, default=None)
    session_derogation = attr.ib(type=str, default=None)
    volume_first_quadrimester = attr.ib(type=float, default=None)
    volume_second_quadrimester = attr.ib(type=float, default=None)


@attr.s(frozen=True, slots=True)
class GetLearningUnitCommand(interface.CommandRequest):
    code = attr.ib(type=str)
    year = attr.ib(type=int)


@attr.s(frozen=True, slots=True)
class SearchDetailClassesEffectivesCommand(interface.CommandRequest):
    codes_classes = attr.ib(type=Set[str])
    annee = attr.ib(type=int)


@attr.s(frozen=True, slots=True)
class CanCreateEffectiveClassCommand(interface.CommandRequest):
    learning_unit_code = attr.ib(type=str)
    learning_unit_year = attr.ib(type=int)


@attr.s(frozen=True, slots=True)
class GetEffectiveClassCommand(interface.CommandRequest):
    class_code = attr.ib(type=str)
    learning_unit_code = attr.ib(type=str)
    learning_unit_year = attr.ib(type=int)


@attr.s(frozen=True, slots=True)
class GetClassesEffectivesDepuisUniteDEnseignementCommand(interface.CommandRequest):
    code_unite_enseignement = attr.ib(type=str)
    annee_unite_enseignement = attr.ib(type=int)


@attr.s(frozen=True, slots=True)
class GetEffectiveClassWarningsCommand(interface.CommandRequest):
    class_code = attr.ib(type=str)
    learning_unit_code = attr.ib(type=str)
    learning_unit_year = attr.ib(type=int)


@attr.s(frozen=True, slots=True)
class UpdateEffectiveClassCommand(interface.CommandRequest):
    class_code = attr.ib(type=str)
    learning_unit_code = attr.ib(type=str)
    year = attr.ib(type=int)
    teaching_place_uuid = attr.ib(type=str)
    title_fr = attr.ib(type=str, default="")
    title_en = attr.ib(type=str, default="")
    derogation_quadrimester = attr.ib(type=str, default=None)
    session_derogation = attr.ib(type=str, default=None)
    volume_first_quadrimester = attr.ib(type=float, default=None)
    volume_second_quadrimester = attr.ib(type=float, default=None)


@attr.s(frozen=True, slots=True)
class DeleteEffectiveClassCommand(interface.CommandRequest):
    class_code = attr.ib(type=str)
    learning_unit_code = attr.ib(type=str)
    year = attr.ib(type=int)


@attr.s(frozen=True, slots=True)
class CanDeleteEffectiveClassCommand(interface.CommandRequest):
    class_code = attr.ib(type=str)
    learning_unit_code = attr.ib(type=str)
    year = attr.ib(type=int)


@attr.s(frozen=True, slots=True)
class SearchTutorsDistributedToEffectiveClassCommand(interface.CommandRequest):
    class_code = attr.ib(type=str)
    learning_unit_code = attr.ib(type=str)
    year = attr.ib(type=int)
