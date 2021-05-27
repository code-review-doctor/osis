##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2021 Université catholique de Louvain (http://www.uclouvain.be)
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
from collections import namedtuple
from decimal import Decimal
from typing import Optional, List

import attr

from osis_common.ddd.interface import DTO

_SecondaryDomainDTO = namedtuple(
    'SecondaryDomainDTO',
    'decree_name code name'
)
_CoorganizationDTO = namedtuple(
    'CoorganizationDTO',
    'name organization_name country city logo_url all_students enrollment_place diploma is_producing_certificate '
    'is_producing_annexe'
)
_CertificateAimDTO = namedtuple(
    'CertificateAimDTO',
    'section code description'
)


@attr.s(frozen=True, slots=True)
class TrainingDto(DTO):
    acronym = attr.ib(type=str)
    year = attr.ib(type=int)
    code = attr.ib(type=str)
    uuid = attr.ib(type=str)
    type = attr.ib(type=str)
    credits = attr.ib(type=Decimal)
    schedule_type = attr.ib(type=str)
    duration = attr.ib(type=str)
    start_year = attr.ib(type=int)
    title_fr = attr.ib(type=str)
    partial_title_fr = attr.ib(type=str)
    title_en = attr.ib(type=str)
    partial_title_en = attr.ib(type=str)
    status = attr.ib(type=str)
    keywords = attr.ib(type=str)
    internship_presence = attr.ib(type=str)
    is_enrollment_enabled = attr.ib(type=str)
    has_online_re_registration = attr.ib(type=str)
    has_partial_deliberation = attr.ib(type=str)
    has_admission_exam = attr.ib(type=str)
    has_dissertation = attr.ib(type=str)
    produce_university_certificate = attr.ib(type=str)
    decree_category = attr.ib(type=str)
    rate_code = attr.ib(type=str)
    main_language_name = attr.ib(type=str)
    english_activities = attr.ib(type=str)
    other_language_activities = attr.ib(type=str)
    internal_comment = attr.ib(type=str)
    main_domain_decree_name = attr.ib(type=str)
    main_domain_code = attr.ib(type=str)
    main_domain_name = attr.ib(type=str)
    secondary_domains = attr.ib(type=List[_SecondaryDomainDTO])
    isced_domain_code = attr.ib(type=str)
    isced_domain_title_fr = attr.ib(type=str)
    isced_domain_title_en = attr.ib(type=str)
    management_entity_acronym = attr.ib(type=str)
    administration_entity_acronym = attr.ib(type=str)
    end_year = attr.ib(type=Optional[int])
    enrollment_campus_name = attr.ib(type=str)
    enrollment_campus_university_name = attr.ib(type=str)
    other_campus_activities = attr.ib(type=str)
    funding_can_be_funded = attr.ib(type=str)
    funding_orientation = attr.ib(type=str)
    funding_can_be_international_funded = attr.ib(type=str)
    funding_international_funding_orientation = attr.ib(type=str)
    ares_code = attr.ib(type=str)
    ares_graca = attr.ib(type=str)
    ares_authorization = attr.ib(type=str)
    co_graduation_code_inter_cfb = attr.ib(type=str)
    co_graduation_coefficient = attr.ib(type=str)
    co_organizations = attr.ib(type=List[_CoorganizationDTO])
    academic_type = attr.ib(type=str)
    duration_unit = attr.ib(type=str)
    diploma_leads_to_diploma = attr.ib(type=str)
    diploma_printing_title = attr.ib(type=str)
    diploma_professional_title = attr.ib(type=str)
    diploma_aims = attr.ib(type=List[_CertificateAimDTO])


@attr.s(frozen=True, slots=True)
class BachelorDto(TrainingDto):
    first_year_bachelor_administration_entity_acronym = attr.ib(type=Optional[str])
