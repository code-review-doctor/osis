
from typing import List

from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView
from rules.contrib.views import LoginRequiredMixin

from base.models.utils.utils import ChoiceEnum
from preparation_inscription.views.consulter_contenu_groupement import ConsulterContenuGroupementView


class TypeAjustement(ChoiceEnum):
    SUPPRESSION = _('SUPPRESSION')
    MODIFICATION = _('MODIFICATION')
    AJOUT = _('AJOUT')


class TreeHTMLView(LoginRequiredMixin, TemplateView):
    name = 'tree-view-mockup-resultat-apres-ajout-groupements'

    # TemplateView
    template_name = "mockup/blocks/mockup_tree_apres_ajout_groupements.html"

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
                                                'type_ajustement': None,
                                                'children': []
                                            },
                                            {
                                                'id': '11112',
                                                'text': 'LESPO1321 - Economic, Political and Social Ethics',
                                                'obligatoire': True,
                                                'type_ajustement': None,
                                                'children': []
                                            },
                                            {
                                                'id': '11113',
                                                'text': 'Cours au choix',
                                                'obligatoire': True,
                                                'type_ajustement': None,
                                                'children': []
                                            },
                                            {
                                                'id': '11115',
                                                'text': 'Economie et gestion',
                                                'obligatoire': True,
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


class ConsulterContenuGroupementViewMockup(ConsulterContenuGroupementView):
    name = 'consulter-contenu-groupement-mockup-resultat-apres-ajout-groupements'

    # TemplateView
    template_name = "mockup/blocks/mockup_consulter_contenu_groupement.html"

    def get_content(self):
        return []
