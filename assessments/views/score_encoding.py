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
import copy
import logging
import traceback

import pika
import pika.exceptions
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from django.core.exceptions import ValidationError
from django.db import close_old_connections, transaction
from django.db.utils import OperationalError as DjangoOperationalError, InterfaceError as DjangoInterfaceError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.views import View
from psycopg2._psycopg import OperationalError as PsycopOperationalError, InterfaceError as PsycopInterfaceError
from rules.contrib.views import LoginRequiredMixin

import base
from assessments.business import score_encoding_sheet
from assessments.views.program_manager.learning_unit_score_encoding import LearningUnitScoreEncodingProgramManagerView
from assessments.views.program_manager.learning_unit_score_encoding_form import \
    LearningUnitScoreEncodingProgramManagerFormView
from assessments.views.program_manager.score_encoding_progress_overview import \
    ScoreEncodingProgressOverviewProgramManagerView
from assessments.views.program_manager.score_sheet_pdf_export import ScoreSheetsPDFExportProgramManagerView
from assessments.views.program_manager.score_sheet_xls_export import ScoreSheetXLSExportProgramManagerView
from assessments.views.program_manager.score_sheet_xls_import import ScoreSheetXLSImportProgramManagerView
from assessments.views.tutor.learning_unit_score_encoding import LearningUnitScoreEncodingTutorView
from assessments.views.tutor.learning_unit_score_encoding_form import LearningUnitScoreEncodingTutorFormView
from assessments.views.tutor.score_encoding_progress_overview import ScoreEncodingProgressOverviewTutorView
from assessments.views.tutor.score_sheet_pdf_export import ScoreSheetsPDFExportTutorView
from assessments.views.tutor.score_sheet_xls_export import ScoreSheetXLSExportTutorView
from assessments.views.tutor.score_sheet_xls_import import ScoreSheetXLSImportTutorView
from base import models as mdl
from base.auth.roles import program_manager
from base.auth.roles import tutor as tutor_mdl
from base.auth.roles.program_manager import ProgramManager
from base.auth.roles.tutor import Tutor
from base.models import session_exam_calendar
from base.models.enums import exam_enrollment_state as enrollment_states, exam_enrollment_state
from base.models.person import Person
from base.utils import send_mail
from osis_common.document import paper_sheet
from osis_common.queue.queue_sender import send_message
from osis_role.contrib.helper import EntityRoleHelper

logger = logging.getLogger(settings.DEFAULT_LOGGER)
queue_exception_logger = logging.getLogger(settings.QUEUE_EXCEPTION_LOGGER)


def _is_inside_scores_encodings_period(user):
    return bool(mdl.session_exam_calendar.current_session_exam())


def _is_not_inside_scores_encodings_period(user):
    return not _is_inside_scores_encodings_period(user)


@login_required
@permission_required('base.can_access_evaluation', raise_exception=True)
def assessments(request):
    return render(request, "assessments.html", {'section': 'assessments'})


@login_required
@permission_required('assessments.can_access_scoreencoding', raise_exception=True)
@user_passes_test(_is_not_inside_scores_encodings_period, login_url=reverse_lazy('scores_encoding'))
def outside_period(request):
    date_format = str(_('date_format'))
    latest_session_exam = mdl.session_exam_calendar.get_latest_session_exam()
    closest_new_session_exam = mdl.session_exam_calendar.get_closest_new_session_exam()

    if latest_session_exam:
        month_session = latest_session_exam.month_session_name()
        str_date = latest_session_exam.end_date.strftime(date_format)
        messages.add_message(
            request,
            messages.WARNING,
            _("The period of scores' encoding for %(month_session)s session is closed since %(str_date)s")
            % {'month_session': month_session, 'str_date': str_date}
        )

    if closest_new_session_exam:
        month_session = closest_new_session_exam.month_session_name()
        str_date = closest_new_session_exam.start_date.strftime(date_format)
        messages.add_message(
            request,
            messages.WARNING,
            _("The period of scores' encoding for %(month_session)s session will be open %(str_date)s")
            % {'month_session': month_session, 'str_date': str_date}
        )

    if not messages.get_messages(request):
        messages.add_message(request, messages.WARNING, _("The period of scores' encoding is not opened"))
    return render(request, "outside_scores_encodings_period.html", {})


# TODO :: to remove ?
def get_json_data_scores_sheets(tutor_global_id):
    try:
        if isinstance(tutor_global_id, bytes):
            tutor_global_id = tutor_global_id.decode('utf-8')
        person = mdl.person.find_by_global_id(tutor_global_id)
        tutor = tutor_mdl.find_by_person(person)
        number_session = mdl.session_exam_calendar.find_session_exam_number()
        academic_yr = session_exam_calendar.current_opened_academic_year()

        if tutor:
            exam_enrollments = list(mdl.exam_enrollment.find_for_score_encodings(number_session,
                                                                                 tutor=tutor,
                                                                                 academic_year=academic_yr))
            return score_encoding_sheet.scores_sheet_data(exam_enrollments, tutor=tutor)
        else:

            return {}
    except (PsycopOperationalError, PsycopInterfaceError, DjangoOperationalError, DjangoInterfaceError):
        queue_exception_logger.error(
            'Postgres Error during get_json_data_scores_sheets on global_id {} => retried'.format(tutor_global_id)
        )
        trace = traceback.format_exc()
        queue_exception_logger.error(trace)
        return get_json_data_scores_sheets(tutor_global_id)
    except Exception:
        logger.warning('(Not PostgresError) during get_json_data_scores_sheets on global_id {}'.format(tutor_global_id))
        trace = traceback.format_exc()
        logger.error(trace)
        return {}
    finally:
        close_old_connections()


