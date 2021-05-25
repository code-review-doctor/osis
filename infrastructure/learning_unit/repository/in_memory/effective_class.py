from typing import Optional, List

from ddd.logic.learning_unit.builder.learning_unit_identity_builder import LearningUnitIdentityBuilder
from ddd.logic.learning_unit.domain.model.effective_class import EffectiveClass, EffectiveClassIdentity
from ddd.logic.learning_unit.repository.i_effective_class import IEffectiveClassRepository
from osis_common.ddd.interface import ApplicationService


class EffectiveClassRepository(IEffectiveClassRepository):
    effective_classes = list()

    @classmethod
    def get(cls, entity_id: EffectiveClassIdentity) -> EffectiveClass:
        for effective_class in cls.effective_classes:
            if effective_class.entity_id == entity_id:
                return effective_class
        return None

    @classmethod
    def search(cls, entity_ids: Optional[List[EffectiveClassIdentity]] = None, **kwargs) -> List[EffectiveClass]:
        pass

    @classmethod
    def delete(cls, entity_id: EffectiveClassIdentity, **kwargs: ApplicationService) -> None:
        pass

    @classmethod
    def save(cls, entity: EffectiveClass) -> None:
        pass

    @classmethod
    def get_all_identities(self) -> List['EffectiveClassIdentity']:
        return [effective_class.entity_id for effective_class in self.effective_classes]
