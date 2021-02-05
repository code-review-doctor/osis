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
from typing import List, Dict

from django.core.exceptions import MultipleObjectsReturned
from django.db.models import Prefetch
from django.utils.translation import gettext_lazy as _, pgettext_lazy

from backoffice.settings.base import LANGUAGE_CODE_EN
from base.business.xls import get_name_or_username, convert_boolean
from base.models.education_group_year import EducationGroupYear
from base.models.enums import academic_calendar_type
from base.models.enums import education_group_categories
from base.models.enums import mandate_type as mandate_types
from base.models.enums.education_group_types import TrainingType
from base.models.mandate import Mandate
from base.models.offer_year_calendar import OfferYearCalendar
from education_group.models.group_year import GroupYear
from osis_common.document import xls_build
from program_management.models.education_group_version import EducationGroupVersion
from education_group.ddd.service.read import get_group_service, get_training_service
from education_group.ddd import command
from program_management.ddd.domain.node import NodeIdentity, NodeNotFoundException
from program_management.ddd.domain.service.identity_search import ProgramTreeVersionIdentitySearch
from program_management.ddd.repositories.program_tree_version import ProgramTreeVersionRepository
from program_management.ddd.service.read import node_identity_service
from education_group.ddd.domain.service.identity_search import TrainingIdentitySearch
from education_group.views import serializers
from base.models.enums.publication_contact_type import PublicationContactType
# List of key that a user can modify
DATE_FORMAT = '%d-%m-%Y'
DATE_TIME_FORMAT = '%d-%m-%Y %H:%M'
DESC = "desc"
WORKSHEET_TITLE = _('Education_groups')
XLS_FILENAME = _('Education_groups')
XLS_DESCRIPTION = _("List education groups")
EDUCATION_GROUP_TITLES = [str(_('Ac yr.')), str(pgettext_lazy('abbreviation', 'Acronym/Short title')),
                          str(_('Title')), str(_('Type')), str(_('Entity')), str(_('Code'))]
ORDER_COL = 'order_col'
ORDER_DIRECTION = 'order_direction'
#

WORKSHEET_TITLE_ADMINISTRATIVE = _('Trainings')
XLS_FILENAME_ADMINISTRATIVE = _('training_administrative_data')
XLS_DESCRIPTION_ADMINISTRATIVE = _("List of trainings with administrative data")

# Column for xls with administrative data
MANAGEMENT_ENTITY_COL = _('Management entity')
TRANING_COL = _('Training')
TYPE_COL = _('Type')
ACADEMIC_YEAR_COL = _('Validity')
START_COURSE_REGISTRATION_COL = _('Begining of course registration')
END_COURSE_REGISTRATION_COL = _('Ending of course registration')
START_EXAM_REGISTRATION_COL = _('Begining of exam registration')
END_EXAM_REGISTRATION_COL = _('Ending of exam registration')
MARKS_PRESENTATION_COL = _('Marks presentation')
DISSERTATION_PRESENTATION_COL = _('Dissertation presentation')
DELIBERATION_COL = _('Deliberation')
SCORES_DIFFUSION_COL = _('Scores diffusion')
WEIGHTING_COL = _('Weighting')
DEFAULT_LEARNING_UNIT_ENROLLMENT_COL = _('Default learning unit enrollment')
CHAIR_OF_THE_EXAM_BOARD_COL = _('Chair of the exam board')
EXAM_BOARD_SECRETARY_COL = _('Exam board secretary')
EXAM_BOARD_SIGNATORY_COL = _('Exam board signatory')
SIGNATORY_QUALIFICATION_COL = _('Signatory qualification')

SESSIONS_COLUMNS = 'sessions_columns'
SESSIONS_NUMBER = 3
SESSION_HEADERS = [
    START_EXAM_REGISTRATION_COL,
    END_EXAM_REGISTRATION_COL,
    MARKS_PRESENTATION_COL,
    DISSERTATION_PRESENTATION_COL,
    DELIBERATION_COL,
    SCORES_DIFFUSION_COL
]
EDUCATION_GROUP_TITLES_ADMINISTRATIVE = [
    MANAGEMENT_ENTITY_COL,
    TRANING_COL,
    TYPE_COL,
    ACADEMIC_YEAR_COL,
    START_COURSE_REGISTRATION_COL,
    END_COURSE_REGISTRATION_COL,
    SESSIONS_COLUMNS,   # this columns will be duplicate by SESSIONS_NUMBER [content: SESSION_HEADERS]
    WEIGHTING_COL,
    DEFAULT_LEARNING_UNIT_ENROLLMENT_COL,
    CHAIR_OF_THE_EXAM_BOARD_COL,
    EXAM_BOARD_SECRETARY_COL,
    EXAM_BOARD_SIGNATORY_COL,
    SIGNATORY_QUALIFICATION_COL,
]

