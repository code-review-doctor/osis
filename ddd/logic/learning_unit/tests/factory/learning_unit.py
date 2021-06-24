import datetime

import factory.fuzzy
import uuid

from base.models.enums.internship_subtypes import InternshipSubtype
from base.models.enums.learning_unit_year_periodicity import PeriodicityEnum
from base.models.enums.learning_unit_year_session import DerogationSession
from base.models.enums.quadrimesters import DerogationQuadrimester
from ddd.logic.learning_unit.domain.model._financial_volumes_repartition import FinancialVolumesRepartition
from ddd.logic.learning_unit.domain.model._partim import Partim, PartimIdentity
from ddd.logic.learning_unit.domain.model._remarks import Remarks
from ddd.logic.learning_unit.domain.model._titles import Titles
from ddd.logic.learning_unit.domain.model._volumes_repartition import LecturingPart, Volumes, PracticalPart
from ddd.logic.learning_unit.domain.model.learning_unit import LearningUnit, LearningUnitIdentity, CourseLearningUnit, \
    ExternalLearningUnit
from ddd.logic.learning_unit.tests.factory.ucl_entity import UclEntityIdentityFactory, DRTEntityFactory
from ddd.logic.shared_kernel.academic_year.domain.model.academic_year import AcademicYearIdentity
from ddd.logic.shared_kernel.campus.domain.model.uclouvain_campus import UclouvainCampusIdentity
from ddd.logic.shared_kernel.language.domain.model.language import LanguageIdentity


class _AcademicYearIdentityFactory(factory.Factory):
    class Meta:
        model = AcademicYearIdentity
        abstract = False

    year = factory.fuzzy.FuzzyInteger(low=1999, high=2099)


class _LanguageIdentityFactory(factory.Factory):
    class Meta:
        model = LanguageIdentity
        abstract = False

    code_iso = 'fr_BE'


class _UclouvainCampusIdentityFactory(factory.Factory):
    class Meta:
        model = UclouvainCampusIdentity

    uuid = uuid.uuid4()


class _TitlesFactory(factory.Factory):
    class Meta:
        model = Titles
        abstract = False

    common_fr = factory.fuzzy.FuzzyText(length=240)
    specific_fr = factory.fuzzy.FuzzyText(length=240)
    common_en = factory.fuzzy.FuzzyText(length=240)
    specific_en = factory.fuzzy.FuzzyText(length=240)


class _RemarksFactory(factory.Factory):
    class Meta:
        model = Remarks
        abstract = False

    faculty = factory.fuzzy.FuzzyText(length=240)
    publication_fr = factory.fuzzy.FuzzyText(length=240)
    publication_en = factory.fuzzy.FuzzyText(length=240)


class _PartimIdentityFactory(factory.Factory):
    class Meta:
        model = PartimIdentity
        abstract = False

    subdivision = factory.fuzzy.FuzzyText(length=10)


class _PartimFactory(factory.Factory):
    class Meta:
        model = Partim
        abstract = False

    entity_id = factory.SubFactory(_PartimIdentityFactory)
    title_fr = factory.fuzzy.FuzzyText(length=240)
    title_en = factory.fuzzy.FuzzyText(length=240)
    credits = factory.fuzzy.FuzzyInteger(low=1, high=180)
    periodicity = factory.fuzzy.FuzzyChoice(PeriodicityEnum)
    language_id = factory.SubFactory(_LanguageIdentityFactory)
    remarks = factory.SubFactory(_RemarksFactory)


class _FinancialVolumesRepartitionFactory(factory.Factory):
    class Meta:
        model = FinancialVolumesRepartition
        abstract = False

    responsible_entity = factory.SubFactory(UclEntityIdentityFactory)
    entity_2 = factory.SubFactory(UclEntityIdentityFactory)
    entity_3 = factory.SubFactory(UclEntityIdentityFactory)
    repartition_volume_responsible_entity = factory.fuzzy.FuzzyDecimal
    repartition_volume_entity_2 = factory.fuzzy.FuzzyDecimal
    repartition_volume_entity_3 = factory.fuzzy.FuzzyDecimal


class _VolumesFactory(factory.Factory):
    class Meta:
        model = Volumes
        abstract = False

    volume_first_quadrimester = factory.fuzzy.FuzzyDecimal(low=1, high=60)
    volume_second_quadrimester = factory.fuzzy.FuzzyDecimal(low=1, high=60)
    volume_annual = factory.LazyAttribute(lambda o: o.volume_first_quadrimester + o.volume_second_quadrimester)
    planned_classes = factory.fuzzy.FuzzyInteger(low=0, high=10)
    volumes_repartition = factory.SubFactory(_FinancialVolumesRepartitionFactory)


