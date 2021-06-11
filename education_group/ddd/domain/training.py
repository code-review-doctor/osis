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

import attr

from base.ddd.utils.converters import to_upper_case_converter
from base.models.enums.academic_type import AcademicTypes
from base.models.enums.active_status import ActiveStatusEnum
from base.models.enums.activity_presence import ActivityPresence
from base.models.enums.decree_category import DecreeCategories
from base.models.enums.duration_unit import DurationUnitsEnum
from base.models.enums.education_group_types import TrainingType
from base.models.enums.internship_presence import InternshipPresence
from base.models.enums.rate_code import RateCode
from base.models.enums.schedule_type import ScheduleTypeEnum
from education_group.ddd.domain._campus import Campus
from education_group.ddd.domain._co_graduation import CoGraduation
from education_group.ddd.domain._co_organization import Coorganization
from education_group.ddd.domain._diploma import Diploma
from education_group.ddd.domain._entity import Entity
from education_group.ddd.domain._funding import Funding
from education_group.ddd.domain._hops import HOPS
from education_group.ddd.domain._isced_domain import IscedDomain
from education_group.ddd.domain._language import Language
from education_group.ddd.domain._study_domain import StudyDomain
from education_group.ddd.domain._titles import Titles
from education_group.ddd.validators import validators_by_business_action
from osis_common.ddd import interface
from program_management.ddd.domain.academic_year import AcademicYear


@attr.s(frozen=True, slots=True)
class TrainingIdentity(interface.EntityIdentity):
    acronym = attr.ib(type=str, converter=to_upper_case_converter)
    year = attr.ib(type=int)


@attr.s(frozen=True, slots=True)
class TrainingIdentityThroughYears(interface.ValueObject):
    uuid = attr.ib(type=int)


@attr.s(slots=True)
class Training(interface.RootEntity):

    # FIXME :: split fields into separate ValueObjects (to discuss with business people)
    entity_id = entity_identity = attr.ib(type=TrainingIdentity)
    code = attr.ib(type=str, converter=to_upper_case_converter)  # to remove
    type = attr.ib(type=TrainingType)
    credits = attr.ib(type=int)
    start_year = attr.ib(type=int)
    titles = attr.ib(type=Titles)
    status = attr.ib(type=ActiveStatusEnum, default=ActiveStatusEnum.ACTIVE)
    identity_through_years = attr.ib(type=TrainingIdentityThroughYears, default=None)
    schedule_type = attr.ib(type=ScheduleTypeEnum, default=ScheduleTypeEnum.DAILY)
    duration = attr.ib(type=int, default=1)
    duration_unit = attr.ib(type=DurationUnitsEnum, default=DurationUnitsEnum.QUADRIMESTER)
    keywords = attr.ib(type=str, default="")
    internship_presence = attr.ib(type=InternshipPresence, default=InternshipPresence.NO)
    is_enrollment_enabled = attr.ib(type=bool, default=True)
    has_online_re_registration = attr.ib(type=bool, default=True)
    has_partial_deliberation = attr.ib(type=bool, default=False)
    has_admission_exam = attr.ib(type=bool, default=False)
    has_dissertation = attr.ib(type=bool, default=False)
    produce_university_certificate = attr.ib(type=bool, default=False)
    decree_category = attr.ib(type=DecreeCategories, default=None)
    rate_code = attr.ib(type=RateCode, default=None)
    main_language = attr.ib(type=Language, default=None)
    english_activities = attr.ib(type=ActivityPresence, default=None)
    other_language_activities = attr.ib(type=ActivityPresence, default=None)
    internal_comment = attr.ib(type=str, default=None)
    main_domain = attr.ib(type=StudyDomain, default=None)
    secondary_domains = attr.ib(type=List[StudyDomain], default=[])
    isced_domain = attr.ib(type=IscedDomain, default=None)
    management_entity = attr.ib(type=Entity, default=None)
    administration_entity = attr.ib(type=Entity, default=None)
    end_year = attr.ib(type=int, default=None)
    enrollment_campus = attr.ib(type=Campus, default=None)
    other_campus_activities = attr.ib(type=ActivityPresence, default=None)
    funding = attr.ib(type=Funding, default=None)
    hops = attr.ib(type=HOPS, default=None)
    co_graduation = attr.ib(type=CoGraduation, default=None)
    co_organizations = attr.ib(type=List[Coorganization], factory=list)
    academic_type = attr.ib(type=AcademicTypes, default=None)
    diploma = attr.ib(type=Diploma, default=None)

    @property
    def acronym(self) -> str:
        return self.entity_id.acronym

    @property
    def year(self) -> int:
        return self.entity_id.year

    @property
    def academic_year(self) -> AcademicYear:
        return AcademicYear(self.year)

    def is_finality(self) -> bool:
        return self.type in set(TrainingType.finality_types_enum())

    def is_bachelor(self) -> bool:
        return self.type == TrainingType.BACHELOR

    def is_master_specialized(self):
        return self.type == TrainingType.MASTER_MC

    def is_aggregation(self):
        return self.type == TrainingType.AGGREGATION

    def is_master_60_credits(self):
        return self.type == TrainingType.MASTER_M1

    def is_master_120_credits(self):
        return self.type == TrainingType.PGRM_MASTER_120

    def is_master_180_240_credits(self):
        return self.type == TrainingType.PGRM_MASTER_180_240

    def update(self, data: 'UpdateTrainingData'):
        data_as_dict = attr.asdict(data, recurse=False)
        for field, new_value in data_as_dict.items():
            setattr(self, field, new_value)
        validators_by_business_action.UpdateTrainingValidatorList(self).validate()
        return self

    def update_from_other_training(self, other_training: 'Training'):
        fields_not_to_update = (
            "year", "acronym", "academic_year", "entity_id", "entity_identity", "identity_through_years",
            "co_organizations"
        )
        for field in other_training.__slots__:
            if field in fields_not_to_update:
                continue
            value = getattr(other_training, field)
            setattr(self, field, value)

    def update_aims(self, data: 'UpdateDiplomaData'):
        self._update_aims(data.diploma)
        validators = validators_by_business_action.UpdateCertificateAimsValidatorList(self)
        validators.validate()

    def update_aims_from_other_training(self, other_training: 'Training'):
        self._update_aims(other_training.diploma)

    def _update_aims(self, diploma: Diploma):
        if self.diploma:
            self.diploma = attr.evolve(self.diploma, aims=diploma.aims if diploma else [])

    def has_same_values_as(self, other_training: 'Training') -> bool:
        return not bool(self.get_conflicted_fields(other_training))

    def get_conflicted_fields(self, other_training: 'Training') -> List[str]:
        fields_not_to_compare = ("year", "entity_id", "entity_identity", "identity_through_years", "diploma",
                                 "co_organizations")
        conflicted_fields = []
        for field_name in other_training.__slots__:
            if field_name in fields_not_to_compare:
                continue
            if getattr(self, field_name) != getattr(other_training, field_name):
                conflicted_fields.append(field_name)
        conflicted_fields.extend(self._get_diploma_conflicted_fields(other_training))
        return conflicted_fields

    def _get_diploma_conflicted_fields(self, other: 'Training'):
        self_diploma = self.diploma or Diploma()
        other_diploma = other.diploma or Diploma()

        conflicted_fields = list()

        if self_diploma.printing_title != other_diploma.printing_title:
            conflicted_fields.append("printing_title")
        if self_diploma.leads_to_diploma != other_diploma.leads_to_diploma:
            conflicted_fields.append("leads_to_diploma")
        if self_diploma.professional_title != other_diploma.professional_title:
            conflicted_fields.append("professional_title")

        return conflicted_fields

    def has_conflicted_certificate_aims(self, other: 'Training'):
        return self.diploma.aims != other.diploma.aims


