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
from base.utils.excel import get_html_to_text
from education_group.ddd import command
from education_group.ddd.service.read import get_group_service, get_training_service, get_mini_training_service
from education_group.models.group_year import GroupYear
from education_group.views import serializers
from osis_common.document import xls_build
from program_management.ddd.domain.node import NodeIdentity
from program_management.ddd.domain.service.identity_search import ProgramTreeVersionIdentitySearch
from program_management.ddd.repositories.node import NodeRepository
from program_management.ddd.repositories.program_tree_version import ProgramTreeVersionRepository
from program_management.ddd.domain import exception
from openpyxl.styles import Font

ARES_ONLY = [str(_('ARES study code')), str(_('ARES-GRACA')), str(_('ARES ability'))]

ACTIVITIES_TITLES = [
    str(_('Activities on other campus')), str(_('Internship')), str(_('Dissertation')), str(_('Primary language')),
    str(_('activities in English')).capitalize(), str(_('Other languages activities'))
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
    WITH_OSIS_CODE: [str(_('Code'))],
    WITH_PARTIAL_ENGLISH_TITLES: [str(_('Title in English')), str(_('Partial title in French')),
                                  str(_('Partial title in English'))],
    WITH_EDUCATION_FIELDS: [str(_('main domain')).capitalize(), str(_('secondary domains')).capitalize(),
                            str(_('ISCED domain'))],
    WITH_ORGANIZATION: [str(_('Schedule type')), str(_('Manag. ent.')), str(_('Admin. ent.')),
                        str(_('Learning location')), str(_('Duration'))] + ACTIVITIES_TITLES,
    WITH_ACTIVITIES: ACTIVITIES_TITLES,
    WITH_RESPONSIBLES_AND_CONTACTS: ["{} - {}".format(str(_('General informations')), str(_('contacts')))],
    WITH_DIPLOMA_CERTIFICAT: [str(_('Leads to diploma/certificate')), str(_('Diploma title')),
                              str(_('Professionnal title')), str(_('certificate aims')).capitalize()],
    WITH_CO_GRADUATION_AND_PARTNERSHIP: COMMON_ARES_TITlES + [str(_('Program organized with other institutes'))],
    WITH_ARES_CODE: COMMON_ARES_TITlES + ARES_ONLY,
    WITH_ENROLLMENT: [str(_('Enrollment campus')), str(_('Enrollment enabled')), str(_('Web re-registration')),
                      str(_('Partial deliberation')), str(_('Admission exam')), str(_('Rate code'))],
    WITH_FUNDING: [str(_('Funding')), str(_('Funding direction')), str(_('Funding international cooperation CCD/CUD')),
                   str(_('Funding international cooperation CCD/CUD direction'))],
    WITH_OTHER_LEGAL_INFORMATION: [str(_('Academic type')), str(_('University certificate')),
                                   str(_('Decree category'))],
    WITH_ADDITIONAL_INFO: [str(_('Type of constraint')), str(_('minimum constraint').capitalize()),
                           str(_('maximum constraint').capitalize()), str(_('comment (internal)').capitalize()),
                           str(_('Remark')), str(_('Remark in English'))],
    WITH_KEYWORDS: [str(_('Keywords'))]
}

CARRIAGE_RETURN = "\n"
BOLD_FONT = Font(bold=True)


def create_customized_xls(user, found_education_groups_param, filters, order_data, other_params: List):
    found_education_groups = ordering_data(found_education_groups_param, order_data)
    working_sheets_data = prepare_xls_content_with_parameters(found_education_groups, other_params)
    parameters = {xls_build.DESCRIPTION: XLS_DESCRIPTION,
                  xls_build.USER: get_name_or_username(user),
                  xls_build.FILENAME: XLS_FILENAME,
                  xls_build.HEADER_TITLES: _build_headers(other_params),
                  xls_build.WS_TITLE: WORKSHEET_TITLE,
                  xls_build.FONT_ROWS: {BOLD_FONT: [0]}
                  }

    return xls_build.generate_xls(xls_build.prepare_xls_parameters_list(working_sheets_data, parameters), filters)


def prepare_xls_content_with_parameters(found_education_groups: List[GroupYear], other_params: List['str']) -> List:
    if WITH_ORGANIZATION in other_params and WITH_ACTIVITIES in other_params:
        other_params.remove(WITH_ACTIVITIES)
    return [extract_xls_data_from_education_group_with_parameters(eg, other_params) for eg in found_education_groups]


