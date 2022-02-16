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
import datetime
from typing import Union

from django import forms
from django.core.exceptions import ValidationError

from base.business.academic_calendar import AcademicSessionEvent, AcademicEventRepository, AcademicEvent
from base.forms.utils.datefield import DatePickerInput
from django.utils.translation import gettext_lazy as _

from base.models.enums.academic_calendar_type import AcademicCalendarTypes


class AcademicCalendarUpdateForm(forms.Form):
    start_date = forms.DateField(label=_("Start date"), widget=DatePickerInput())
    end_date = forms.DateField(widget=DatePickerInput(), label=_("End date"), required=False)

    def __init__(
            self,
            *args,
            academic_event: Union['AcademicEvent', 'AcademicSessionEvent'],
            academic_event_repository: 'AcademicEventRepository',
            **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.academic_event = academic_event
        self.academic_event_repository = academic_event_repository

    def clean(self):
        cleaned_data = self.cleaned_data
        if all([cleaned_data.get('end_date'), cleaned_data.get('start_date')]) \
                and cleaned_data['end_date'] < cleaned_data['start_date']:
            raise ValidationError({
                'end_date': _("%(max)s must be greater or equals than %(min)s") % {
                    "max": _("End date"),
                    "min": _("Start date"),
                }
            })
        attendance_mark_period_should_be_comprised_inside_score_encoding_period(
            self.academic_event,
            cleaned_data.get('start_date'),
            cleaned_data.get('end_date'),
            self.academic_event_repository
        )
        return cleaned_data


def attendance_mark_period_should_be_comprised_inside_score_encoding_period(
        academic_event: AcademicSessionEvent,
        new_start_date: datetime.date,
        new_end_date: datetime.date,
        academic_event_repository: AcademicEventRepository
):
    if academic_event.type != AcademicCalendarTypes.ATTENDANCE_MARK.name:
        return

    score_exam_submission_events = academic_event_repository.get_academic_events(
        AcademicCalendarTypes.SCORES_EXAM_SUBMISSION.name
    )
    score_exam_submission_event_for_same_session = next(
        (
            event
            for event in score_exam_submission_events
            if event.session == academic_event.session
            and event.authorized_target_year == academic_event.authorized_target_year
        ),
        None
    )

    if score_exam_submission_event_for_same_session is None or \
            score_exam_submission_event_for_same_session.start_date > new_start_date or \
            score_exam_submission_event_for_same_session.end_date < new_end_date:
        raise ValidationError(_(
                "The start date cannot be lower than the score encoding start date and "
                "the end date cannot be greater than the score encoding end date"
        ))
