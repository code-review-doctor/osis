##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2022 Université catholique de Louvain (http://www.uclouvain.be)
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

from reference.api.views.academic_calendar import AcademicCalendarList
from reference.api.views.academic_year import AcademicYears
from reference.api.views.city import CityList
from reference.api.views.country import CountryList, CountryDetail
from reference.api.views.high_school import HighSchoolList, HighSchoolDetail
from reference.api.views.language import LanguageList
from reference.api.views.study_domain import StudyDomainList

app_name = "reference"
urlpatterns = [
    url(r'^cities/$', CityList.as_view(), name=CityList.name),
    url(r'^countries/$', CountryList.as_view(), name=CountryList.name),
    url(r'^countries/(?P<uuid>[0-9a-f-]+)$', CountryDetail.as_view(), name=CountryDetail.name),
    url(r'^high_schools/$', HighSchoolList.as_view(), name=HighSchoolList.name),
    url(r'^high_schools/(?P<uuid>[0-9a-f-]+)$', HighSchoolDetail.as_view(), name=HighSchoolDetail.name),
    url(r'^study-domains$', StudyDomainList.as_view(), name=StudyDomainList.name),
    url(r'^languages$', LanguageList.as_view(), name=LanguageList.name),
    url(r'^academic_years$', AcademicYears.as_view(), name=AcademicYears.name),
    url(r'^academic_calendars/$', AcademicCalendarList.as_view(), name=AcademicCalendarList.name),

]
