from typing import Optional, List

from ddd.logic.shared_kernel.campus.domain.model.uclouvain_campus import UclouvainCampusIdentity, UclouvainCampus
from ddd.logic.shared_kernel.campus.repository.i_uclouvain_campus import IUclouvainCampusRepository
from ddd.logic.shared_kernel.language.domain.model.language import LanguageIdentity, Language
from ddd.logic.shared_kernel.language.repository.i_language import ILanguageRepository
from osis_common.ddd.interface import ApplicationService


class UclouvainCampusRepository(IUclouvainCampusRepository):
    campus_list = list()

    @classmethod
    def get(cls, entity_id: UclouvainCampusIdentity) -> UclouvainCampus:
        for campus in cls.campus_list:
            if campus.entity_id == entity_id:
                return campus
        return None

    @classmethod
    def search(cls, entity_ids: Optional[List[UclouvainCampusIdentity]] = None, **kwargs) -> List[UclouvainCampus]:
        pass

    @classmethod
    def delete(cls, entity_id: UclouvainCampusIdentity, **kwargs: ApplicationService) -> None:
        pass

    @classmethod
    def save(cls, entity: UclouvainCampus) -> None:
        cls.campus_list.append(entity)