def extract_xls_data_from_education_group_with_parameters(group_year: GroupYear, other_params: List['str']) -> List:
    root_node = NodeRepository().get(NodeIdentity(code=group_year.acronym, year=group_year.academic_year.year))
    training = None
    mini_training = None
    group = None    
    if root_node:
        if training:
            training = _get_training(group_year.academic_year.year, group_year.acronym)            
        elif mini_training:
            mini_training = _get_mini_training(group_year.academic_year.year, group_year.acronym)
        else:
            group = _get_group(group_year.academic_year.year, group_year.partial_acronym)
    else:
        group = _get_group(group_year.academic_year.year, group_year.partial_acronym)

    node_identity = NodeIdentity(code=group_year.partial_acronym, year=group_year.academic_year.year)
    program_tree_version_identity = ProgramTreeVersionIdentitySearch().get_from_node_identity(node_identity)
    try:
        current_version = ProgramTreeVersionRepository.get(program_tree_version_identity)
    except exception.ProgramTreeVersionNotFoundException:
        current_version = None
    # get_group_cmd = command.GetGroupCommand(year=group_year.academic_year.year, code=group_year.partial_acronym)
    # group = get_group_service.get_group(get_group_cmd)

    data = [
        group_year.academic_year.name,
        group_year.complete_title_fr,
        build_title_fr(training, current_version, mini_training),
        get_category(training, mini_training, group),
        group.type.value,
        group.credits if group.credits else ""
    ]
    if WITH_VALIDITY in other_params:
        if training:
            data.append(training.status.value)
            data.append(_get_start_year(current_version, training, group))
            data.append(_get_end_year(current_version, training, group))
        elif mini_training:
            data.append(mini_training.status.value)
            data.append(current_version.start_year)
            data.append(
                current_version.end_year_of_existence if current_version.end_year_of_existence else _('unspecified')
            )
        else:
            data.extend(_add_empty_characters(len(PARAMETER_HEADERS[WITH_VALIDITY])))

    if WITH_OSIS_CODE in other_params:
        data.append(group.code)

    if WITH_PARTIAL_ENGLISH_TITLES in other_params:
        data.extend(_get_titles_en(current_version, training, mini_training, group))

    if WITH_EDUCATION_FIELDS in other_params:
        if training:
            data.append(training.main_domain if training.main_domain else '')
            data.append(training.secondary_domains if training.secondary_domains else '')
            data.append("{} {}".format(training.isced_domain.code,
                                       training.isced_domain.title_fr) if training.isced_domain else '')
        else:
            data.extend(_add_empty_characters(len(PARAMETER_HEADERS[WITH_EDUCATION_FIELDS])))

    if WITH_ORGANIZATION in other_params:
        if training:
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
            data.extend(_add_empty_characters(len(PARAMETER_HEADERS[WITH_ORGANIZATION])))

    if WITH_RESPONSIBLES_AND_CONTACTS in other_params:
        if training:
            data.append(_get_responsibles_and_contacts(group))
        else:
            data.extend(_add_empty_characters(len(PARAMETER_HEADERS[WITH_RESPONSIBLES_AND_CONTACTS])))

    if WITH_ACTIVITIES in other_params:
        if training:
            data.extend(activities_data(training))
        else:
            data.extend(_add_empty_characters(len(PARAMETER_HEADERS[WITH_ACTIVITIES])))

    if WITH_DIPLOMA_CERTIFICAT in other_params:
        if training:
            data.append(yesno(training.diploma.leads_to_diploma).title())
            data.append(yesno(training.diploma.printing_title))
            data.append(yesno(training.diploma.professional_title))
            aims = ''
            for aim in training.diploma.aims:
                aims += "{} - {} - {}{}".format(aim.section, aim.code, aim.description, CARRIAGE_RETURN)
            data.append(aims)
        else:
            data.extend(_add_empty_characters(len(PARAMETER_HEADERS[WITH_DIPLOMA_CERTIFICAT])))

    if WITH_CO_GRADUATION_AND_PARTNERSHIP in other_params:
        if training:
            data.extend(_build_common_ares_code_data(training))
            data.append(get_co_organizations(training))
        else:
            data.extend(_add_empty_characters(len(PARAMETER_HEADERS[WITH_CO_GRADUATION_AND_PARTNERSHIP])))

    if WITH_ENROLLMENT in other_params:
        if training:
            data.append("{} - {}".format(training.enrollment_campus.name, training.enrollment_campus.university_name))
            data.append(yesno(training.is_enrollment_enabled).title())
            data.append(yesno(training.has_online_re_registration).title())
            data.append(yesno(training.has_partial_deliberation).title())
            data.append(yesno(training.has_admission_exam).title())
            data.append(training.rate_code.value if training.rate_code else '')
        else:
            data.extend(_add_empty_characters(len(PARAMETER_HEADERS[WITH_ENROLLMENT])))

    if WITH_FUNDING in other_params:
        if training:
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
            data.extend(_add_empty_characters(len(PARAMETER_HEADERS[WITH_FUNDING])))

    if WITH_ARES_CODE in other_params:
        if training:
            if WITH_CO_GRADUATION_AND_PARTNERSHIP not in other_params:
                data.extend(_build_common_ares_code_data(training))
            data.append(training.hops.ares_code)
            data.append(training.hops.ares_graca)
            data.append(training.hops.ares_authorization)
        else:
            if WITH_ORGANIZATION:
                data.extend(_add_empty_characters(len(PARAMETER_HEADERS[WITH_ARES_CODE])-len(COMMON_ARES_TITlES)))
            else:
                data.extend(_add_empty_characters(len(PARAMETER_HEADERS[WITH_ARES_CODE])))

    if WITH_OTHER_LEGAL_INFORMATION in other_params:
        if training:
            data.append(training.academic_type.value if training.academic_type else '')
            data.append(yesno(training.produce_university_certificate).title())
            data.append("{} - {}".format(training.decree_category.name,
                                         training.decree_category.value) if training.decree_category.value else '')
        else:
            data.extend(_add_empty_characters(len(PARAMETER_HEADERS[WITH_OTHER_LEGAL_INFORMATION])))

    if WITH_ADDITIONAL_INFO in other_params:
        if training or mini_training or group:
            data.append(group.content_constraint.type.value.title() if group.content_constraint.type else '')
            data.append(group.content_constraint.minimum)
            data.append(group.content_constraint.maximum)
            if training:
                data.append(training.internal_comment)
            else:
                data.append('')
            data.append(get_html_to_text(group.remark.text_fr))
            data.append(get_html_to_text(group.remark.text_en))
        else:
            data.extend(_add_empty_characters(len(PARAMETER_HEADERS[WITH_ADDITIONAL_INFO])))

    if WITH_KEYWORDS in other_params:
        if training:
            data.append(training.keywords)
        elif mini_training:
            data.append(mini_training.keywords)
        else:
            data.extend(_add_empty_characters(len(PARAMETER_HEADERS[WITH_KEYWORDS])))
    return data


