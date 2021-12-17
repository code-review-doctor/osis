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
import json
import logging

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.views.generic import DetailView

from base import models as mdl
from base.business.institution import find_summary_course_submission_dates_for_entity_version
from base.models import entity
from base.models.academic_year import AcademicYear
from base.models.entity_version import EntityVersion
from learning_unit.calendar.learning_unit_summary_edition_calendar import LearningUnitSummaryEditionCalendar

logger = logging.getLogger(settings.DEFAULT_LOGGER)


class EntityRead(LoginRequiredMixin, DetailView):
    permission_required = 'perms.base.can_access_structure'
    raise_exception = True

    template_name = "entity/identification.html"

    pk_url_kwarg = "entity_version_id"
    context_object_name = "entity"

    model = EntityVersion

    def get(self, request, *args, **kwargs):
        entity_version_id = kwargs['entity_version_id']
        entity_version = get_object_or_404(EntityVersion, id=entity_version_id)
        return self._build_entity_read_render(entity_version, request)

    def _build_entity_read_render(self, entity_version, request):
        entity_parent = entity_version.get_parent_version()
        descendants = entity_version.descendants
        calendar = LearningUnitSummaryEditionCalendar()
        target_years_opened = calendar.get_target_years_opened()
        if target_years_opened:
            target_year_displayed = target_years_opened[0]
        else:
            previous_academic_event = calendar.get_previous_academic_event()
            target_year_displayed = previous_academic_event.authorized_target_year
        academic_year = AcademicYear.objects.get(year=target_year_displayed)
        calendar_summary_course_submission = find_summary_course_submission_dates_for_entity_version(
            entity_version=entity_version,
            ac_year=academic_year
        )
        context = {
            'entity_version': entity_version,
            'entity_parent': entity_parent,
            'descendants': descendants,
            'calendar_summary_course_submission': calendar_summary_course_submission
        }
        return render(request, self.template_name, context)


class EntityReadByAcronym(EntityRead):
    pk_url_kwarg = "entity_acronym"

    def get(self, request, *args, **kwargs):
        entity_acronym = kwargs['entity_acronym']
        results = entity.search(acronym=entity_acronym)
        if results:
            entity_version = results[0].most_recent_entity_version
        else:
            raise Http404('No EntityVersion matches the given query.')
        return self._build_entity_read_render(entity_version, request)


class EntityVersionsRead(PermissionRequiredMixin, DetailView):
    permission_required = 'perms.base.can_access_structure'
    raise_exception = True

    template_name = "entity/versions.html"

    pk_url_kwarg = "entity_version_id"
    context_object_name = "entity"

    model = EntityVersion

    def get(self, request, *args, **kwargs):
        entity_version_id = kwargs['entity_version_id']
        entity_version = mdl.entity_version.find_by_id(entity_version_id)
        entity_parent = entity_version.get_parent_version()
        entities_version = mdl.entity_version.search(entity=entity_version.entity) \
                                             .order_by('-start_date')
        return render(request, "entity/versions.html", locals())


class EntityDiagramRead(LoginRequiredMixin, DetailView):
    permission_required = 'perms.base.can_access_structure'
    raise_exception = True

    template_name = "entity/organogram.html"

    pk_url_kwarg = "entity_version_id"
    context_object_name = "entity"

    model = EntityVersion

    def get(self, request, *args, **kwargs):
        entity_version_id = kwargs['entity_version_id']
        entity_version = mdl.entity_version.find_by_id(entity_version_id)
        entities_version_as_json = json.dumps(entity_version.get_organigram_data())

        return render(
            request, "entity/organogram.html",
            {
                "entity_version": entity_version,
                "entities_version_as_json": entities_version_as_json,
            }
        )
