import factory.fuzzy

from ddd.logic.learning_unit.tests.factory.learning_unit import _LanguageIdentityFactory, \
    _UclouvainCampusIdentityFactory
from ddd.logic.shared_kernel.campus.domain.model.uclouvain_campus import UclouvainCampus
from ddd.logic.shared_kernel.language.domain.model.language import Language
import string


class _CampusFactory(factory.Factory):
    class Meta:
        model = UclouvainCampus
        abstract = False

    entity_id = factory.SubFactory(_UclouvainCampusIdentityFactory)
    name = factory.fuzzy.FuzzyText(length=100, chars=string.digits)
    organization_name = factory.fuzzy.FuzzyText(length=255, chars=string.digits)


class UCLCampusFactory(_CampusFactory):
    entity_id = _UclouvainCampusIdentityFactory(
        uuid="123"
    )
