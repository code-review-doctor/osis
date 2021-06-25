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
import attr

from base.models.enums.academic_type import AcademicTypes
from base.models.enums.active_status import ActiveStatusEnum
from base.models.enums.activity_presence import ActivityPresence
from base.models.enums.decree_category import DecreeCategories
from base.models.enums.diploma_coorganization import DiplomaCoorganizationTypes
from base.models.enums.duration_unit import DurationUnitsEnum
from base.models.enums.education_group_types import TrainingType
from base.models.enums.funding_codes import FundingCodes
from base.models.enums.internship_presence import InternshipPresence
from base.models.enums.rate_code import RateCode
from base.models.enums.schedule_type import ScheduleTypeEnum
from base.models.utils import utils
from ddd.logic.formation_catalogue.domain.model._first_year_bachelor import FirstYearBachelor, FirstYearBachelorIdentity
from ddd.logic.formation_catalogue.domain.model.bachelor import Bachelor
from ddd.logic.formation_catalogue.dtos import TrainingDto, BachelorDto
from education_group.ddd.domain._academic_partner import AcademicPartner, AcademicPartnerIdentity
from education_group.ddd.domain._address import Address
from education_group.ddd.domain._campus import Campus
from education_group.ddd.domain._co_graduation import CoGraduation
from education_group.ddd.domain._co_organization import Coorganization, CoorganizationIdentity
from education_group.ddd.domain._diploma import Diploma, DiplomaAim, DiplomaAimIdentity
from education_group.ddd.domain._entity import Entity as EntityValueObject, Entity
from education_group.ddd.domain._funding import Funding
from education_group.ddd.domain._hops import HOPS
from education_group.ddd.domain._isced_domain import IscedDomain, IscedDomainIdentity
from education_group.ddd.domain._language import Language
from education_group.ddd.domain._study_domain import StudyDomain, StudyDomainIdentity
from education_group.ddd.domain._titles import Titles
from education_group.ddd.domain.exception import TrainingNotFoundException
from education_group.ddd.domain.training import Training, TrainingIdentity, TrainingIdentityThroughYears
from education_group.ddd.validators.validators_by_business_action import CopyTrainingValidatorList, \
    CreateTrainingValidatorList
from osis_common.ddd import interface
from osis_common.ddd.interface import RootEntityBuilder


