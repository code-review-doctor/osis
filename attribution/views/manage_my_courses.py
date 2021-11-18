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
import itertools
from datetime import datetime
from typing import Iterable

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from django.utils.translation import gettext as _
from django.views.decorators.http import require_http_methods
from django.views.generic import TemplateView

from base.auth.roles.tutor import Tutor
from base.models.learning_unit_year import LearningUnitYear
from base.views import teaching_material
from base.views.learning_unit import get_specifications_context, get_achievements_group_by_language, \
    get_languages_settings
from base.views.learning_units.pedagogy.read import read_learning_unit_pedagogy
from base.views.learning_units.pedagogy.update import edit_learning_unit_pedagogy, \
    post_method_edit_force_majeure_pedagogy
from education_group.templatetags.academic_year_display import display_as_academic_year
from learning_unit.calendar.learning_unit_force_majeur_summary_edition import \
    LearningUnitForceMajeurSummaryEditionCalendar
from learning_unit.calendar.learning_unit_summary_edition_calendar import LearningUnitSummaryEditionCalendar
from learning_unit.views.utils import learning_unit_year_getter
from osis_role.contrib.views import permission_required


class MyAttributionsSummaryEditable(LoginRequiredMixin, TemplateView):
    template_name = 'manage_my_courses/list_my_courses_summary_editable.html'

    @cached_property
    def tutor(self):
        return get_object_or_404(Tutor, person__user=self.request.user)

    @cached_property
    def learning_unit_years(self):
        return LearningUnitYear.objects_with_container.filter(
            academic_year__year=self.year,
            learningcomponentyear__attributionchargenew__attribution__tutor=self.tutor
        ).select_related(
            'academic_year',
            'learning_container_year__requirement_entity'
        ).distinct().order_by(
            'academic_year__year',
            'acronym'
        )

    @cached_property
    def summary_edition_calendar(self):
        return LearningUnitSummaryEditionCalendar()

    @cached_property
    def force_majeur_summary_edition_calendar(self):
        return LearningUnitForceMajeurSummaryEditionCalendar()

    @cached_property
    def summary_edition_academic_events_opened(self):
        return self.summary_edition_calendar.get_opened_academic_events()

    @cached_property
    def force_majeure_academic_events_opened(self):
        return self.force_majeur_summary_edition_calendar.get_opened_academic_events()

    @cached_property
    def year(self):
        if self.summary_edition_academic_events_opened or self.force_majeure_academic_events_opened:
            event_based = min(
                self.summary_edition_academic_events_opened + self.force_majeure_academic_events_opened,
                key=lambda event: event.authorized_target_year
            )
            return event_based.authorized_target_year
        return datetime.today().year

    @cached_property
    def main_summary_edition_academic_event(self):
        main_summary_edition_academic_event = next(
            (event for event in self.summary_edition_academic_events_opened if
             event.authorized_target_year == self.year),
            None
        )
        if not main_summary_edition_academic_event:
            main_summary_edition_academic_event = self.summary_edition_calendar.get_academic_event(self.year)
            if not main_summary_edition_academic_event.is_open_now():
                messages.add_message(
                    self.request,
                    messages.INFO,
                    _('For the academic year %(data_year)s, the summary edition period ended on %(end_date)s.') % {
                        "data_year": display_as_academic_year(
                            main_summary_edition_academic_event.authorized_target_year
                        ),
                        "end_date": main_summary_edition_academic_event.end_date.strftime('%d/%m/%Y'),
                    }
                )
            next_summary_edition_academic_event = self.summary_edition_calendar.get_academic_event(self.year + 1)
            if next_summary_edition_academic_event and not next_summary_edition_academic_event.is_open_now():
                messages.add_message(
                    self.request,
                    messages.INFO,
                    _('For the academic year %(data_year)s, the summary edition period will open on %(start_date)s.') %
                    {
                        "data_year": display_as_academic_year(
                            next_summary_edition_academic_event.authorized_target_year
                        ),
                        "start_date": next_summary_edition_academic_event.start_date.strftime('%d/%m/%Y'),
                    }
                )
        return main_summary_edition_academic_event

    @cached_property
    def force_majeure_academic_event(self):
        force_majeure_academic_event = next(
            (event for event in self.force_majeure_academic_events_opened if event.authorized_target_year == self.year),
            None
        )
        if force_majeure_academic_event:
            messages.add_message(
                self.request,
                messages.WARNING,
                _('Force majeure case : Some fields of the description fiche can be edited from %(start_date)s '
                  'to %(end_date)s.') % {
                    "start_date": force_majeure_academic_event.start_date.strftime('%d/%m/%Y'),
                    "end_date": force_majeure_academic_event.end_date.strftime('%d/%m/%Y'),
                }
            )
        else:
            force_majeure_academic_event = self.force_majeur_summary_edition_calendar.get_academic_event(
                target_year=self.main_summary_edition_academic_event.authorized_target_year
            )
        return force_majeure_academic_event

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            'learning_unit_years': self.learning_unit_years,
            'summary_edition_academic_event': self.main_summary_edition_academic_event,
            'force_majeure_academic_event': self.force_majeure_academic_event,
        }


