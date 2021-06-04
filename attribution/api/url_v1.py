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
from django.urls import path, include

from attribution.api.views.application import ApplicationUpdateDeleteView, ApplicationListCreateView, \
    RenewAttributionsAboutToExpire, SendApplicationsSummary
from attribution.api.views.vacant_course import VacantCourseListView
from attribution.api.views.attribution import AttributionListView, MyAttributionListView
from attribution.api.views.calendar import ApplicationCoursesCalendarListView

app_name = "attribution"
urlpatterns = [
    path('application/', include([
        path('calendars', ApplicationCoursesCalendarListView.as_view(), name=ApplicationCoursesCalendarListView.name),
        path('vacant_courses', VacantCourseListView.as_view(), name=VacantCourseListView.name),
        path('renewal', RenewAttributionsAboutToExpire.as_view(), name=RenewAttributionsAboutToExpire.name),
        path('<str:application_uuid>/', ApplicationUpdateDeleteView.as_view(), name=ApplicationUpdateDeleteView.name),
        path('send_summary', SendApplicationsSummary.as_view(), name=SendApplicationsSummary.name),
        path('', ApplicationListCreateView.as_view(), name=ApplicationListCreateView.name),
    ])),

    path('<int:year>/me/', MyAttributionListView.as_view(), name=MyAttributionListView.name),
    path('<int:year>/<str:global_id>/', AttributionListView.as_view(), name=AttributionListView.name),
]
