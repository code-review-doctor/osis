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

"""
Utility files for mail sending
"""
import datetime

from django.contrib.auth.models import Permission
from django.contrib.messages import ERROR
from django.db.models import Q
from django.utils import translation
from django.utils.translation import gettext as _
from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook

from base.models.enums import proposal_type
from base.models.person import Person
from osis_common.document import xls_build
from osis_common.document.xls_build import _adjust_column_width
from osis_common.messaging import message_config, send_message as message_service

EDUCATIONAL_INFORMATION_UPDATE_TXT = 'educational_information_update_txt'

EDUCATIONAL_INFORMATION_UPDATE_HTML = 'educational_information_update_html'

ASSESSMENTS_SCORES_SUBMISSION_MESSAGE_TEMPLATE = "assessments_scores_submission"
ASSESSMENTS_ALL_SCORES_BY_PGM_MANAGER = "assessments_all_scores_by_pgm_manager"


def send_mail_after_the_learning_unit_year_deletion(managers, acronym: str, academic_year, msg_list):
    html_template_ref = 'learning_unit_year_deletion_html'
    txt_template_ref = 'learning_unit_year_deletion_txt'
    receivers = [message_config.create_receiver(manager.id, manager.email, manager.language) for manager in managers]
    suject_data = {'learning_unit_acronym': acronym}
    template_base_data = {'learning_unit_acronym': acronym,
                          'academic_year': academic_year,
                          'msg_list': msg_list,
                          }
    message_content = message_config.create_message_content(html_template_ref, txt_template_ref, None, receivers,
                                                            template_base_data, suject_data, None)
    return message_service.send_messages(message_content)


def send_mail_before_annual_procedure_of_automatic_postponement_of_luy(statistics_context: dict):
    html_template_ref = 'luy_before_auto_postponement_html'
    txt_template_ref = 'luy_before_auto_postponement_txt'

    permission = Permission.objects.get(codename='can_receive_emails_about_automatic_postponement')
    managers = Person.objects.filter(Q(user__groups__permissions=permission) | Q(user__user_permissions=permission)) \
        .distinct()

    receivers = [message_config.create_receiver(manager.id, manager.email, manager.language) for manager in managers]
    template_base_data = {
        'academic_year': statistics_context['max_academic_year_to_postpone'].past(),
        'end_academic_year': statistics_context['max_academic_year_to_postpone'],

        # Use len instead of count() (it's buggy when a queryset is built with a difference())
        'luys_to_postpone': len(statistics_context['to_duplicate']),
        'luys_already_existing': statistics_context['already_duplicated'].count(),
        'luys_ending_this_year': statistics_context['ending_on_max_academic_year'].count(),
    }
    message_content = message_config.create_message_content(html_template_ref, txt_template_ref, None, receivers,
                                                            template_base_data, None, None)
    return message_service.send_messages(message_content)


def send_mail_after_annual_procedure_of_automatic_postponement_of_luy(
        statistics_context: dict, luys_postponed: list, luys_with_errors: list):
    html_template_ref = 'luy_after_auto_postponement_html'
    txt_template_ref = 'luy_after_auto_postponement_txt'

    permission = Permission.objects.get(codename='can_receive_emails_about_automatic_postponement')
    managers = Person.objects.filter(
        Q(user__groups__permissions=permission) | Q(user__user_permissions=permission)
    ).distinct()

    receivers = [message_config.create_receiver(manager.id, manager.email, manager.language) for manager in managers]
    template_base_data = {
        'academic_year':  statistics_context['max_academic_year_to_postpone'].past(),
        'end_academic_year': statistics_context['max_academic_year_to_postpone'],
        'luys_postponed': len(luys_postponed),
        'luys_postponed_qs': sorted(luys_postponed, key=lambda luy: luy.acronym),
        'luys_already_existing': statistics_context['already_duplicated'].count(),
        'luys_already_existing_qs': statistics_context['already_duplicated'].order_by("learningunityear__acronym"),
        'luys_ending_this_year': statistics_context['ending_on_max_academic_year'].count(),
        'luys_ending_this_year_qs': statistics_context['ending_on_max_academic_year'].order_by(
            "learningunityear__acronym"
        ),
        'luys_with_errors': luys_with_errors
    }
    message_content = message_config.create_message_content(html_template_ref, txt_template_ref, None, receivers,
                                                            template_base_data, None, None)
    return message_service.send_messages(message_content)


def send_mail_cancellation_learning_unit_proposals(manager, tuple_proposals_results, research_criteria):
    html_template_ref = 'learning_unit_proposal_canceled_html'
    txt_template_ref = 'learning_unit_proposal_canceled_txt'
    return _send_mail_action_learning_unit_proposal(manager, tuple_proposals_results, html_template_ref,
                                                    txt_template_ref, "cancellation", research_criteria)