@login_required
@permission_required('base.can_access_learningunit_pedagogy', fn=learning_unit_year_getter, raise_exception=True)
def view_educational_information(request, learning_unit_year_id):
    context = {
        'create_teaching_material_urlname': 'tutor_teaching_material_create',
        'update_teaching_material_urlname': 'tutor_teaching_material_edit',
        'delete_teaching_material_urlname': 'tutor_teaching_material_delete',
        'update_mobility_modality_urlname': 'tutor_mobility_modality_update'
    }
    template = 'manage_my_courses/educational_information.html'
    query_set = LearningUnitYear.objects.all().select_related(
        'learning_unit', 'learning_container_year', 'academic_year'
    )
    learning_unit_year = get_object_or_404(query_set, pk=learning_unit_year_id)

    context.update(get_specifications_context(learning_unit_year, request))
    context['submission_dates'] = LearningUnitSummaryEditionCalendar().get_academic_event(
        learning_unit_year.academic_year.year
    )
    context['force_majeure_submission_dates'] = LearningUnitForceMajeurSummaryEditionCalendar().get_academic_event(
        learning_unit_year.academic_year.year
    )
    context["achievements"] = _fetch_achievements_by_language(learning_unit_year)
    context.update(get_languages_settings())
    context['div_class'] = 'collapse'
    return read_learning_unit_pedagogy(request, learning_unit_year_id, context, template)


def _fetch_achievements_by_language(learning_unit_year: LearningUnitYear) -> Iterable:
    fr_achievement_code = "achievements_FR"
    en_achievement_code = "achievements_EN"
    achievements = get_achievements_group_by_language(learning_unit_year)
    return itertools.zip_longest(achievements.get(fr_achievement_code, []), achievements.get(en_achievement_code, []))


@login_required
@permission_required('base.can_edit_learningunit_pedagogy', fn=learning_unit_year_getter, raise_exception=True)
def edit_educational_information(request, learning_unit_year_id):
    return edit_learning_unit_pedagogy(request, learning_unit_year_id)


@login_required
@permission_required('base.can_edit_learningunit_pedagogy_force_majeur', fn=learning_unit_year_getter,
                     raise_exception=True)
def edit_educational_information_force_majeure(request, learning_unit_year_id):
    if request.method == 'POST':
        return post_method_edit_force_majeure_pedagogy(request)
    return edit_learning_unit_pedagogy(request, learning_unit_year_id)


@login_required
@require_http_methods(['POST', 'GET'])
@permission_required('base.can_edit_learningunit_pedagogy', fn=learning_unit_year_getter, raise_exception=True)
def create_teaching_material(request, learning_unit_year_id):
    return teaching_material.create_view(request, learning_unit_year_id)


@login_required
@require_http_methods(['POST', 'GET'])
@permission_required('base.can_edit_learningunit_pedagogy', fn=learning_unit_year_getter, raise_exception=True)
def update_teaching_material(request, learning_unit_year_id, teaching_material_id):
    return teaching_material.update_view(request, learning_unit_year_id, teaching_material_id)


@login_required
@require_http_methods(['POST', 'GET'])
@permission_required('base.can_edit_learningunit_pedagogy', fn=learning_unit_year_getter, raise_exception=True)
def delete_teaching_material(request, learning_unit_year_id, teaching_material_id):
    return teaching_material.delete_view(request, learning_unit_year_id, teaching_material_id)