class _LecturingPartFactory(factory.Factory):
    class Meta:
        model = LecturingPart
        abstract = False

    volumes = factory.SubFactory(_VolumesFactory)


class _PracticalPartFactory(factory.Factory):
    class Meta:
        model = PracticalPart
        abstract = False

    volumes = factory.SubFactory(_VolumesFactory)


class LearningUnitIdentityFactory(factory.Factory):
    class Meta:
        model = LearningUnitIdentity
        abstract = False

    academic_year = factory.SubFactory(_AcademicYearIdentityFactory)
    code = factory.Sequence(lambda n: 'LFAC1%03d' % n)


class _LearningUnitFactory(factory.Factory):
    class Meta:
        model = LearningUnit
        abstract = False

    entity_id = factory.SubFactory(LearningUnitIdentityFactory)
    titles = factory.SubFactory(_TitlesFactory)
    credits = factory.fuzzy.FuzzyInteger(low=1, high=180)
    internship_subtype = factory.fuzzy.FuzzyChoice(InternshipSubtype)

    responsible_entity_identity = factory.SubFactory(UclEntityIdentityFactory)
    attribution_entity_identity = factory.SubFactory(UclEntityIdentityFactory)

    periodicity = factory.fuzzy.FuzzyChoice(PeriodicityEnum)
    language_id = factory.SubFactory(_LanguageIdentityFactory)
    remarks = factory.SubFactory(_RemarksFactory)
    partims = factory.List([factory.SubFactory(_PartimFactory)])

    derogation_quadrimester = factory.fuzzy.FuzzyChoice(DerogationQuadrimester)
    derogation_session = factory.fuzzy.FuzzyChoice(DerogationSession)

    lecturing_part = factory.SubFactory(_LecturingPartFactory)
    practical_part = factory.SubFactory(_PracticalPartFactory)

    teaching_place = factory.SubFactory(_UclouvainCampusIdentityFactory)

    professional_integration = True
    is_active = True


class _CourseLearningUnitFactory(_LearningUnitFactory):
    class Meta:
        model = CourseLearningUnit
        abstract = False


class _ExternalLearningUnitFactory(_LearningUnitFactory):
    class Meta:
        model = ExternalLearningUnit
        abstract = False


class LDROI1001LearningUnitIdentityFactory(LearningUnitIdentityFactory):
    code = "LDROI1001"
    academic_year = _AcademicYearIdentityFactory(year=datetime.datetime.now().year)


class LDROI1001CourseLearningUnitFactory(_CourseLearningUnitFactory):
    entity_id = LDROI1001LearningUnitIdentityFactory
    titles = _TitlesFactory(
        common_fr="Introduction au droit",
        specific_fr="Partie 1 : droit civil",
        common_en="Introduction to law",
        specific_en="Part 1 : civic law"
    )
    credits = 7
    internship_subtype = None
    responsible_entity_identity = DRTEntityFactory().entity_id
    periodicity = PeriodicityEnum.ANNUAL.name

    partims = []

    remarks = _RemarksFactory(
        faculty="Remark fac",
        publication_fr="Remarqué publiée sur le portail",
        publication_en="Remark published"
    )

    derogation_quadrimester = DerogationQuadrimester.Q1and2.name

    lecturing_part = _LecturingPartFactory(
        volumes=_VolumesFactory(
            volume_first_quadrimester=5.0,
            volume_second_quadrimester=15.0,
            volume_annual=20.0
        )
    )

    practical_part = _PracticalPartFactory(
        volumes=_VolumesFactory(
            volume_first_quadrimester=25.0,
            volume_second_quadrimester=35.0,
            volume_annual=60.0
        )
    )


class LDROI1002ExternalLearningUnitFactory(_ExternalLearningUnitFactory):
    entity_id = LearningUnitIdentityFactory(
        code="LDROI1002",
        academic_year=_AcademicYearIdentityFactory(year=datetime.datetime.now().year)
    )
    partims = []


class LDROI1003CourseWithPartimsLearningUnitFactory(_CourseLearningUnitFactory):
    entity_id = LearningUnitIdentityFactory(
        code="LDROI1003",
        academic_year=_AcademicYearIdentityFactory(year=datetime.datetime.now().year)
    )
    partims = [_PartimFactory()]


class LDROI1004CourseWithoutVolumesLearningUnitFactory(_CourseLearningUnitFactory):
    entity_id = LearningUnitIdentityFactory(
        code="LDROI1004",
        academic_year=_AcademicYearIdentityFactory(year=datetime.datetime.now().year)
    )
    lecturing_part = None
    practical_part = None
