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
from assessments.business import score_encoding_progress, score_encoding_list
from assessments.business import score_encoding_sheet
from assessments.models import score_sheet_address as score_sheet_address_mdl
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
from attribution import models as mdl_attr
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


@login_required
@permission_required('assessments.can_access_scoreencoding', raise_exception=True)
@user_passes_test(_is_inside_scores_encodings_period, login_url=reverse_lazy('outside_scores_encodings_period'))
def scores_encoding(request):
    template_name = "scores_encoding.html"
    academic_yr = session_exam_calendar.current_opened_academic_year()
    number_session = mdl.session_exam_calendar.find_session_exam_number()
    score_encoding_progress_list = None
    context = {'academic_year': academic_yr,
               'number_session': number_session,
               'active_tab': request.GET.get('active_tab')}

    education_group_year_id = request.GET.get('offer', None)
    if education_group_year_id:
        education_group_year_id = int(education_group_year_id)

    if program_manager.is_program_manager(request.user):
        template_name = "scores_encoding_by_learning_unit.html"
        NOBODY = -1

        tutor_id = request.GET.get('tutor')
        if tutor_id:
            tutor_id = int(tutor_id)
        learning_unit_year_acronym = request.GET.get('learning_unit_year_acronym')
        incomplete_encodings_only = request.GET.get('incomplete_encodings_only', False)

        # Manage filter
        learning_unit_year_ids = None
        if learning_unit_year_acronym:
            learning_unit_year_acronym = learning_unit_year_acronym.strip() \
                if isinstance(learning_unit_year_acronym, str) \
                else learning_unit_year_acronym
            learning_unit_year_ids = list(
                mdl.learning_unit_year.search(
                    academic_year_id=academic_yr.id,
                    acronym=learning_unit_year_acronym
                ).values_list('id', flat=True)
            )
        if tutor_id and tutor_id != NOBODY:
            learning_unit_year_ids_filter_by_tutor = mdl_attr.attribution.search(
                tutor=tutor_id, list_learning_unit_year=learning_unit_year_ids
            ).distinct('learning_unit_year').values_list('learning_unit_year_id', flat=True)

            learning_unit_year_ids = list(learning_unit_year_ids_filter_by_tutor)

        score_encoding_progress_list = score_encoding_progress.get_scores_encoding_progress(
            user=request.user,
            education_group_year_id=education_group_year_id,
            number_session=number_session,
            academic_year=academic_yr,
            learning_unit_year_ids=learning_unit_year_ids
        )

        score_encoding_progress_list = score_encoding_progress. \
            append_related_tutors_and_score_responsibles(score_encoding_progress_list)

        score_encoding_progress_list = score_encoding_progress.group_by_learning_unit_year(score_encoding_progress_list)

        if incomplete_encodings_only:
            score_encoding_progress_list = score_encoding_progress.filter_only_incomplete(score_encoding_progress_list)

        if tutor_id == NOBODY:
            score_encoding_progress_list = score_encoding_progress. \
                filter_only_without_attribution(score_encoding_progress_list)

        all_tutors = score_encoding_progress.find_related_tutors(request.user, academic_yr, number_session)

        all_offers = mdl.education_group_year.find_by_user(request.user, academic_yr=academic_yr).order_by('acronym')

        if not score_encoding_progress_list:
            messages.add_message(request, messages.WARNING, _('No result!'))

        context.update({'offer_list': all_offers,
                        'tutor_list': all_tutors,
                        'education_group_year_id': education_group_year_id,
                        'tutor_id': tutor_id,
                        'learning_unit_year_acronym': learning_unit_year_acronym,
                        'incomplete_encodings_only': incomplete_encodings_only,
                        'last_synchronization': mdl.synchronization.find_last_synchronization_date()})

    elif tutor_mdl.is_tutor(request.user):
        tutor = tutor_mdl.find_by_user(request.user)
        score_encoding_progress_list = score_encoding_progress.get_scores_encoding_progress(
            user=request.user,
            education_group_year_id=None,
            number_session=number_session,
            academic_year=academic_yr
        )
        education_group_year_list = score_encoding_progress.find_related_education_group_years(
            score_encoding_progress_list
        )
        if education_group_year_id:
            score_encoding_progress_list = [
                score_encoding for score_encoding in score_encoding_progress_list
                if score_encoding.education_group_year_id == education_group_year_id
            ]

        score_encoding_progress_list = score_encoding_progress.group_by_learning_unit_year(score_encoding_progress_list)

        context.update({'tutor': tutor,
                        'education_group_year_list': education_group_year_list,
                        'education_group_year_id': education_group_year_id})

    context.update({
        'notes_list': score_encoding_progress_list
    })

    return render(request, template_name, context)


