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
from django.urls import path, include

from preparation_inscription.views.ajouter_unites_enseignement import AjouterUnitesEnseignementView
from preparation_inscription.views.consulter_contenu_groupement import ConsulterContenuGroupementView
from preparation_inscription.views.detail import PreparationInscriptionMainView
from preparation_inscription.views.formulaire_inscription_cours import FormulaireInscriptionCoursView
from preparation_inscription.views.liste_unites_enseignement import ListeUnitesEnseignementView
from preparation_inscription.views.modification_contenu_groupement import ModifierProprietesContenuView
from preparation_inscription.views.program_tree import ProgramTreeHTMLView
from preparation_inscription.views.supprimer_unites_enseignement import SupprimerUnitesEnseignementView

urlpatterns = [

    path('<int:annee>/<str:code_programme>/', include([
        path('', PreparationInscriptionMainView.as_view(), name=PreparationInscriptionMainView.name),
        path('detail', ConsulterContenuGroupementView.as_view(), name=ConsulterContenuGroupementView.name),
        path('<str:code_groupement>/detail', ConsulterContenuGroupementView.as_view(),
             name=ConsulterContenuGroupementView.name),
        path('delete', SupprimerUnitesEnseignementView.as_view(), name=SupprimerUnitesEnseignementView.name),
        path(
            'add/<str:code_groupement>',
            AjouterUnitesEnseignementView.as_view(),
            name=AjouterUnitesEnseignementView.name
        ),
        path('update', ModifierProprietesContenuView.as_view(), name=ModifierProprietesContenuView.name),
        path('tree/', ProgramTreeHTMLView.as_view(), name=ProgramTreeHTMLView.name),
        path(
            'formulaire_inscription/',
            FormulaireInscriptionCoursView.as_view(),
            name=FormulaireInscriptionCoursView.name
        ),
        path('liste_unites_enseignement/', ListeUnitesEnseignementView.as_view(), name=ListeUnitesEnseignementView.name)
    ])),
]
