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
from typing import List

from django.template.defaultfilters import yesno
from django.utils.translation import gettext_lazy as _, pgettext_lazy

from base.business.education_group import ordering_data
from base.business.xls import get_name_or_username
from base.models.enums.publication_contact_type import PublicationContactType
from education_group.ddd import command
from education_group.ddd.service.read import get_group_service, get_training_service
from education_group.models.group_year import GroupYear
from education_group.views import serializers
from osis_common.document import xls_build
from program_management.ddd.domain.node import NodeIdentity
from program_management.ddd.domain.service.identity_search import ProgramTreeVersionIdentitySearch
from program_management.ddd.repositories.program_tree_version import ProgramTreeVersionRepository
from base.utils.excel import get_html_to_text

ARES_ONLY = [str(_('ARES study code')), str(_('ARES-GRACA')), str(_('ARES ability'))]

ACTIVITIES_TITLES = [
    str(_('Activities on other campus')), str(_('Internship')), str(_('Dissertation')), str(_('Primary language')),
    str(_('activities in English')).title(), str(_('Other languages activities')),
]

WORKSHEET_TITLE = _('Education_groups')
XLS_FILENAME = _('Education_groups')
XLS_DESCRIPTION = _("List education groups")

WITH_VALIDITY = "with_validity"
WITH_OSIS_CODE = "with_osis_code"
WITH_PARTIAL_ENGLISH_TITLES = "with_partial_english_titles"
WITH_EDUCATION_FIELDS = "with_education_fields"
WITH_ORGANIZATION = "with_organization"
WITH_ACTIVITIES = "with_activities"
WITH_RESPONSIBLES_AND_CONTACTS = "with_responsibles_and_contacts"
WITH_DIPLOMA_CERTIFICAT = "with_diploma_and_certificat"
WITH_CO_GRADUATION_AND_PARTNERSHIP = "with_co_graduation_and_partnership"
WITH_ARES_CODE = "with_ares_code"
WITH_ENROLLMENT = "with_enrollment"
WITH_FUNDING = "with_funding"
WITH_OTHER_LEGAL_INFORMATION = "with_other_legal_information"
WITH_ADDITIONAL_INFO = "with_additional_info"
WITH_KEYWORDS = "with_keywords"

TRAINING_LIST_CUSTOMIZABLE_PARAMETERS = [
    WITH_VALIDITY,
    WITH_OSIS_CODE,
    WITH_PARTIAL_ENGLISH_TITLES,
    WITH_EDUCATION_FIELDS,
    WITH_ORGANIZATION,
    WITH_RESPONSIBLES_AND_CONTACTS,
    WITH_ACTIVITIES,
    WITH_DIPLOMA_CERTIFICAT,
    WITH_CO_GRADUATION_AND_PARTNERSHIP,
    WITH_ENROLLMENT,
    WITH_FUNDING,
    WITH_ARES_CODE,
    WITH_OTHER_LEGAL_INFORMATION,
    WITH_ADDITIONAL_INFO,
    WITH_KEYWORDS
]
DEFAULT_EDUCATION_GROUP_TITLES = [str(_('Ac yr.')), str(pgettext_lazy('abbreviation', 'Acronym/Short title')),
                                  str(_('Title')), str(_('Category')), str(_('Type')), str(_('Credits'))]

COMMON_ARES_TITlES = [str(_('Code co-graduation inter CfB')), str(_('Co-graduation total coefficient'))]

PARAMETER_HEADERS = {
    WITH_VALIDITY: [str(_('Status')), str(_('Beginning')), str(_('Last year of org.'))],
    WITH_OSIS_CODE: [str(_('Code OSIS'))],
    WITH_PARTIAL_ENGLISH_TITLES: [str(_('Title in English')), str(_('Partial title in French')),
                                  str(_('Partial title in English'))],
    WITH_EDUCATION_FIELDS: [str(_('main domain')).title(), str(_('secondary domains')).title(), str(_('ISCED domain'))],
    WITH_ORGANIZATION: [str(_('Schedule type')), str(_('Manag. ent.')), str(_('Admin. ent.')),
                        str(_('Learning location')), str(_('Duration'))] + ACTIVITIES_TITLES,
    WITH_ACTIVITIES: ACTIVITIES_TITLES,
    WITH_RESPONSIBLES_AND_CONTACTS: ["{} - {}".format(str(_('General informations')), str(_('contacts')))],
    WITH_DIPLOMA_CERTIFICAT: [str(_('Leads to diploma/certificate')), str(_('Diploma title')),
                              str(_('Professionnal title')), str(_('certificate aims')).title()],
    WITH_CO_GRADUATION_AND_PARTNERSHIP: COMMON_ARES_TITlES + [str(_('Program organized with other institutes'))],
    WITH_ARES_CODE: COMMON_ARES_TITlES + ARES_ONLY,
    WITH_ENROLLMENT: [str(_('Enrollment campus')), str(_('Enrollment enabled')), str(_('Web re-registration')),
                      str(_('Partial deliberation')), str(_('Admission exam')), str(_('Rate code'))],
    WITH_FUNDING: [str(_('Funding')), str(_('Funding direction')), str(_('Funding international cooperation CCD/CUD')),
                   str(_('Funding international cooperation CCD/CUD direction'))],
    WITH_OTHER_LEGAL_INFORMATION: [str(_('Academic type')), str(_('University certificate')),
                                   str(_('Decree category'))],
    WITH_ADDITIONAL_INFO: [str(_('Type of constraint')), str(_('minimum constraint').title()),
                           str(_('maximum constraint').title()), str(_('comment (internal)').title()),
                           str(_('Remark')), str(_('remark in english').title())],
    WITH_KEYWORDS: [str(_('Keywords'))]
}

