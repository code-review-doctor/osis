import factory.fuzzy

from ddd.logic.learning_unit.tests.factory.learning_unit import _LanguageIdentityFactory
from ddd.logic.shared_kernel.language.domain.model.language import Language
import string


class _LanguageFactory(factory.Factory):
    class Meta:
        model = Language
        abstract = False

    entity_id = factory.SubFactory(_LanguageIdentityFactory)
    name = factory.fuzzy.FuzzyText(length=80, chars=string.digits)


class FRLanguageFactory(_LanguageFactory):
    entity_id = _LanguageIdentityFactory(
        code_iso="FR"
    )