def _build_headers(xls_parameters: List) -> List['str']:

    customized_headers = DEFAULT_EDUCATION_GROUP_TITLES.copy()
    if WITH_ORGANIZATION in xls_parameters and WITH_ACTIVITIES in xls_parameters:
        xls_parameters.remove(WITH_ACTIVITIES)
    for parameter in xls_parameters:
        if parameter == WITH_ARES_CODE and WITH_CO_GRADUATION_AND_PARTNERSHIP in xls_parameters:
            customized_headers.extend(ARES_ONLY)
        else:
            customized_headers.extend(PARAMETER_HEADERS[parameter])
    return customized_headers


def _get_training(year: int, acronym: str) -> 'Training':
    get_training_cmd = command.GetTrainingCommand(
        year=year,
        acronym=acronym
    )
    return get_training_service.get_training(get_training_cmd)


def _add_empty_characters(number_of_occurences):
    return ['' for occurence in range(number_of_occurences)]


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


def get_category(training, mini_training, group):
    if training:
        return str(_('Training'))
    elif mini_training:
        return str(_('Mini-training'))
    elif group:
        return str(_('Group'))
    else:
        return ''


def _get_titles_en(current_version, training, mini_training, group):
    titles = []
    if training:
        title_en = training.titles.title_en if training.titles.title_en else ''
    elif mini_training:
        title_en = mini_training.titles.title_en if mini_training.titles.title_en else ''
    elif group:
        title_en = group.titles.title_en
    else:
        title_en = ''

    if training or mini_training:
        if (not current_version.is_standard or current_version.is_transition) and current_version.title_en:
            title_en += current_version.title_en
        titles.append(title_en)

        if training and training.is_finality():
            titles.append(training.titles.partial_title_fr)
            titles.append(training.titles.partial_title_en)
        else:
            titles.extend(['', ''])
    else:
        titles.extend([title_en, '', ''])

    return titles


def build_title_fr(training, current_version, mini_training):
    if training:
        title_fr = training.titles.title_fr
    elif mini_training:
        title_fr = mini_training.titles.title_fr
    else:
        return ''
    if (not current_version.is_standard or current_version.is_transition) and current_version.title_fr:
        title_fr += current_version.title_fr
    return title_fr


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


def _get_mini_training(year: int, acronym: str) -> 'MiniTraining':
    get_mini_training_cmd = command.GetMiniTrainingCommand(
        year=year,
        acronym=acronym
    )
    return get_mini_training_service.get_mini_training(get_mini_training_cmd)


def _get_group(year: int, acronym: str) -> 'Group':
    get_group_training_cmd = command.GetGroupCommand(
        year=year,
        code=acronym
    )
    return get_group_service.get_group(get_group_training_cmd)