CARRIAGE_RETURN = "\n"


def create_customized_xls(user, found_education_groups_param, filters, order_data, other_params: List):
    if WITH_ORGANIZATION in other_params and WITH_ACTIVITIES in other_params:
        other_params.remove(WITH_ACTIVITIES)

    found_education_groups = ordering_data(found_education_groups_param, order_data)
    working_sheets_data = prepare_xls_content_with_parameters(found_education_groups, other_params)
    parameters = {xls_build.DESCRIPTION: XLS_DESCRIPTION,
                  xls_build.USER: get_name_or_username(user),
                  xls_build.FILENAME: XLS_FILENAME,
                  xls_build.HEADER_TITLES: _build_customized_header(other_params),
                  xls_build.WS_TITLE: WORKSHEET_TITLE}

    return xls_build.generate_xls(xls_build.prepare_xls_parameters_list(working_sheets_data, parameters), filters)


def prepare_xls_content_with_parameters(found_education_groups: List[GroupYear], other_params) -> List:
    return [extract_xls_data_from_education_group_with_parameters(eg, other_params) for eg in found_education_groups]


def extract_xls_data_from_education_group_with_parameters(group_year: GroupYear, other_params) -> List:
    training = _get_training(group_year.academic_year.year, group_year.acronym)

    node_identity = NodeIdentity(code=group_year.partial_acronym, year=group_year.academic_year.year)
    program_tree_version_identity = ProgramTreeVersionIdentitySearch().get_from_node_identity(node_identity)
    current_version = ProgramTreeVersionRepository.get(program_tree_version_identity)
    get_group_cmd = command.GetGroupCommand(year=group_year.academic_year.year, code=group_year.partial_acronym)
    group = get_group_service.get_group(get_group_cmd)

    data = [
        group_year.academic_year.name,
        group_year.complete_title_fr,
        build_title_fr(training, group, current_version),
        get_category(group),
        group.type.value,
        group.credits if group.credits else ""
    ]
    if WITH_VALIDITY in other_params:
        if training:
            data.append(training.status.value)
            data.append(_get_start_year(current_version, training, group))
            data.append(_get_end_year(current_version, training, group))
        else:
            data.extend(add_empty_str(WITH_VALIDITY))

    if WITH_OSIS_CODE in other_params:
        data.append(group.code)

    if WITH_PARTIAL_ENGLISH_TITLES in other_params:
        data.extend(_get_titles(current_version, training, group))

    if WITH_EDUCATION_FIELDS in other_params:
        if group.is_training():
            data.append(training.main_domain if training.main_domain else '')
            data.append(training.secondary_domains if training.secondary_domains else '')
            data.append("{} {}".format(training.isced_domain.code,
                                       training.isced_domain.title_fr) if training.isced_domain else '')
        else:
            data.extend(add_empty_str(WITH_EDUCATION_FIELDS))

    if WITH_ORGANIZATION in other_params:
        if group.is_training():
            data.append(training.schedule_type.value)
            data.append(management_entity(training, group, current_version))
            data.append(training.administration_entity.acronym)
            data.append("{} - {}".format(group.teaching_campus.name, group.teaching_campus.university_name))
            if training.duration and training.duration_unit.value:
                data.append("{} {}".format(training.duration, training.duration_unit.value))
            else:
                data.append("")
            data.extend(activities_data(training))
        else:
            data.extend(add_empty_str(WITH_ORGANIZATION))

    if WITH_RESPONSIBLES_AND_CONTACTS in other_params:
        if group.is_training():
            data.append(_get_responsibles_and_contacts(group))
        else:
            data.extend(add_empty_str(WITH_RESPONSIBLES_AND_CONTACTS))

    if WITH_ACTIVITIES in other_params:
        if group.is_training():
            data.extend(activities_data(training))
        else:
            data.extend(add_empty_str(WITH_ACTIVITIES))

    if WITH_DIPLOMA_CERTIFICAT in other_params:
        if group.is_training():
            data.append(yesno(training.diploma.leads_to_diploma).title())
            data.append(yesno(training.diploma.printing_title))
            data.append(yesno(training.diploma.professional_title))
            aims = ''
            for aim in training.diploma.aims:
                aims += "{} - {} - {}{}".format(aim.section, aim.code, aim.description, CARRIAGE_RETURN)
            data.append(aims)
        else:
            data.extend(add_empty_str(WITH_DIPLOMA_CERTIFICAT))

    if WITH_CO_GRADUATION_AND_PARTNERSHIP in other_params:
        if group.is_training():
            data.extend(_build_common_ares_code_data(training))
            data.append(get_co_organizations(training))
        else:
            data.extend(add_empty_str(WITH_CO_GRADUATION_AND_PARTNERSHIP))

    if WITH_ENROLLMENT in other_params:
        if group.is_training():
            data.append("{} - {}".format(training.enrollment_campus.name, training.enrollment_campus.university_name))
            data.append(yesno(training.is_enrollment_enabled).title())
            data.append(yesno(training.has_online_re_registration).title())
            data.append(yesno(training.has_partial_deliberation).title())
            data.append(yesno(training.has_admission_exam).title())
            data.append(training.rate_code.value if training.rate_code else '')
        else:
            data.extend(add_empty_str(WITH_ENROLLMENT))

    if WITH_FUNDING in other_params:
        if group.is_training():
            data.append(yesno(training.funding.can_be_funded).title())
            data.append(
                training.funding.funding_orientation.value.title() if training.funding.funding_orientation else ''
            )
            data.append(yesno(training.funding.can_be_international_funded).title())
            data.append(
                training.funding.international_funding_orientation.value.title()
                if training.funding.international_funding_orientation else ''
            )
        else:
            data.extend(add_empty_str(WITH_FUNDING))

    if WITH_ARES_CODE in other_params:
        if group.is_training():
            if WITH_CO_GRADUATION_AND_PARTNERSHIP not in other_params:
                data.extend(_build_common_ares_code_data(training))
            data.append(training.hops.ares_code)
            data.append(training.hops.ares_graca)
            data.append(training.hops.ares_authorization)
        else:
            data.extend(add_empty_str(WITH_ARES_CODE))

    if WITH_OTHER_LEGAL_INFORMATION in other_params:
        if group.is_training():
            data.append(training.academic_type.value if training.academic_type else '')
            data.append(yesno(training.produce_university_certificate).title())
            data.append("{} - {}".format(training.decree_category.name,
                                         training.decree_category.value) if training.decree_category.value else '')
        else:
            data.extend(add_empty_str(WITH_OTHER_LEGAL_INFORMATION))

    if WITH_ADDITIONAL_INFO in other_params:
        if group.is_training():
            data.append(group.content_constraint.type.value.title() if group.content_constraint.type else '')
            data.append(group.content_constraint.minimum)
            data.append(group.content_constraint.maximum)
            data.append(training.internal_comment)
            data.append(get_html_to_text(group.remark.text_fr))
            data.append(get_html_to_text(group.remark.text_en))

        else:
            data.extend(add_empty_str(WITH_ADDITIONAL_INFO))

    if WITH_KEYWORDS in other_params:
        if group.is_training():
            data.append(training.keywords)
        else:
            data.extend(add_empty_str(WITH_KEYWORDS))
    return data


