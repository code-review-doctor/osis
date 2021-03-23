import abc
from typing import List

import attr

from osis_common.ddd.interface import CommandRequest, RootEntity
from workshops_ddd_ue.domain.learning_unit_year import LearningUnit, LearningUnitIdentity
from workshops_ddd_ue.factory.learning_unit_identity_factory import LearningUnitIdentityBuilder
from workshops_ddd_ue.validators.validators_by_business_action import CopyLearningUnitToNextYearValidatorList


# TODO :: to move into osis_common.ddd.interface
class RootEntityBuilder(abc.ABC):

    def build_from_command(self, cmd: CommandRequest) -> RootEntity:
        raise NotImplementedError()

    def build_from_database_model(self, django_model_object: 'django.db.models.Model') -> RootEntity:
        raise NotImplementedError()


class LearningUnitBuilder(RootEntityBuilder):

    @classmethod
    def copy_to_next_year(
            cls,
            learning_unit: 'LearningUnit',
            all_existing_lear_unit_identities: List['LearningUnitIdentity']
    ) -> 'LearningUnit':
        CopyLearningUnitToNextYearValidatorList(learning_unit.entity_id, all_existing_lear_unit_identities).validate()
        learning_unit_next_year = attr.evolve(
            learning_unit,
            entity_id=LearningUnitIdentityBuilder.build_for_next_year(learning_unit.entity_id)
        )
        return learning_unit_next_year
