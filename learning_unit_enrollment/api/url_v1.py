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
from django.conf.urls import url
from django.urls import path

from learning_unit_enrollment.api.views.enrollment import LearningUnitEnrollmentsListView, \
    MyLearningUnitEnrollmentsListView

app_name = "learning_unit_enrollment"
urlpatterns = [
    path('enrollments/<str:acronym>/<int:year>/', LearningUnitEnrollmentsListView.as_view(),
         name=LearningUnitEnrollmentsListView.name),
    url(r'^my_enrollments/(?P<program_code>[0-9A-Za-z_/ ]+)/(?P<year>[0-9]{4})/$',
        MyLearningUnitEnrollmentsListView.as_view(),
        name=MyLearningUnitEnrollmentsListView.name)
]