@login_required
@permission_required('assessments.can_access_scoreencoding', raise_exception=True)
@user_passes_test(_is_inside_scores_encodings_period, login_url=reverse_lazy('outside_scores_encodings_period'))
def online_encoding(request, learning_unit_year_id=None):
    template_name = "online_encoding.html"
    context = _get_common_encoding_context(request, learning_unit_year_id)
    return render(request, template_name, context)


@login_required
@permission_required('assessments.can_access_scoreencoding', raise_exception=True)
@user_passes_test(_is_inside_scores_encodings_period, login_url=reverse_lazy('outside_scores_encodings_period'))
@transaction.non_atomic_requests
def online_encoding_form(request, learning_unit_year_id=None):
    template_name = "online_encoding_form.html"
    if request.method == 'POST':
        scores_list_before_update = score_encoding_list.get_scores_encoding_list(
            user=request.user,
            learning_unit_year_id=learning_unit_year_id
        )

        updated_enrollments = None
        encoded_enrollment_ids = _extract_id_from_post_data(request)
        # Get only encoded from database
        scores_list_encoded = score_encoding_list.get_scores_encoding_list(
            user=request.user,
            learning_unit_year_id=learning_unit_year_id,
            enrollments_ids=encoded_enrollment_ids)
        # Append value encoded by user
        scores_list_encoded.enrollments = _extract_encoded_values_from_post_data(
            request,
            scores_list_encoded.enrollments)

        updated_enrollments = _update_enrollments(request, scores_list_encoded, updated_enrollments)

        context = _get_common_encoding_context(request, learning_unit_year_id)
        if messages.get_messages(request):
            context = _preserve_encoded_values(request, context)
        else:
            template_name = "online_encoding.html"
            send_messages_to_notify_encoding_progress(
                all_enrollments=context["enrollments"],
                learning_unit_year=context["learning_unit_year"],
                is_program_manager=context["is_program_manager"],
                updated_enrollments=updated_enrollments,
                pgm_manager=mdl.person.find_by_user(request.user),
                encoding_already_completed_before_update=scores_list_before_update.
                educ_groups_which_encoding_was_complete_before_update
            )
    else:
        context = _get_common_encoding_context(request, learning_unit_year_id)
    return render(request, template_name, context)


