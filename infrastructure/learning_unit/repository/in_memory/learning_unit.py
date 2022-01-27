from typing import Optional, List, Set, Tuple

from base.ddd.utils.in_memory_repository import InMemoryGenericRepository
from ddd.logic.learning_unit.domain.model.learning_unit import LearningUnitIdentity, LearningUnit
from ddd.logic.learning_unit.dtos import LearningUnitSearchDTO
from ddd.logic.learning_unit.repository.i_learning_unit import ILearningUnitRepository


class LearningUnitRepository(InMemoryGenericRepository, ILearningUnitRepository):
    entities = list()  # type: List[LearningUnit]

    @classmethod
    def search(cls, entity_ids: Optional[List['LearningUnitIdentity']] = None, **kwargs) -> List['LearningUnit']:
        raise NotImplementedError

    @classmethod
    def search_learning_units_dto(
            cls,
            code_annee_values: Set[Tuple[str, int]] = None,
            code: str = None,
            annee_academique: int = None,
            intitule: str = None) -> List['LearningUnitSearchDTO']:
        if not code_annee_values and not code and annee_academique is None and not intitule:
            return []
        result = cls.entities
        if code_annee_values:
            result = [
                cls._convert_learning_unit_to_search_dto(entity)
                for entity in cls.entities
                if (entity.code, entity.year) in code_annee_values
            ]
        if code:
            result = [entity for entity in result if code in entity.code]
        if annee_academique:
            result = [entity for entity in result if entity.year == annee_academique]
        if intitule:
            result = [entity for entity in result if intitule in entity.complete_title_fr]
        return result

    @classmethod
    def _convert_learning_unit_to_search_dto(cls, learning_unit: 'LearningUnit') -> 'LearningUnitSearchDTO':
        return LearningUnitSearchDTO(
            year=learning_unit.year,
            code=learning_unit.code,
            full_title=learning_unit.complete_title_fr,
            type=learning_unit.type,
            responsible_entity_code=learning_unit.responsible_entity_identity.code,
            responsible_entity_title="",
            partims=learning_unit.get_partims_information(),
            quadrimester=learning_unit.derogation_quadrimester,
            credits=learning_unit.credits,
            lecturing_volume_annual=learning_unit.lecturing_part.volumes.volume_annual if
            learning_unit.has_lecturing_volume() else 0,
            practical_volume_annual=learning_unit.practical_part.volumes.volume_annual if
            learning_unit.has_practical_volume() else 0,
            session_derogation=learning_unit.derogation_session,
        )

    # TODO: To implement when Proposals are in DDD
    @classmethod
    def has_proposal_this_year_or_in_past(cls, learning_unit: 'LearningUnit') -> bool:
        return False

    # TODO: To implement when Enrollments are in DDD
    @classmethod
    def has_enrollments(cls, learning_unit: 'LearningUnit') -> bool:
        return False
