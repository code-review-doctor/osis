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


class ProgramTreeHTMLView(LoginRequiredMixin, TemplateView):
    name = 'program-tree-view'

    # TemplateView
    template_name = "preparation_inscription/program_tree.html"

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
        return [{
            'id': 'root_node',
            'text': 'ECGE1BA',
            'block': 'Bloc',
            'children': [
                {
                    'id': 'node_1',
                    'text': 'Node 1',
                    'block': '',
                    'children': [
                        {
                            'id': 'node_11',
                            'text': 'Node 11',
                            'block': '2',
                            'children': []
                        },
                        {
                            'id': 'node_12',
                            'text': 'Node 12',
                            'block': '3',
                            'children': []
                        },
                    ]
                },
                {
                    'id': 'node_2',
                    'text': 'Node 2',
                    'block': '',
                    'children': []
                },
                {
                    'id': 'node_3',
                    'text': 'Node 3',
                    'block': '',
                    'children': [
                        {
                            'id': 'node_31',
                            'text': 'Node 31',
                            'block': '2',
                            'children': []
                        },
                    ]
                },
            ]
        }]

    def get_node_of_tree(self, node_id: str) -> List:
        return [
            {
                'id': 'node_3',
                'text': 'Node 3',
                'children': [
                    {
                        'id': 'node_31',
                        'text': 'Node 31',
                        'children': []
                    },
                ]
            }
        ]
