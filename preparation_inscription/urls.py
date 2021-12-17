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
from django.urls import include, path

from preparation_inscription.views.ajouter_ue import RechercherUeView, ajouterUeView
from preparation_inscription.views.formulaire_par_defaut import FormulaireParDefaultView

urlpatterns = [
    path('<int:year>/<acronym:acronym>/', include([
        path('default_enrollment_form/', FormulaireParDefaultView.as_view(), name='default_enrollment_form'),
    ])),
    path('<int:year>/<acronym:acronym>/<str:version_name>/', include([
        path('default_enrollment_form/', FormulaireParDefaultView.as_view(), name='default_enrollment_form'),
        path(
            '<str:transition_name>/default_enrollment_form/',
            FormulaireParDefaultView.as_view(),
            name='default_enrollment_form'
        ),
    ])),
    path('search_ue/', RechercherUeView.as_view(), name='search_ue_to_program'),
    path('add_ue/<int:year>/', ajouterUeView, name='add_ue_to_program'),
]