WITH_VALIDITY = "with_validity"
WITH_OSIS_CODE = "with_osis_code"
WITH_PARTIAL_ENGLISH_TITLES = "with_partial_english_titles"
WITH_EDUCATION_FIELDS = "with_education_fields"
WITH_ORGANIZATION = "with_organization"
WITH_ACTIVITIES_ORGANIZATION = "with_activities_organization"
WITH_RESPONSIBLES_AND_CONTACTS = "with_responsibles_and_contacts"

TRAINING_LIST_CUSTOMIZABLE_PARAMETERS = [
    WITH_VALIDITY,
    WITH_OSIS_CODE,
    WITH_PARTIAL_ENGLISH_TITLES,
    WITH_EDUCATION_FIELDS,
    WITH_ORGANIZATION,
    WITH_ACTIVITIES_ORGANIZATION,
    WITH_RESPONSIBLES_AND_CONTACTS
]
DEFAULT_EDUCATION_GROUP_TITLES = [str(_('Ac yr.')), str(pgettext_lazy('abbreviation', 'Acronym/Short title')),
                                  str(_('Title')), str(_('Category')), str(_('Type')), str(_('Credits'))]


PARAMETER_HEADERS = {
    WITH_VALIDITY: [str(_('Status')), str(_('Beginning')), str(_('Last year of org.'))],
    WITH_OSIS_CODE: [str(_('Code OSIS'))],
    WITH_PARTIAL_ENGLISH_TITLES: [str(_('Title in English')), str(_('Partial title in French')),
                                  str(_('Partial title in English'))],
    WITH_EDUCATION_FIELDS: [str(_('main domain')).title(), str(_('secondary domains')).title(), str(_('ISCED domain'))],
    WITH_ORGANIZATION: [str(_('Schedule type')), str(_('Manag. ent.')), str(_('Admin. ent.')),
                        str(_('Learning location')), str(_('Duration'))],
    WITH_ACTIVITIES_ORGANIZATION: [str(_('Activities on other campus')), str(_('Internship')), str(_('Dissertation')),
                                   str(_('Primary language')), str(_('activities in English')).title(),
                                   str(_('Other languages activities')),
                                   ],
    WITH_RESPONSIBLES_AND_CONTACTS: ["{} - {}".format(str(_('General informations')), str(_('contacts')))]


}
CARRIAGE_RETURN = "\n"

def create_xls(user, found_education_groups_param, filters, order_data):
    found_education_groups = ordering_data(found_education_groups_param, order_data)
    working_sheets_data = prepare_xls_content(found_education_groups)
    parameters = {xls_build.DESCRIPTION: XLS_DESCRIPTION,
                  xls_build.USER: get_name_or_username(user),
                  xls_build.FILENAME: XLS_FILENAME,
                  xls_build.HEADER_TITLES: EDUCATION_GROUP_TITLES,
                  xls_build.WS_TITLE: WORKSHEET_TITLE}

    return xls_build.generate_xls(xls_build.prepare_xls_parameters_list(working_sheets_data, parameters), filters)


def prepare_xls_content(found_education_groups: List[GroupYear]) -> List:
    return [extract_xls_data_from_education_group(eg) for eg in found_education_groups]


def extract_xls_data_from_education_group(group_year: GroupYear) -> List:
    """ At this stage, the group_year has been annotated with property complete_title_fr / full_title_fr"""
    return [
        group_year.academic_year.name,
        group_year.complete_title_fr,
        group_year.full_title_fr,
        group_year.education_group_type,
        group_year.management_entity_version.acronym if group_year.management_entity_version else '',
        group_year.partial_acronym
    ]


def ordering_data(object_list, order_data):
    order_col = order_data.get(ORDER_COL)
    order_direction = order_data.get(ORDER_DIRECTION)
    reverse_direction = order_direction == DESC

    return sorted(list(object_list), key=lambda t: _get_field_value(t, order_col), reverse=reverse_direction)


def _get_field_value(instance, field):
    field_path = field.split('.')
    attr = instance
    for elem in field_path:
        try:
            attr = getattr(attr, elem) or ''
        except AttributeError:
            return None
    return attr


