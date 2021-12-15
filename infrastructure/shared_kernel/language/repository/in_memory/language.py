from typing import Optional, List

from ddd.logic.shared_kernel.language.domain.model.language import LanguageIdentity, Language
from ddd.logic.shared_kernel.language.repository.i_language import ILanguageRepository
from osis_common.ddd.interface import ApplicationService


class LanguageRepository(ILanguageRepository):
    languages = list()

    @classmethod
    def get(cls, entity_id: LanguageIdentity) -> Language:
        for language in cls.languages:
            if language.entity_id == entity_id:
                return language
        return None

    @classmethod
    def search(cls, entity_ids: Optional[List[LanguageIdentity]] = None, **kwargs) -> List[Language]:
        pass

    @classmethod
    def delete(cls, entity_id: LanguageIdentity, **kwargs: ApplicationService) -> None:
        pass

    @classmethod
    def save(cls, entity: Language) -> None:
        cls.languages.append(entity)