def send_mail_consolidation_learning_unit_proposal(manager, tuple_proposals_results, research_criteria):
    html_template_ref = 'learning_unit_proposal_consolidated_html'
    txt_template_ref = 'learning_unit_proposal_consolidated_txt'
    return _send_mail_action_learning_unit_proposal(manager, tuple_proposals_results, html_template_ref,
                                                    txt_template_ref, "consolidation", research_criteria)


def _send_mail_action_learning_unit_proposal(manager, tuple_proposals_results, html_template_ref, txt_template_ref,
                                             operation, research_criteria):
    receivers = [message_config.create_receiver(manager.id, manager.email, manager.language)]
    suject_data = {}
    template_base_data = {
        "first_name": manager.first_name,
        "last_name": manager.last_name
    }
    attachment = ("report.xlsx",
                  build_proposal_report_attachment(manager, tuple_proposals_results, operation, research_criteria),
                  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    message_content = message_config.create_message_content(html_template_ref, txt_template_ref, None, receivers,
                                                            template_base_data, suject_data, attachment=attachment)
    return message_service.send_messages(message_content)


# FIXME should be moved to osis_common
def build_proposal_report_attachment(manager, proposals_with_results, operation, research_criteria):
    table_data = _build_table_proposal_data(proposals_with_results)

    xls_parameters = {
        xls_build.LIST_DESCRIPTION_KEY: "Liste d'activités",
        xls_build.FILENAME_KEY: 'Learning_units',
        xls_build.USER_KEY: str(manager),
        xls_build.WORKSHEETS_DATA: [
            {
                xls_build.CONTENT_KEY: table_data,
                xls_build.HEADER_TITLES_KEY: [_('Ac yr.'), _('Code'), _('Title'), _('Type'),
                                              _("Proposal status"), _('Status'), _('Reason for failure')],
                xls_build.WORKSHEET_TITLE_KEY: 'Report'
            }
        ],
        "operation": operation,
        "research_criteria": research_criteria
    }

    return _create_xls(xls_parameters)


def _build_table_proposal_data(proposals_with_results):
    return [
        (
            proposal.learning_unit_year.academic_year.name,
            proposal.learning_unit_year.acronym,
            proposal.learning_unit_year.get_learning_unit_previous_year().complete_title
            if proposal.type == proposal_type.ProposalType.SUPPRESSION.name
            else proposal.learning_unit_year.complete_title,
            proposal.get_type_display(),
            proposal.get_state_display(),
            _("Success") if ERROR not in results else _("Failure"),
            "".join([str(error_msg) for error_msg in results.get(ERROR, [])])
        ) for (proposal, results) in proposals_with_results
    ]


# FIXME should be moved to osis_common
def _create_xls(parameters_dict):
    workbook = Workbook(encoding='utf-8')
    sheet_number = 0
    for worksheet_data in parameters_dict.get(xls_build.WORKSHEETS_DATA):
        xls_build._build_worksheet(worksheet_data, workbook, sheet_number)
        sheet_number = sheet_number + 1

    _build_worksheet_parameters(workbook, parameters_dict.get(xls_build.USER_KEY),
                                parameters_dict.get("operation", ""), parameters_dict.get("research_criteria"))
    return save_virtual_workbook(workbook)


# FIXME should be moved to osis_common
def _build_worksheet_parameters(workbook, a_user, operation, research_criteria):
    worksheet_parameters = workbook.create_sheet(title=str(_('parameters')))
    now = datetime.datetime.now()
    worksheet_parameters.append([str(_('author')), str(a_user)])
    worksheet_parameters.append([str(_('Date')), now.strftime('%d-%m-%Y %H:%M')])
    worksheet_parameters.append([_('Operation'), _(operation)])
    if research_criteria:
        worksheet_parameters.append([_('Research criteria')])
        for research_key, research_value in research_criteria:
            worksheet_parameters.append(["", research_key, str(research_value)])

    _adjust_column_width(worksheet_parameters)
    return worksheet_parameters


def send_mail_for_educational_information_update(teachers, learning_units_years):
    html_template_ref = EDUCATIONAL_INFORMATION_UPDATE_HTML
    txt_template_ref = EDUCATIONAL_INFORMATION_UPDATE_TXT
    receivers = [message_config.create_receiver(teacher.id, teacher.email, teacher.language) for teacher in teachers]
    template_base_data = {'learning_unit_years': learning_units_years}

    message_content = message_config.create_message_content(html_template_ref, txt_template_ref, None, receivers,
                                                            template_base_data, {}, None)
    return message_service.send_messages(message_content)


def get_enrollment_headers(lang_code):
    with translation.override(lang_code):
        return [
            translation.pgettext('Submission email table header', 'Program'),
            translation.pgettext('Submission email table header', 'Session number'),
            translation.pgettext('Submission email table header', 'Registration number'),
            _('Name'),
            _('Score'),
            _('Justification')
        ]


def _get_encoding_status(language, all_encoded):
    message = 'All the scores are encoded.' if all_encoded else 'It remains notes to encode.'
    with translation.override(language):
        return translation.gettext(message)


def _get_txt_complementary_first_col_header(lang_code):
    with translation.override(lang_code):
        return _('Updated')