def create_xls_administrative_data(user, education_group_years_qs, filters, order_data, language: str):
    # Make select_related/prefetch_related in order to have low DB HIT
    education_group_years = education_group_years_qs.filter(
        education_group_type__category=education_group_categories.TRAINING
    ).select_related(
        'educationgroupversion__offer__education_group_type',
        'educationgroupversion__offer__academic_year',
    ).prefetch_related(
        Prefetch(
            'educationgroupversion__offer__education_group__mandate_set',
            queryset=Mandate.objects.prefetch_related('mandatary_set')
        ),
        Prefetch(
            'educationgroupversion__offer__offeryearcalendar_set',
            queryset=OfferYearCalendar.objects.select_related('academic_calendar__sessionexamcalendar')
        )
    )
    found_education_groups = ordering_data(education_group_years, order_data)
    # FIXME: should be improved with ddd usage

    working_sheets_data = prepare_xls_content_administrative(
        [gy.educationgroupversion for gy in found_education_groups],
        language
    )
    header_titles = _get_translated_header_titles()
    parameters = {
        xls_build.DESCRIPTION: XLS_DESCRIPTION_ADMINISTRATIVE,
        xls_build.USER: get_name_or_username(user),
        xls_build.FILENAME: XLS_FILENAME_ADMINISTRATIVE,
        xls_build.HEADER_TITLES: header_titles,
        xls_build.WS_TITLE: WORKSHEET_TITLE_ADMINISTRATIVE
    }
    return xls_build.generate_xls(xls_build.prepare_xls_parameters_list(working_sheets_data, parameters), filters)


def _get_translated_header_titles() -> List[str]:
    translated_headers = []
    for title in EDUCATION_GROUP_TITLES_ADMINISTRATIVE:
        if title != SESSIONS_COLUMNS:
            translated_headers.append(str(_(title)))
        else:
            translated_headers.extend(_get_translated_header_session_columns())
    return translated_headers


def _get_translated_header_session_columns():
    translated_session_headers = []
    for title in SESSION_HEADERS:
        translated_session_headers.append(str(_(title)))

    # Duplicate translation by nb_session + append nb_session to title
    all_headers_sessions = []
    for session_number in range(1, SESSIONS_NUMBER + 1):
        all_headers_sessions += ["{} {} ".format(translated_title, session_number) for translated_title in
                                 translated_session_headers]
    return all_headers_sessions


def prepare_xls_content_administrative(education_group_versions: List[EducationGroupVersion], language: str):
    xls_data = []
    for education_group_version in education_group_versions:
        education_group_year = education_group_version.offer
        main_data = _extract_main_data(education_group_version, language)
        administrative_data = _extract_administrative_data(education_group_year)
        mandatary_data = _extract_mandatary_data(education_group_year)

        # Put all dict together and ordered it by EDUCATION_GROUP_TITLES_ADMINISTRATIVE
        row = _convert_data_to_xls_row(
            education_group_year_data={**main_data, **administrative_data, **mandatary_data},
            header_list=EDUCATION_GROUP_TITLES_ADMINISTRATIVE
        )
        xls_data.append(row)
    return xls_data


def _extract_main_data(a_version: EducationGroupVersion, language) -> Dict:
    an_education_group_year = a_version.offer
    return {
        MANAGEMENT_ENTITY_COL:
            an_education_group_year.management_entity_version.acronym
            if an_education_group_year.management_entity_version else '',
        TRANING_COL: "{}{}".format(
            an_education_group_year.acronym,
            "[{}]".format(a_version.version_name) if a_version and a_version.version_name else ''
        ),
        TYPE_COL: "{}{}".format(
            an_education_group_year.education_group_type,
            _get_title(a_version, language)
        ),
        ACADEMIC_YEAR_COL: an_education_group_year.academic_year.name,
        WEIGHTING_COL: convert_boolean(an_education_group_year.weighting),
        DEFAULT_LEARNING_UNIT_ENROLLMENT_COL: convert_boolean(an_education_group_year.default_learning_unit_enrollment)
    }


def _extract_administrative_data(an_education_group_year: EducationGroupYear) -> Dict:
    course_enrollment_calendar = _get_offer_year_calendar_from_prefetched_data(
        an_education_group_year,
        academic_calendar_type.COURSE_ENROLLMENT
    )
    administrative_data = {
        START_COURSE_REGISTRATION_COL: _format_date(course_enrollment_calendar, 'start_date', DATE_FORMAT),
        END_COURSE_REGISTRATION_COL: _format_date(course_enrollment_calendar, 'end_date', DATE_FORMAT),
        SESSIONS_COLUMNS: [
            _extract_session_data(an_education_group_year, session_number) for
            session_number in range(1, SESSIONS_NUMBER + 1)
        ]
    }
    return administrative_data