@login_required
@permission_required('assessments.can_access_scoreencoding', raise_exception=True)
@user_passes_test(_is_inside_scores_encodings_period, login_url=reverse_lazy('outside_scores_encodings_period'))
@transaction.non_atomic_requests
def online_encoding_submission(request, learning_unit_year_id):
    scores_list = score_encoding_list.get_scores_encoding_list(user=request.user,
                                                               learning_unit_year_id=learning_unit_year_id)
    submitted_enrollments = []
    draft_scores_not_sumitted_yet = scores_list.remaining_drafts_to_submit_before_deadlines
    not_submitted_enrollments = set([
        ex for ex in scores_list.enrollments
        if not ex.is_final and ex.enrollment_state == exam_enrollment_state.ENROLLED
    ])
    for exam_enroll in draft_scores_not_sumitted_yet:
        if (exam_enroll.score_draft is not None and exam_enroll.score_final is None) \
                or (exam_enroll.justification_draft and not exam_enroll.justification_final):
            submitted_enrollments.append(exam_enroll)
            not_submitted_enrollments.remove(exam_enroll)
        if exam_enroll.is_draft:
            if exam_enroll.score_draft is not None:
                exam_enroll.score_final = exam_enroll.score_draft
            if exam_enroll.justification_draft:
                exam_enroll.justification_final = exam_enroll.justification_draft
            exam_enroll.full_clean()
            with transaction.atomic():
                exam_enroll.save()
                mdl.exam_enrollment.create_exam_enrollment_historic(request.user, exam_enroll)

    # Send mail to all the teachers of the submitted learning unit on any submission
    all_encoded = len(not_submitted_enrollments) == 0
    learning_unit_year = mdl.learning_unit_year.get_by_id(learning_unit_year_id)
    attributions = mdl_attr.attribution.Attribution.objects.filter(learning_unit_year=learning_unit_year)
    persons = list(set([attribution.tutor.person for attribution in attributions]))
    send_mail.send_mail_after_scores_submission(persons, learning_unit_year.acronym, submitted_enrollments, all_encoded)
    return HttpResponseRedirect(reverse('online_encoding', args=(learning_unit_year_id,)))


def _update_enrollments(request, scores_list_encoded, updated_enrollments):
    try:
        updated_enrollments = score_encoding_list.update_enrollments(
            scores_encoding_list=scores_list_encoded,
            user=request.user)
    except Exception as e:
        error_msg = e.messages[0] if isinstance(e, ValidationError) else e.args[0]
        messages.add_message(request, messages.ERROR, _(error_msg))
    return updated_enrollments


def __send_messages_for_each_education_group_year(
        all_enrollments,
        learning_unit_year,
        updated_enrollments,
        pgm_manager: mdl.person.Person,
        encoding_already_completed_before_update: bool
):
    """
    Send a message for each education group year to all the tutors of a learning unit inside a program
    managed by the program manager if all the scores
    of this learning unit, inside this program, are encoded and at most one score is newly encoded.
    Th encoder is a program manager, so all the encoded scores are final.
    :param all_enrollments: The enrollments to the learning unit year , inside the managed program.
    :param learning_unit_year: The learning unit year of the enrollments.
    :param updated_enrollments: list of exam enrollments objects which has been updated
    :param pgm_manager: The program manager (current logged user) that has encoded scores.
    :param encoding_already_completed_before_update: Before update encoding was already complete.
    :return: A list of error message if message cannot be sent
    """
    sent_error_messages = []
    education_group_years = [
        enrollment.learning_unit_enrollment.offer_enrollment.education_group_year
        for enrollment in updated_enrollments
    ]
    education_group_ids = {education_group_year.education_group_id for education_group_year in education_group_years}
    score_sheet_addresses = score_sheet_address_mdl.search_from_education_group_ids(education_group_ids)
    for education_group_year in set(education_group_years):
        score_sheet_address = next(
            (
                score_sheet_address for score_sheet_address in score_sheet_addresses
                if score_sheet_address.education_group_id == education_group_year.education_group_id
            ),
            None
        )
        sent_error_message = __send_message_for_education_group_year(
            all_enrollments,
            learning_unit_year,
            education_group_year,
            pgm_manager=pgm_manager,
            encoding_already_completed_before_update=encoding_already_completed_before_update,
            score_sheet_address=score_sheet_address,
            updated_enrollments=updated_enrollments
        )
        if sent_error_message:
            sent_error_messages.append(sent_error_message)
    return sent_error_messages


