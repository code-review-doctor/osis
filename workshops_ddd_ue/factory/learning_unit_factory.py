import abc
from typing import List

from osis_common.ddd.interface import CommandRequest
from workshops_ddd_ue.domain.learning_unit_year import LearningUnit
from workshops_ddd_ue.validators.validators_by_business_action import CopyLearningUnitToNextYearValidatorList


class Builder(abc.ABC):

    def build_from_command(self, cmd: CommandRequest):
        raise NotImplementedError()

    def build_from_database_model(self, django_model_object: django.db.models.Model):
        raise NotImplementedError()


class LearningUnitBuilder(Builder):
    def build_from_command(self, cmd: CommandRequest):
        pass

    def build_from_database_model(self, django_model_object: django.db.models.Model):
        pass

    @classmethod
    def copy_to_next_year(
            cls,
            learning_unit: 'LearningUnit',
            all_existing_learning_units: List['LearningUnit']
    ) -> 'LearningUnit':
        CopyLearningUnitToNextYearValidatorList(learning_unit.entity_id, all_existing_learning_units).validate()
        return ???