def _extract_session_data(education_group_year: EducationGroupYear, session_number: int) -> Dict:
    session_academic_cal_type = [
        academic_calendar_type.EXAM_ENROLLMENTS,
        academic_calendar_type.SCORES_EXAM_SUBMISSION,
        academic_calendar_type.DISSERTATION_SUBMISSION,
        academic_calendar_type.DELIBERATION,
        academic_calendar_type.SCORES_EXAM_DIFFUSION
    ]
    offer_year_cals = {}
    for academic_cal_type in session_academic_cal_type:
        offer_year_cals[academic_cal_type] = _get_offer_year_calendar_from_prefetched_data(
            education_group_year,
            academic_cal_type,
            session_number=session_number
        )

    return {
        START_EXAM_REGISTRATION_COL: _format_date(offer_year_cals[academic_calendar_type.EXAM_ENROLLMENTS],
                                                  'start_date', DATE_FORMAT),
        END_EXAM_REGISTRATION_COL: _format_date(offer_year_cals[academic_calendar_type.EXAM_ENROLLMENTS], 'end_date',
                                                DATE_FORMAT),
        MARKS_PRESENTATION_COL: _format_date(offer_year_cals[academic_calendar_type.SCORES_EXAM_SUBMISSION],
                                             'start_date', DATE_FORMAT),
        DISSERTATION_PRESENTATION_COL: _format_date(offer_year_cals[academic_calendar_type.DISSERTATION_SUBMISSION],
                                                    'start_date', DATE_FORMAT),
        DELIBERATION_COL: _format_date(offer_year_cals[academic_calendar_type.DELIBERATION], 'start_date',
                                       DATE_TIME_FORMAT),
        SCORES_DIFFUSION_COL: _format_date(offer_year_cals[academic_calendar_type.SCORES_EXAM_DIFFUSION], 'start_date',
                                           DATE_TIME_FORMAT),
    }


def _extract_mandatary_data(education_group_year: EducationGroupYear) -> Dict:
    representatives = {mandate_types.PRESIDENT: [], mandate_types.SECRETARY: [], mandate_types.SIGNATORY: []}

    for mandate in education_group_year.education_group.mandate_set.all():
        representatives = _get_representatives(education_group_year, mandate, representatives)

    return {
        CHAIR_OF_THE_EXAM_BOARD_COL: names(representatives[mandate_types.PRESIDENT]),
        EXAM_BOARD_SECRETARY_COL: names(representatives[mandate_types.SECRETARY]),
        EXAM_BOARD_SIGNATORY_COL: names(representatives[mandate_types.SIGNATORY]),
        SIGNATORY_QUALIFICATION_COL: qualification(representatives[mandate_types.SIGNATORY]),
    }


def _get_representatives(education_group_year, mandate, representatives_param):
    representatives = representatives_param
    for mandataries in mandate.mandatary_set.all():
        if _is_valid_mandate(mandataries, education_group_year):
            if mandataries.mandate.function == mandate_types.PRESIDENT:
                representatives.get(mandate_types.PRESIDENT).append(mandataries)
            if mandataries.mandate.function == mandate_types.SECRETARY:
                representatives.get(mandate_types.SECRETARY).append(mandataries)
            if mandataries.mandate.function == mandate_types.SIGNATORY:
                representatives.get(mandate_types.SIGNATORY).append(mandataries)
    return representatives


def _convert_data_to_xls_row(education_group_year_data, header_list):
    xls_row = []
    for header in header_list:
        if header == SESSIONS_COLUMNS:
            session_datas = education_group_year_data.get(header, [])
            xls_row.extend(_convert_session_data_to_xls_row(session_datas))
        else:
            value = education_group_year_data.get(header, '')
            xls_row.append(value)
    return xls_row


def _convert_session_data_to_xls_row(session_datas):
    xls_session_rows = []
    for session_number in range(0, SESSIONS_NUMBER):
        session_formatted = _convert_data_to_xls_row(session_datas[session_number], SESSION_HEADERS)
        xls_session_rows.extend(session_formatted)
    return xls_session_rows


def _get_offer_year_calendar_from_prefetched_data(an_education_group_year: EducationGroupYear,
                                                  academic_calendar_type,
                                                  session_number=None):
    offer_year_cals = _get_all_offer_year_calendar_from_prefetched_data(
        an_education_group_year,
        academic_calendar_type
    )
    if session_number:
        offer_year_cals = [
            offer_year_cal for offer_year_cal in offer_year_cals
            if offer_year_cal.academic_calendar.sessionexamcalendar and
            offer_year_cal.academic_calendar.sessionexamcalendar.number_session == session_number
        ]

    if len(offer_year_cals) > 1:
        raise MultipleObjectsReturned
    return offer_year_cals[0] if offer_year_cals else None