# TODO :: to remove ?
def send_json_scores_sheets_to_response_queue(global_id):
    data = get_json_data_scores_sheets(global_id)
    credentials = pika.PlainCredentials(settings.QUEUES.get('QUEUE_USER'),
                                        settings.QUEUES.get('QUEUE_PASSWORD'))
    rabbit_settings = pika.ConnectionParameters(settings.QUEUES.get('QUEUE_URL'),
                                                settings.QUEUES.get('QUEUE_PORT'),
                                                settings.QUEUES.get('QUEUE_CONTEXT_ROOT'),
                                                credentials)
    try:
        connect = pika.BlockingConnection(rabbit_settings)
        channel = connect.channel()
        queue_name = settings.QUEUES.get('QUEUES_NAME').get('SCORE_ENCODING_PDF_RESPONSE')
        send_message(queue_name, data, connect, channel)
    except (RuntimeError, pika.exceptions.ConnectionClosed, pika.exceptions.ChannelClosed, pika.exceptions.AMQPError):
        logger.exception('Could not send back scores_sheets json in response queue for global_id {}'.format(global_id))


def _get_count_still_enrolled(enrollments):
    nb_enrolled = 0
    for enrollment in enrollments:
        if enrollment.enrollment_state == enrollment_states.ENROLLED:
            nb_enrolled += 1
    return nb_enrolled


class LearningUnitScoreEncodingView(LoginRequiredMixin, View):
    @cached_property
    def person(self):
        return self.request.user.person

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if EntityRoleHelper.has_role(self.person, Tutor):
            return LearningUnitScoreEncodingTutorView.as_view()(request, *args, **kwargs)
        elif EntityRoleHelper.has_role(self.person, ProgramManager):
            return LearningUnitScoreEncodingProgramManagerView.as_view()(request, *args, **kwargs)
        return self.handle_no_permission()


class LearningUnitScoreEncodingFormView(LoginRequiredMixin, View):
    @cached_property
    def person(self):
        return self.request.user.person

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if EntityRoleHelper.has_role(self.person, Tutor):
            return LearningUnitScoreEncodingTutorFormView.as_view()(request, *args, **kwargs)
        elif EntityRoleHelper.has_role(self.person, ProgramManager):
            return LearningUnitScoreEncodingProgramManagerFormView.as_view()(request, *args, **kwargs)
        return self.handle_no_permission()


class ScoreSheetsPDFExportView(LoginRequiredMixin, View):
    @cached_property
    def person(self):
        return self.request.user.person

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if EntityRoleHelper.has_role(self.person, Tutor):
            return ScoreSheetsPDFExportTutorView.as_view()(request, *args, **kwargs)
        elif EntityRoleHelper.has_role(self.person, ProgramManager):
            return ScoreSheetsPDFExportProgramManagerView.as_view()(request, *args, **kwargs)
        return self.handle_no_permission()


class ScoreSheetXLSExportView(LoginRequiredMixin, View):
    @cached_property
    def person(self):
        return self.request.user.person

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if EntityRoleHelper.has_role(self.person, Tutor):
            return ScoreSheetXLSExportTutorView.as_view()(request, *args, **kwargs)
        elif EntityRoleHelper.has_role(self.person, ProgramManager):
            return ScoreSheetXLSExportProgramManagerView.as_view()(request, *args, **kwargs)
        return self.handle_no_permission()


class ScoreSheetXLSImportView(LoginRequiredMixin, View):
    @cached_property
    def person(self):
        return self.request.user.person

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if EntityRoleHelper.has_role(self.person, Tutor):
            return ScoreSheetXLSImportTutorView.as_view()(request, *args, **kwargs)
        elif EntityRoleHelper.has_role(self.person, ProgramManager):
            return ScoreSheetXLSImportProgramManagerView.as_view()(request, *args, **kwargs)
        return self.handle_no_permission()


class ScoreEncodingProgressOverviewView(LoginRequiredMixin, View):
    @cached_property
    def person(self):
        return self.request.user.person

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if EntityRoleHelper.has_role(self.person, Tutor):
            return ScoreEncodingProgressOverviewTutorView.as_view()(request, *args, **kwargs)
        elif EntityRoleHelper.has_role(self.person, ProgramManager):
            return ScoreEncodingProgressOverviewProgramManagerView.as_view()(request, *args, **kwargs)
        return self.handle_no_permission()
