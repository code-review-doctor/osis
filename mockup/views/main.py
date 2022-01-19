from typing import List

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class DetailView(LoginRequiredMixin, TemplateView):
    name = 'detail-view'

    # TemplateView
    template_name = "mockup/detail.html"

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            'element': self.get_element(),
        }

    def get_element(self):
        return {
            'champs1': '1',
            'champs2': '2',
            'champs3': '3',
            'champs4': '4',
            'champs5': '5',
            'champs6': '6',
        }


class TreeHTMLView(LoginRequiredMixin, TemplateView):
    name = 'tree-view'

    # TemplateView
    template_name = "mockup/tree.html"

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            'tree': self.get_tree()
        }

    def get_tree(self) -> List:
        return [
            {
                'id': 'node_1',
                'text': 'Node 1',
                'children': [
                    {
                        'id': 'node_11',
                        'text': 'Node 11',
                        'children': []
                    },
                    {
                        'id': 'node_12',
                        'text': 'Node 12',
                        'children': []
                    },
                ]
            },
            {
                'id': 'node_2',
                'text': 'Node 2',
                'children': []
            },
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
            },
        ]
