import factory.fuzzy

from base.models.enums.learning_unit_year_session import DerogationSession
from base.models.enums.quadrimesters import DerogationQuadrimester
from ddd.logic.learning_unit.domain.model._class_titles import ClassTitles
from ddd.logic.learning_unit.domain.model._volumes_repartition import ClassVolumes
from ddd.logic.learning_unit.domain.model.effective_class import EffectiveClassIdentity, EffectiveClass
from ddd.logic.learning_unit.tests.factory.learning_unit import _LearningUnitIdentityFactory
from ddd.logic.shared_kernel.campus.domain.model.uclouvain_campus import UclouvainCampusIdentity


class _EffectiveClassIdentityFactory(factory.Factory):
    class Meta:
        model = EffectiveClassIdentity
        abstract = False

    class_code = factory.fuzzy.FuzzyText(length=1)
    learning_unit_identity = factory.SubFactory(_LearningUnitIdentityFactory)


class _EffectiveClassFactory(factory.Factory):
    class Meta:
        model = EffectiveClass
        abstract = False

    entity_id = factory.SubFactory(_EffectiveClassIdentityFactory)
    titles = ClassTitles(
        fr="Intitulé en français de la classe effective",
        en="English title",
    )
    teaching_place = UclouvainCampusIdentity(uuid='33afea7a-9e80-4384-86df-392e3fb171c6')
    volumes = ClassVolumes(
        volume_first_quadrimester=10.0,
        volume_second_quadrimester=10.0,
    )
    derogation_quadrimester = factory.fuzzy.FuzzyChoice(DerogationQuadrimester)
    session_derogation = factory.fuzzy.FuzzyChoice(DerogationSession)


class LecturingEffectiveClassFactory(_EffectiveClassFactory):
    pass


class PracticalEffectiveClassFactory(_EffectiveClassFactory):
    pass
