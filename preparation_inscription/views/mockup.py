
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
                                                'text': 'LECGE101R - Economie et gestion',
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
        return []


class ConsulterContenuGroupementViewMockup(ConsulterContenuGroupementView):
    name = 'consulter-contenu-groupement-mockup-resultat-apres-ajout-groupements'

    # TemplateView
    template_name = "mockup/blocks/mockup_consulter_contenu_groupement.html"
    htmx_template_name = "mockup/blocks/mockup_consulter_contenu_groupement.html"

    def get_content(self):
        return {
            'search_result': [
                {
                    "code": "LESPO1113",
                    "intitule": "Sociologie et anthropologie des mondes contemporains",
                    "volumes": 40,
                    "bloc": 1,
                    "quadrimestre": "Q1 ou Q2",
                    "credits": 5,
                    "session_derogation": "",
                    "obligatoire": "Oui"
                },
                {
                    "code": "LESPO1321",
                    "intitule": "Economic, Political and Social Ethics",
                    "volumes": 30,
                    "bloc": 3,
                    "quadrimestre": "Q2",
                    "credits": 3,
                    "session_derogation": "",
                    "obligatoire": "Oui"
                },
                {
                    "code": "CHOIX",
                    "intitule": "Cours au choix",
                    "volumes": "",
                    "bloc": "",
                    "quadrimestre": "",
                    "credits": "",
                    "session_derogation": "",
                    "obligatoire": "Oui"
                },
                {
                    "code": "LECGE101R",
                    "intitule": "Economie et gestion",
                    "volumes": "",
                    "bloc": "",
                    "quadrimestre": "",
                    "credits": "",
                    "session_derogation": "",
                    "obligatoire": "Oui",
                    "type_ajustement": TypeAjustement.AJOUT.name
                },

            ],
            'intitule_groupement': 'MAT1ECGE',
            'intitule_complet_groupement': 'Formation pluridisciplinaire en sciences humaines',
        }
