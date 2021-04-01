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
from typing import List

from base.ddd.utils.business_validator import MultipleBusinessExceptions
from base.models.enums.entity_type import EntityType
from ddd.logic.learning_unit.domain.model.responsible_entity import ResponsibleEntity
from osis_common.ddd import interface
from ddd.logic.learning_unit.builder.learning_unit_builder import LearningUnitBuilder
from ddd.logic.learning_unit.commands import CreateLearningUnitCommand
from ddd.logic.learning_unit.domain.validator.exceptions import InvalidResponsibleEntityTypeOrCodeException
from ddd.logic.learning_unit.domain.model.learning_unit import LearningUnitIdentity
from osis_common.ddd.interface import BusinessException


class CreateLearningUnit(interface.DomainService):

    @classmethod
    def create(
            cls,
            responsible_entity: 'ResponsibleEntity',
            cmd: 'CreateLearningUnitCommand',
            all_existing_identities: List['LearningUnitIdentity']
    ):
        # FIXME :: créer une fonction utilitaire pour exécuter chaque statement en try except
        #  pour lancer 1 seule MultipleBusinessExceptions
        #  et éviter de devoir ajouter manuellement les try-except comme ci-dessous
        exceptions = []
        try:
            cls._should_responsible_entity_have_authorized_type_or_code(responsible_entity)
        except BusinessException as e:
            exceptions.append(e)
        try:
            learning_unit = LearningUnitBuilder.build_from_command(
                cmd,
                all_existing_identities,
                responsible_entity.entity_id
            )
        except MultipleBusinessExceptions as e:
            raise MultipleBusinessExceptions(exceptions=e.exceptions | set(exceptions))
        return learning_unit

    @classmethod
    def _should_responsible_entity_have_authorized_type_or_code(cls, responsible_entity: 'ResponsibleEntity'):
        authorized_types = [
            EntityType.SECTOR,
            EntityType.FACULTY,
            EntityType.SCHOOL,
            EntityType.DOCTORAL_COMMISSION,
        ]
        authorized_codes = [
            "ILV",
            "IUFC",
            "CCR",
            "LLL",
        ]
        if not(responsible_entity.type in authorized_types or responsible_entity.code in authorized_codes):
            raise InvalidResponsibleEntityTypeOrCodeException(
                authorized_types=authorized_types,
                authorized_codes=authorized_codes
            )
