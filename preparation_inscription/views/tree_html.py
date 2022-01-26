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

from django.views.generic import TemplateView
from rules.contrib.views import LoginRequiredMixin

from preparation_inscription.views.consulter_contenu_groupement import TypeAjustement


class TreeHTMLView(LoginRequiredMixin, TemplateView):
    name = 'tree-view'

    # TemplateView
    template_name = "mockup/blocks/tree_recursif.html"

    def get_context_data(self, **kwargs):
        if self.request.GET.get('id') != "#":
            tree = self.get_node_of_tree(self.request.GET['id'])
        else:
            tree = self.get_tree()

        return {
            **super().get_context_data(**kwargs),
            'tree': tree
        }

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

    def get_node_of_tree(self, node_id: str) -> List:
        return [
            # {
            #     'id': 'node_3',
            #     'text': 'Node 3',
            #     'children': [
            #         {
            #             'id': 'node_31',
            #             'text': 'Node 31',
            #             'children': []
            #         },
            #     ]
            # }
        ]