def __send_message_for_education_group_year(
        all_enrollments,
        learning_unit_year,
        education_group_year,
        pgm_manager: mdl.person.Person,
        encoding_already_completed_before_update: bool,
        score_sheet_address: score_sheet_address_mdl.ScoreSheetAddress = None,
        updated_enrollments=None,
):
    enrollments = filter_enrollments_by_education_group_year(all_enrollments, education_group_year)
    progress = mdl.exam_enrollment.calculate_exam_enrollment_progress(enrollments)
    offer_acronym = education_group_year.acronym
    # TODO :: fix here
    sent_error_message = None
    if progress == 100:
        receivers = list(
            set([tutor.person for tutor in tutor_mdl.find_by_learning_unit(learning_unit_year)])
        )
        cc_list = [pgm_manager]
        if score_sheet_address and score_sheet_address.email:
            # Todo: Refactor CC list must not be a person but a list of email...
            cc_list.append(Person(email=score_sheet_address.email))
        updated_enrollments_ids = [enrollment.id for enrollment in updated_enrollments]
        sent_error_message = send_mail.send_message_after_all_encoded_by_manager(
            receivers,
            enrollments,
            learning_unit_year.acronym,
            offer_acronym,
            updated_enrollments_ids,
            encoding_already_completed_before_update=encoding_already_completed_before_update,
            cc=cc_list
        )
    return sent_error_message


def filter_enrollments_by_education_group_year(enrollments, education_group_year):
    filtered_enrollments = filter(
        lambda enrol: enrol.learning_unit_enrollment.offer_enrollment.education_group_year == education_group_year,
        enrollments
    )
    return list(filtered_enrollments)


def _preserve_encoded_values(request, data):
    data = copy.deepcopy(data)
    is_program_manager = data['is_program_manager']
    for enrollment in data['enrollments']:
        enrollment.score_draft = request.POST.get('score_' + str(enrollment.id))
        enrollment.justification_draft = request.POST.get('justification_' + str(enrollment.id))
        if is_program_manager:
            enrollment.score_final = request.POST.get('score_' + str(enrollment.id))
            enrollment.justification_final = request.POST.get('justification_' + str(enrollment.id))
    return data


def _extract_id_from_post_data(request):
    post_data = dict(request.POST.lists())
    return [int(param.split("_")[-1]) for param, value in post_data.items()
            if "score_changed_" in param and next(iter(value or []), None) == "true"]


def _extract_encoded_values_from_post_data(request, enrollments):
    enrollment_with_encoded_values = copy.deepcopy(enrollments)
    for enrollment in enrollment_with_encoded_values:
        enrollment.score_encoded = request.POST.get('score_' + str(enrollment.id))
        enrollment.justification_encoded = request.POST.get('justification_' + str(enrollment.id))
    return enrollment_with_encoded_values


def send_messages_to_notify_encoding_progress(
        all_enrollments,
        learning_unit_year,
        is_program_manager,
        updated_enrollments,
        pgm_manager: mdl.person.Person,
        encoding_already_completed_before_update: bool
):
    if is_program_manager:
        __send_messages_for_each_education_group_year(
            all_enrollments,
            learning_unit_year,
            updated_enrollments,
            pgm_manager,
            encoding_already_completed_before_update
        )


def _get_common_encoding_context(request, learning_unit_year_id):
    scores_list = score_encoding_list.get_scores_encoding_list(user=request.user,
                                                               learning_unit_year_id=learning_unit_year_id)
    score_responsibles = mdl_attr.attribution.find_all_responsibles_by_learning_unit_year(
        scores_list.learning_unit_year
    )
    tutors = tutor_mdl.find_by_learning_unit(scores_list.learning_unit_year) \
        .exclude(id__in=[score_responsible.id for score_responsible in score_responsibles])
    is_coordinator = mdl_attr.attribution.is_score_responsible(request.user, scores_list.learning_unit_year)
    is_program_manager = program_manager.is_program_manager(request.user)

    context = {
        'section': 'scores_encoding',
        'is_program_manager': is_program_manager,
        'score_responsibles': list(score_responsibles),
        'tutors': list(tutors),
        'is_coordinator': is_coordinator,
        'draft_scores_not_submitted': len(scores_list.remaining_drafts_to_submit_before_deadlines),
        'exam_enrollments_encoded': len(scores_list.enrollment_encoded),
        'total_exam_enrollments': _get_count_still_enrolled(scores_list.enrollments),
        'progress': scores_list.progress,
        'progress_int': scores_list.progress_int
    }
    context.update(scores_list.__dict__)
    return context


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
