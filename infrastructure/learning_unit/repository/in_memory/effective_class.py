from typing import List

from base.ddd.utils.in_memory_repository import InMemoryGenericRepository
from ddd.logic.learning_unit.domain.model.effective_class import EffectiveClass
from ddd.logic.learning_unit.repository.i_effective_class import IEffectiveClassRepository


class EffectiveClassRepository(InMemoryGenericRepository, IEffectiveClassRepository):
    entities = list()  # type: List[EffectiveClass]
