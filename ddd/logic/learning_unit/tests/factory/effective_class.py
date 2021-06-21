import factory.fuzzy

from base.models.enums.learning_unit_year_session import DerogationSession
from base.models.enums.quadrimesters import DerogationQuadrimester
from ddd.logic.learning_unit.domain.model._class_titles import ClassTitles
from ddd.logic.learning_unit.domain.model._volumes_repartition import ClassVolumes
from ddd.logic.learning_unit.domain.model.effective_class import EffectiveClass, EffectiveClassIdentity, \
    LecturingEffectiveClass, PracticalEffectiveClass
from ddd.logic.learning_unit.tests.factory.learning_unit import _LearningUnitIdentityFactory, \
    _UclouvainCampusIdentityFactory


class _ClassTitlesFactory(factory.Factory):
    class Meta:
        model = ClassTitles
        abstract = False

    fr = factory.fuzzy.FuzzyText(length=240)
    en = factory.fuzzy.FuzzyText(length=240)


class _ClassVolumesFactory(factory.Factory):
    class Meta:
        model = ClassVolumes
        abstract = False

    volume_first_quadrimester = factory.fuzzy.FuzzyDecimal(low=1, high=60)
    volume_second_quadrimester = factory.fuzzy.FuzzyDecimal(low=1, high=60)


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
    titles = factory.SubFactory(_ClassTitlesFactory)
    teaching_place = factory.SubFactory(_UclouvainCampusIdentityFactory)
    derogation_quadrimester = factory.fuzzy.FuzzyChoice(choices=DerogationQuadrimester)
    session_derogation = factory.fuzzy.FuzzyChoice(choices=DerogationSession)
    volumes = factory.SubFactory(_ClassVolumesFactory)


class _LecturingEffectiveClassFactory(_EffectiveClassFactory):
    class Meta:
        model = LecturingEffectiveClass
        abstract = False


class _PracticalEffectiveClassFactory(_EffectiveClassFactory):
    class Meta:
        model = PracticalEffectiveClass
        abstract = False


class LecturingEffectiveClassFactory(_LecturingEffectiveClassFactory):
    session_derogation = DerogationSession.DEROGATION_SESSION_1XX
    derogation_quadrimester = DerogationQuadrimester.Q1
    volumes = _ClassVolumesFactory(
        volume_first_quadrimester=1,
        volume_second_quadrimester=0
    )