def _get_all_offer_year_calendar_from_prefetched_data(an_education_group_year: EducationGroupYear,
                                                      academic_calendar_type) -> List:
    return [
        offer_year_calendar for offer_year_calendar in an_education_group_year.offeryearcalendar_set.all()
        if offer_year_calendar.academic_calendar.reference == academic_calendar_type
    ]


def _format_date(obj, date_key, date_form) -> str:
    date = getattr(obj, date_key, None) if obj else None
    if date:
        return date.strftime(date_form)
    return '-'


def _is_valid_mandate(mandate, education_group_yr: EducationGroupYear):
    return mandate.start_date <= education_group_yr.academic_year.start_date and \
           mandate.end_date >= education_group_yr.academic_year.end_date


def names(representatives) -> str:
    return ', '.join(sorted(str(mandatory.person.full_name) for mandatory in representatives))


def qualification(signatories) -> str:
    return ', '.join(sorted(signatory.mandate.qualification for signatory in signatories
                            if signatory.mandate.qualification))


def has_coorganization(education_group_year: EducationGroupYear) -> bool:
    return education_group_year.education_group_type.category == "TRAINING" and \
           education_group_year.education_group_type.name not in [
               TrainingType.PGRM_MASTER_120.name,
               TrainingType.PGRM_MASTER_180_240.name
           ]


def _get_title(a_version, language):
    title = a_version.title_fr
    if language == LANGUAGE_CODE_EN and a_version.title_en:
        title = a_version.title_en

    return " [{}]".format(title) if title else ''


def create_customized_xls(user, found_education_groups_param, filters, order_data, other_params: List):
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
    """ At this stage, the group_year has been annotated with property complete_title_fr / full_title_fr"""

    training = _get_training(group_year.academic_year.year, group_year.acronym)

    node_identity = NodeIdentity(code=group_year.partial_acronym, year=group_year.academic_year.year)
    program_tree_version_identity = ProgramTreeVersionIdentitySearch().get_from_node_identity(node_identity)
    training_identity = TrainingIdentitySearch().get_from_program_tree_version_identity(program_tree_version_identity)
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
            data.append(_get_start_year(current_version, training, group_year, group))
            data.append(_get_end_year(current_version, training, group_year, group))
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
            data.append("{} - {}".format(group.teaching_campus.name,group.teaching_campus.university_name))
            if training.duration and training.duration_unit.value:
                data.append("{} {}".format(training.duration, training.duration_unit.value))
            else:
                data.append("")
        else:
            data.extend(add_empty_str(WITH_ORGANIZATION))

    if WITH_ACTIVITIES_ORGANIZATION in other_params:
        if group.is_training():
            data.append(training.other_campus_activities.value if training.other_campus_activities else '')
            data.append(training.internship_presence.value.title() if training.internship_presence else '')
            data.append(str(_('Yes')) if training.has_dissertation else str(_('No')))
            data.append(training.main_language.name if training.main_language else '')
            data.append(training.english_activities.value.title() if training.english_activities else '')
            data.append(training.other_language_activities.value.title() if training.other_language_activities else '')
        else:
            data.extend(add_empty_str(WITH_ACTIVITIES_ORGANIZATION))

    if WITH_RESPONSIBLES_AND_CONTACTS:
        if group.is_training():
            data.append(_get_responsibles_and_contacts(training, group, current_version))
        else:
            data.extend(add_empty_str(WITH_RESPONSIBLES_AND_CONTACTS))
    return data


def _build_customized_header(other_params):
    customized_header = DEFAULT_EDUCATION_GROUP_TITLES
    print(customized_header)
    for parameter in other_params:
        customized_header.extend(PARAMETER_HEADERS[parameter])
    return customized_header


def _get_training(year: int, acronym: str) -> 'Training':
    get_training_cmd = command.GetTrainingCommand(
        year=year,
        acronym=acronym
    )
    return get_training_service.get_training(get_training_cmd)


def add_empty_str(parameter):
    ch = []
    for occurence in PARAMETER_HEADERS[parameter]:
        ch.append('')
    return ch


def _get_start_year(current_version, training, group_year, group):
    if current_version.is_standard:
        return training.start_year
    else:
        return group.start_year


def _get_end_year(current_version, training, group_year, group):
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
            titles.extend('', '')
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


def _get_responsibles_and_contacts(training, group, current_version):
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