@attr.s(frozen=True, slots=True, kw_only=True)
class UpdateTrainingData:
    credits = attr.ib(type=int)
    titles = attr.ib(type=Titles)
    status = attr.ib(type=ActiveStatusEnum, default=ActiveStatusEnum.ACTIVE)
    duration = attr.ib(type=int, default=1)
    duration_unit = attr.ib(type=DurationUnitsEnum, default=DurationUnitsEnum.QUADRIMESTER)
    keywords = attr.ib(type=str, default="")
    internship_presence = attr.ib(type=InternshipPresence, default=InternshipPresence.NO)
    schedule_type = attr.ib(type=ScheduleTypeEnum, default=ScheduleTypeEnum.DAILY)
    is_enrollment_enabled = attr.ib(type=bool, default=True)
    has_online_re_registration = attr.ib(type=bool, default=True)
    has_partial_deliberation = attr.ib(type=bool, default=False)
    has_admission_exam = attr.ib(type=bool, default=False)
    has_dissertation = attr.ib(type=bool, default=False)
    produce_university_certificate = attr.ib(type=bool, default=False)
    main_language = attr.ib(type=Language, default=None)
    english_activities = attr.ib(type=ActivityPresence, default=None)
    other_language_activities = attr.ib(type=ActivityPresence, default=None)
    internal_comment = attr.ib(type=str, default=None)
    main_domain = attr.ib(type=StudyDomain, default=None)
    secondary_domains = attr.ib(type=List[StudyDomain], default=[])
    isced_domain = attr.ib(type=IscedDomain, default=None)
    management_entity = attr.ib(type=Entity, default=None)
    administration_entity = attr.ib(type=Entity, default=None)
    end_year = attr.ib(type=int, default=None)
    teaching_campus = attr.ib(type=Campus, default=None)
    enrollment_campus = attr.ib(type=Campus, default=None)
    other_campus_activities = attr.ib(type=ActivityPresence, default=None)
    funding = attr.ib(type=Funding, default=None)
    hops = attr.ib(type=HOPS, default=None)
    co_graduation = attr.ib(type=CoGraduation, default=None)
    diploma = attr.ib(type=Diploma, default=None)
    decree_category = attr.ib(type=DecreeCategories, default=None)
    rate_code = attr.ib(type=RateCode, default=None)


@attr.s(frozen=True, slots=True, kw_only=True)
class UpdateDiplomaData:
    diploma = attr.ib(type=Diploma, default=None)
