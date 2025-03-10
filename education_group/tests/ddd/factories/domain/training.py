##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from typing import List

import factory.fuzzy

from base.models.enums.academic_type import AcademicTypes
from base.models.enums.activity_presence import ActivityPresence
from base.models.enums.decree_category import DecreeCategories
from base.models.enums.duration_unit import DurationUnitsEnum
from base.models.enums.education_group_types import TrainingType
from base.models.enums.internship_presence import InternshipPresence
from base.models.enums.rate_code import RateCode
from base.models.enums.schedule_type import ScheduleTypeEnum
from education_group.ddd import command
from ddd.logic.formation_catalogue.domain.model._first_year_bachelor import FirstYearBachelor, FirstYearBachelorIdentity
from ddd.logic.formation_catalogue.domain.model.bachelor import Bachelor
from education_group.ddd.domain.training import Training, TrainingIdentity, TrainingIdentityThroughYears
from education_group.ddd.repository import training as training_repository
from education_group.ddd.service.write import copy_training_service
from education_group.tests.ddd.factories.domain.campus import CampusFactory
from education_group.tests.ddd.factories.domain.co_graduation import CoGraduationFactory
from education_group.tests.ddd.factories.domain.diploma import DiplomaFactory
from education_group.tests.ddd.factories.domain.entity import EntityFactory
from education_group.tests.ddd.factories.domain.funding import FundingFactory
from education_group.tests.ddd.factories.domain.hops import HOPSFactory
from education_group.tests.ddd.factories.domain.isced_domain import IscedDomainFactory
from education_group.tests.ddd.factories.domain.language import LanguageFactory
from education_group.tests.ddd.factories.domain.study_domain import StudyDomainFactory
from education_group.tests.ddd.factories.domain.titles import TitlesFactory
from program_management.ddd.domain.node import NodeGroupYear


def generate_end_date(training):
    return training.entity_identity.year + 10


class TrainingIdentityFactory(factory.Factory):
    class Meta:
        model = TrainingIdentity
        abstract = False

    acronym = factory.Sequence(lambda n: 'ACRONYM%02d' % n)
    year = factory.fuzzy.FuzzyInteger(1999, 2099)


class TrainingIdentityThroughYearsFactory(factory.Factory):
    class Meta:
        model = TrainingIdentityThroughYears
        abstract = False

    uuid = factory.Sequence(lambda n: n + 1)


class TrainingFactory(factory.Factory):
    class Meta:
        model = Training
        abstract = False

    entity_identity = factory.SubFactory(TrainingIdentityFactory)
    code = factory.Sequence(lambda n: 'CODE%02d' % n)
    entity_id = factory.LazyAttribute(lambda o: o.entity_identity)
    identity_through_years = factory.SubFactory(TrainingIdentityThroughYearsFactory)
    type = factory.fuzzy.FuzzyChoice(TrainingType)
    credits = factory.fuzzy.FuzzyDecimal(0, 10, precision=1)
    schedule_type = factory.fuzzy.FuzzyChoice(ScheduleTypeEnum)
    duration = factory.fuzzy.FuzzyInteger(1, 5)
    start_year = factory.fuzzy.FuzzyInteger(1999, 2099)
    titles = factory.SubFactory(TitlesFactory)
    keywords = factory.fuzzy.FuzzyText()
    internship_presence = factory.fuzzy.FuzzyChoice(InternshipPresence)
    is_enrollment_enabled = True
    has_online_re_registration = True
    has_partial_deliberation = True
    has_admission_exam = True
    has_dissertation = True
    produce_university_certificate = True
    decree_category = factory.fuzzy.FuzzyChoice(DecreeCategories)
    rate_code = factory.fuzzy.FuzzyChoice(RateCode)
    main_language = factory.SubFactory(LanguageFactory)
    english_activities = factory.fuzzy.FuzzyChoice(ActivityPresence)
    other_language_activities = factory.fuzzy.FuzzyChoice(ActivityPresence)
    internal_comment = factory.fuzzy.FuzzyText()
    main_domain = factory.SubFactory(StudyDomainFactory)
    secondary_domains = None
    isced_domain = factory.SubFactory(IscedDomainFactory)
    management_entity = factory.SubFactory(EntityFactory)
    administration_entity = factory.SubFactory(EntityFactory)
    end_year = factory.LazyAttribute(generate_end_date)
    enrollment_campus = factory.SubFactory(CampusFactory)
    other_campus_activities = factory.fuzzy.FuzzyChoice(ActivityPresence)
    funding = factory.SubFactory(FundingFactory)
    hops = factory.SubFactory(HOPSFactory)
    co_graduation = factory.SubFactory(CoGraduationFactory)
    co_organizations = []
    academic_type = factory.fuzzy.FuzzyChoice(AcademicTypes)
    duration_unit = factory.fuzzy.FuzzyChoice(DurationUnitsEnum)
    diploma = factory.SubFactory(DiplomaFactory)

    @factory.post_generation
    def persist(obj, create, extracted, **kwargs):
        if extracted:
            training_repository.TrainingRepository.create(obj)

    @classmethod
    def multiple(cls, n, *args, **kwargs) -> List['Training']:
        first_training = cls(*args, **kwargs)  # type: Training

        result = [first_training]
        for year in range(first_training.year, first_training.year + n - 1):
            identity = copy_training_service.copy_training_to_next_year(
                command.CopyTrainingToNextYearCommand(acronym=first_training.acronym, postpone_from_year=year)
            )
            result.append(training_repository.TrainingRepository.get(identity))

        return result

    @classmethod
    def from_node(cls, node: 'NodeGroupYear') -> Training:
        return cls(
            code=node.code,
            type=node.node_type,
            entity_identity__acronym=node.title,
            entity_identity__year=node.year,
            start_year=node.start_year,
            end_year=node.end_date,
            management_entity__acronym=node.management_entity_acronym,
            credits=node.credits,
            schedule_type=node.schedule_type,
            titles__title_fr=node.offer_title_fr,
            titles__title_en=node.offer_title_en,
            titles__partial_title_fr=node.offer_partial_title_fr,
            titles__partial_title_en=node.offer_partial_title_en,
            status=node.offer_status
        )


class FirstYearBachelorIdentityFactory(factory.Factory):
    class Meta:
        model = FirstYearBachelorIdentity
        abstract = False


class FirstYearBachelorFactory(factory.Factory):
    class Meta:
        model = FirstYearBachelor
        abstract = False

    entity_id = factory.SubFactory(FirstYearBachelorIdentityFactory)
    administration_entity = factory.SubFactory(EntityFactory)


class BachelorFactory(TrainingFactory):
    class Meta:
        model = Bachelor
        abstract = False

    first_year_bachelor = factory.SubFactory(FirstYearBachelorFactory)
    type = TrainingType.BACHELOR
