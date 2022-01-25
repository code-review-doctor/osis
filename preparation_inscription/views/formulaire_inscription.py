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
from typing import List

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import TemplateView

from base.utils.htmx import HtmxMixin
from preparation_inscription.views.consulter_contenu_groupement import TypeAjustement


class FormulaireInscriptionView(HtmxMixin, LoginRequiredMixin, TemplateView):
    name = 'pae_formulaire_inscription_view'
    # TemplateView
    template_name = "preparation_inscription/tabs.html"
    htmx_template_name = "preparation_inscription/blocks/tab_formulaire_inscription.html"

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            'tree': self.get_tree()
        }

    def post(self, request, *args, **kwargs):
        return redirect("pae_formulaire_inscription_view")

    def get_tree(self) -> List:
        return [
            {
                'id': 'node_1',
                'text': 'Bachelier en sciences économiques et de gestion',
                'obligatoire': True,
                'children': [
                    {
                        'id': 'node_11',
                        'text': 'Contenu:',
                        'obligatoire': True,
                        'children': [
                            {
                                'id': 'node_111',
                                'text': 'Programme de base',
                                'obligatoire': True,
                                'children': [
                                    {
                                        'id': 'node_1111',
                                        'text': 'Formation pluridisciplinaire en sciences humaines',
                                        'obligatoire': True,
                                        'children': [
                                            {
                                                'id': '11111',
                                                'text': 'LESPO1113 - Sociologie et anthropologie des mondes contemporains',
                                                'obligatoire': True,
                                                'type_ajustement': TypeAjustement.SUPPRESSION.name,
                                                'children': []
                                            },
                                            {
                                                'id': '11112',
                                                'text': 'LESPO1321 - Economic, Political and Social Ethics',
                                                'obligatoire': True,
                                                'type_ajustement': TypeAjustement.SUPPRESSION.name,
                                                'children': []
                                            },
                                            {
                                                'id': '11113',
                                                'text': 'LESPO1114 - Political Science',
                                                'obligatoire': True,
                                                'type_ajustement': TypeAjustement.MODIFICATION.name,
                                                'children': []
                                            },
                                            {
                                                'id': '11115',
                                                'text': 'LECGE1115 - Economie politique',
                                                'obligatoire': True,
                                                'type_ajustement': None,
                                                'children': []
                                            },
                                            {
                                                'id': '11114',
                                                'text': 'LINGE1122 - Physique 1',
                                                'obligatoire': True,
                                                'type_ajustement': TypeAjustement.AJOUT.name,
                                                'children': []
                                            },
                                            {
                                                'id': '11116',
                                                'text': 'LINGE1125 - Séminaire de travail universitaire en gestion',
                                                'obligatoire': False,
                                                'type_ajustement': TypeAjustement.AJOUT.name,
                                                'children': []
                                            },
                                        ]
                                    },
                                ]
                            },
                        ]
                    },
                ]
            },
        ]