def _build_customized_header(other_params):
    customized_header = DEFAULT_EDUCATION_GROUP_TITLES
    print(customized_header)
    for parameter in other_params:
        if parameter == WITH_ARES_CODE and WITH_CO_GRADUATION_AND_PARTNERSHIP in other_params:
            customized_header.extend(ARES_ONLY)
        else:
            customized_header.extend(PARAMETER_HEADERS[parameter])
    return customized_header


def _get_training(year: int, acronym: str) -> 'Training':
    get_training_cmd = command.GetTrainingCommand(
        year=year,
        acronym=acronym
    )
    return get_training_service.get_training(get_training_cmd)


def add_empty_str(parameter):
    # ch = []
    # for occurence in PARAMETER_HEADERS[parameter]:
    #     ch.append('')
    # return ch
    return ['' for occurence in PARAMETER_HEADERS[parameter]]


def _get_start_year(current_version, training, group):
    if current_version.is_standard:
        return training.start_year
    else:
        return group.start_year


def _get_end_year(current_version, training, group):
    if current_version.is_standard:
        return training.end_year if training.end_year else str(_("unspecified"))
    else:
        return group.end_year if group.end_year else str(_("unspecified"))


def get_category(group):
    if group.is_training():
        return str(_('Training'))
    return '?'