class TrainingBuilder(RootEntityBuilder):
    @classmethod
    def build_from_command(cls, cmd: 'CommandRequest') -> 'Training':
        raise NotImplementedError

    @classmethod
    def build_from_repository_dto(cls, dto_object: 'TrainingDto') -> 'Training':
        entity_id = TrainingIdentity(acronym=dto_object.acronym, year=dto_object.year)
        secondary_domains = [
            StudyDomain(
                entity_id=StudyDomainIdentity(decree_name=domain.decree_name, code=domain.code),
                domain_name=domain.name
            )
            for domain in dto_object.secondary_domains
        ]

        coorganizations = [
            Coorganization(
                entity_id=CoorganizationIdentity(
                    partner_name=co_organization.organization_name,
                    training_acronym=dto_object.acronym,
                    training_year=dto_object.year,
                ),
                partner=AcademicPartner(
                    entity_id=AcademicPartnerIdentity(name=co_organization.organization_name),
                    address=Address(
                        country_name=co_organization.country,
                        city=co_organization.city,
                    ) if co_organization.country else None,
                    logo_url=co_organization.logo_url,
                ),
                is_for_all_students=co_organization.all_students,
                is_reference_institution=co_organization.enrollment_place,
                certificate_type=DiplomaCoorganizationTypes[co_organization.diploma]
                if co_organization.diploma else None,
                is_producing_certificate=co_organization.is_producing_certificate,
                is_producing_certificate_annexes=co_organization.is_producing_annexe,
            )
            for co_organization in dto_object.co_organizations
        ]
        certificate_aims = [
            DiplomaAim(
                entity_id=DiplomaAimIdentity(section=aim.section, code=aim.code),
                description=aim.description,
            )
            for aim in dto_object.diploma_aims
        ]

        datas = {
            'entity_identity': entity_id,
            'entity_id': entity_id,
            'code': dto_object.code,
            'identity_through_years': TrainingIdentityThroughYears(uuid=dto_object.uuid),
            'type': TrainingType[dto_object.type],
            'credits': dto_object.credits,
            'schedule_type': ScheduleTypeEnum[dto_object.schedule_type],
            'duration': dto_object.duration,
            'start_year': dto_object.start_year,
            'titles': Titles(
                title_fr=dto_object.title_fr,
                partial_title_fr=dto_object.partial_title_fr,
                title_en=dto_object.title_en,
                partial_title_en=dto_object.partial_title_en,
            ),
            'status': ActiveStatusEnum[dto_object.status],
            'keywords': dto_object.keywords,
            'internship_presence': InternshipPresence[dto_object.internship_presence]
            if dto_object.internship_presence else None,
            'is_enrollment_enabled': dto_object.is_enrollment_enabled,
            'has_online_re_registration': dto_object.has_online_re_registration,
            'has_partial_deliberation': dto_object.has_partial_deliberation,
            'has_admission_exam': dto_object.has_admission_exam,
            'has_dissertation': dto_object.has_dissertation,
            'produce_university_certificate': dto_object.produce_university_certificate,
            'decree_category': DecreeCategories[dto_object.decree_category] if dto_object.decree_category else None,
            'rate_code': RateCode[dto_object.rate_code] if dto_object.rate_code else None,
            'main_language': Language(name=dto_object.main_language_name,),
            'english_activities': ActivityPresence[dto_object.english_activities]
            if dto_object.english_activities else None,
            'other_language_activities': ActivityPresence[
                dto_object.other_language_activities] if dto_object.other_language_activities else None,
            'internal_comment': dto_object.internal_comment,
            'main_domain': StudyDomain(
                entity_id=StudyDomainIdentity(
                    decree_name=dto_object.main_domain_decree_name,
                    code=dto_object.main_domain_code,
                ),
                domain_name=dto_object.main_domain_name,
            ) if dto_object.main_domain_name else None,
            'secondary_domains': secondary_domains,
            'isced_domain': IscedDomain(
                entity_id=IscedDomainIdentity(code=dto_object.isced_domain_code),
                title_fr=dto_object.isced_domain_title_fr,
                title_en=dto_object.isced_domain_title_en,
            ) if dto_object.isced_domain_code else None,
            'management_entity': EntityValueObject(acronym=dto_object.management_entity_acronym),
            'administration_entity': EntityValueObject(acronym=dto_object.administration_entity_acronym),
            'end_year': dto_object.end_year,
            'enrollment_campus': Campus(
                name=dto_object.enrollment_campus_name,
                university_name=dto_object.enrollment_campus_university_name,
            ),
            'other_campus_activities': ActivityPresence[
                dto_object.other_campus_activities] if dto_object.other_campus_activities else None,
            'funding': Funding(
                can_be_funded=dto_object.funding_can_be_funded,
                funding_orientation=FundingCodes[dto_object.funding_orientation]
                if dto_object.funding_orientation else None,
                can_be_international_funded=dto_object.funding_can_be_international_funded,
                international_funding_orientation=FundingCodes[dto_object.funding_international_funding_orientation]
                if dto_object.funding_international_funding_orientation else None,
            ),
            'hops': HOPS(
                ares_code=dto_object.ares_code,
                ares_graca=dto_object.ares_graca,
                ares_authorization=dto_object.ares_authorization,
            ),
            'co_graduation': CoGraduation(
                code_inter_cfb=dto_object.co_graduation_code_inter_cfb,
                coefficient=dto_object.co_graduation_coefficient,
            ),
            'co_organizations': coorganizations,
            'academic_type': AcademicTypes[dto_object.academic_type] if dto_object.academic_type else None,
            'duration_unit': DurationUnitsEnum[dto_object.duration_unit] if dto_object.duration_unit else None,
            'diploma': Diploma(
                leads_to_diploma=dto_object.diploma_leads_to_diploma,
                printing_title=dto_object.diploma_printing_title,
                professional_title=dto_object.diploma_professional_title,
                aims=certificate_aims
            )
        }

        if isinstance(dto_object, BachelorDto):
            return Bachelor(
                first_year_bachelor=FirstYearBachelor(
                    entity_id=FirstYearBachelorIdentity(),
                    administration_entity=EntityValueObject(
                        acronym=dto_object.first_year_bachelor_administration_entity_acronym
                    ) if dto_object.first_year_bachelor_administration_entity_acronym else None
                ),
                **datas
            )
        return Training(**datas)

    def copy_to_next_year(self, training_from: 'Training', training_repository: 'TrainingRepository') -> 'Training':
        identity_next_year = TrainingIdentity(acronym=training_from.acronym, year=training_from.year + 1)
        CopyTrainingValidatorList(training_from).validate()
        try:
            training_next_year = training_repository.get(identity_next_year)
            training_next_year.update_from_other_training(training_from)
        except TrainingNotFoundException:
            training_next_year = attr.evolve(
                training_from,
                entity_identity=identity_next_year,
                entity_id=identity_next_year,
            )
        return training_next_year

    def copy_aims_to_next_year(
            self,
            training_from: 'Training',
            training_repository: 'TrainingRepository'
    ) -> 'Training':
        identity_next_year = TrainingIdentity(acronym=training_from.acronym, year=training_from.year + 1)
        training_next_year = training_repository.get(identity_next_year)
        training_next_year.update_aims_from_other_training(training_from)
        return training_next_year

    def create_training(self, command: 'CreateTrainingCommand') -> 'Training':
        training_identity = TrainingIdentity(command.abbreviated_title, command.year)

        secondary_domains = []
        for dom in command.secondary_domains:
            secondary_domains.append(
                StudyDomain(
                    entity_id=StudyDomainIdentity(dom[0], dom[1]),
                    domain_name=None,
                )
            )
        datas = {
            'entity_identity': training_identity,
            'entity_id': training_identity,
            'code': command.code,
            'type': utils.get_enum_from_str(command.type, TrainingType),
            'credits': command.credits,
            'schedule_type': utils.get_enum_from_str(command.schedule_type, ScheduleTypeEnum),
            'duration': command.duration,
            'duration_unit': utils.get_enum_from_str(command.duration_unit, DurationUnitsEnum),
            'start_year': command.start_year,
            'titles': Titles(
                title_fr=command.title_fr,
                partial_title_fr=command.partial_title_fr,
                title_en=command.title_en,
                partial_title_en=command.partial_title_en,
            ),
            'status': utils.get_enum_from_str(command.status, ActiveStatusEnum),
            'keywords': command.keywords,
            'internship_presence': utils.get_enum_from_str(command.internship_presence, InternshipPresence),
            'is_enrollment_enabled': command.is_enrollment_enabled,
            'has_online_re_registration': command.has_online_re_registration,
            'has_partial_deliberation': command.has_partial_deliberation,
            'has_admission_exam': command.has_admission_exam,
            'has_dissertation': command.has_dissertation,
            'produce_university_certificate': command.produce_university_certificate,
            'decree_category': utils.get_enum_from_str(command.decree_category, DecreeCategories),
            'rate_code': utils.get_enum_from_str(command.rate_code, RateCode),
            'main_language': Language(command.main_language) if command.main_language else None,
            'english_activities': utils.get_enum_from_str(command.english_activities, ActivityPresence),
            'other_language_activities': utils.get_enum_from_str(
                command.other_language_activities, ActivityPresence
            ),
            'internal_comment': command.internal_comment,
            'main_domain': StudyDomain(
                entity_id=StudyDomainIdentity(decree_name=command.main_domain_decree, code=command.main_domain_code),
                domain_name=None,
            ) if command.main_domain_code else None,
            'secondary_domains': secondary_domains,
            'isced_domain': IscedDomain(
                entity_id=IscedDomainIdentity(command.isced_domain_code),
                title_fr=None,
                title_en=None,
            ) if command.isced_domain_code else None,
            'management_entity': Entity(acronym=command.management_entity_acronym),
            'administration_entity': Entity(acronym=command.administration_entity_acronym),
            'end_year': command.end_year,
            'enrollment_campus': Campus(
                name=command.enrollment_campus_name,
                university_name=command.enrollment_campus_organization_name,
            ),
            'other_campus_activities': utils.get_enum_from_str(command.other_campus_activities, ActivityPresence),
            'funding': Funding(
                can_be_funded=command.can_be_funded,
                funding_orientation=FundingCodes[
                    command.funding_orientation
                ] if command.funding_orientation else None,
                can_be_international_funded=command.can_be_international_funded,
                international_funding_orientation=FundingCodes[
                    command.international_funding_orientation
                ] if command.international_funding_orientation else None,
            ),
            'hops': HOPS(
                ares_code=command.ares_code,
                ares_graca=command.ares_graca,
                ares_authorization=command.ares_authorization,
            ),
            'co_graduation': CoGraduation(
                code_inter_cfb=command.code_inter_cfb,
                coefficient=command.coefficient,
            ),
            'academic_type': utils.get_enum_from_str(command.academic_type, AcademicTypes),
            'diploma': Diploma(
                aims=None,
                leads_to_diploma=command.leads_to_diploma,
                printing_title=command.printing_title,
                professional_title=command.professional_title,
            ),
        }

        if datas['type'] == TrainingType.BACHELOR:
            training = Bachelor(
                first_year_bachelor=FirstYearBachelor(
                    entity_id=FirstYearBachelorIdentity(),
                    administration_entity=None
                ),
                **datas
            )
        else:
            training = Training(**datas)
        CreateTrainingValidatorList(training).validate()
        return training

    def _get_enum_from_str(self, value: str, enum_class):
        if not value:
            return None
        try:
            return enum_class[value]
        except ValueError:
            raise interface.BusinessException(
                "Invalid enum choice (value={}, enumeration_class={})".format(value, enum_class)
            )