def _get_titles(current_version, training, group):
    titles = []
    if group.is_training():
        title_en = training.titles.title_en if training.titles.title_en else ''
        if (not current_version.is_standard or current_version.is_transition) and current_version.title_en:
            title_en += current_version.title_en
        titles.append(title_en)

        if training.is_finality():
            titles.append(training.titles.partial_title_fr)
            titles.append(training.titles.partial_title_en)
        else:
            titles.extend(['', ''])
    else:
        titles.extend(['', '', ''])

    return titles


def build_title_fr(training, group, current_version):
    if group.is_training():
        title_fr = training.titles.title_fr
        if (not current_version.is_standard or current_version.is_transition) and current_version.title_fr:
            title_fr += current_version.title_fr
        return title_fr
    else:
        return ''


def management_entity(training, group, current_version):
    if current_version.is_standard:
        return training.management_entity.acronym
    else:
        return group.management_entity.acronym


def _get_responsibles_and_contacts(group):
    responsibles_and_contacts = ''

    contacts = serializers.general_information.get_contacts(group)
    academic_responsibles = contacts.get(PublicationContactType.ACADEMIC_RESPONSIBLE.name) or []
    other_academic_responsibles = contacts.get(PublicationContactType.OTHER_ACADEMIC_RESPONSIBLE.name) or []
    jury_members = contacts.get(PublicationContactType.JURY_MEMBER.name) or []
    other_contacts = contacts.get(PublicationContactType.OTHER_CONTACT.name) or []

    responsibles_and_contacts += get_contacts(academic_responsibles, _('Academic responsible'))
    responsibles_and_contacts += get_contacts(other_academic_responsibles, _('Other academic responsibles'))
    responsibles_and_contacts += get_contacts(jury_members, _('Jury members'))
    responsibles_and_contacts += get_contacts(other_contacts, _('Other contacts'))

    return responsibles_and_contacts


def get_contacts(contact_persons, title):
    if contact_persons:
        responsibles_and_contacts = '{}{}'.format(title, CARRIAGE_RETURN)
        for contact in contact_persons:
            if contact.get('email'):
                responsibles_and_contacts += contact.get('email')
            else:
                responsibles_and_contacts += contact.get('description', '')
            responsibles_and_contacts += "{}".format(CARRIAGE_RETURN)
            if contact.get('role_fr'):
                responsibles_and_contacts += "(fr) {}{}".format(contact.get('role_fr'), CARRIAGE_RETURN)
            if contact.get('role_en'):
                responsibles_and_contacts += "(en) {}{}".format(contact.get('role_en'), CARRIAGE_RETURN)
            responsibles_and_contacts += "{}".format(CARRIAGE_RETURN)
        responsibles_and_contacts += "{}".format(CARRIAGE_RETURN)
        return responsibles_and_contacts
    return ''


def get_co_organizations(training):
    co_organizations = ''
    if training.co_organizations:
        for idx, coorganization in enumerate(training.co_organizations):
            if idx > 0:
                co_organizations += CARRIAGE_RETURN
            co_organizations += "{} - {} {}{}".format(
                coorganization.partner.address.country_name,
                coorganization.partner.address.city,
                CARRIAGE_RETURN,
                coorganization.partner.name
            )
            co_organizations += "{} : {}{}".format(str(_('For all students')),
                                                   yesno(coorganization.is_for_all_students).title(),
                                                   CARRIAGE_RETURN)
            co_organizations += "{} : {}{}".format(str(_('Reference institution')),
                                                   yesno(coorganization.is_reference_institution).title(),
                                                   CARRIAGE_RETURN)
            co_organizations += "{} : {}{}".format(
                str(_('UCL Diploma')),
                coorganization.certificate_type.value if coorganization.certificate_type else '', CARRIAGE_RETURN
            )
            co_organizations += "{} : {}{}".format(str(_('Producing certificat')),
                                                   yesno(coorganization.is_producing_certificate).title(),
                                                   CARRIAGE_RETURN)
            co_organizations += "{} : {}{}".format(str(_('Producing annexe')),
                                                   yesno(coorganization.is_producing_certificate_annexes).title(),
                                                   CARRIAGE_RETURN)
    return ''


def _build_common_ares_code_data(training):
    return [training.co_graduation.code_inter_cfb,
            training.co_graduation.coefficient if training.co_graduation.coefficient else '']


def activities_data(training):
    data = list()
    data.append(training.other_campus_activities.value if training.other_campus_activities else '')
    data.append(training.internship_presence.value.title() if training.internship_presence else '')
    data.append(str(_('Yes')) if training.has_dissertation else str(_('No')))
    data.append(training.main_language.name if training.main_language else '')
    data.append(training.english_activities.value.title() if training.english_activities else '')
    data.append(training.other_language_activities.value.title() if training.other_language_activities else '')
    return data
