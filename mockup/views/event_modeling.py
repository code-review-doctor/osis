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
from dal import autocomplete
from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

from base.forms.utils.choice_field import add_blank
from base.models.enums.active_status import ActiveStatusEnum
from base.utils.htmx import HtmxMixin
from education_group.forms.fields import MainEntitiesVersionChoiceField, UpperCaseCharField


class SearchForm(forms.Form):
    autocomplete = forms.ChoiceField(
        required=False,
        label=_('Label').capitalize(),
        widget=autocomplete.ListSelect2(
            url='venetmodeling-autocomplete',
            attrs={'data-html': True, 'data-placeholder': _('Name')},
        )
    )
    code_ue = UpperCaseCharField(max_length=15, label=_("code_ue").capitalize())
    intitule = forms.ChoiceField(
        initial=ActiveStatusEnum.ACTIVE.name,
        choices=add_blank(list(ActiveStatusEnum.choices())),
        label=_("intitule").capitalize(),
    )
    volumes = forms.IntegerField(
        label=_("volumes").capitalize(),
        required=False,
    )
    bloc = forms.BooleanField(label=_('bloc').capitalize())
    management_entity = MainEntitiesVersionChoiceField(
        queryset=None,
        label=_('management_entity').capitalize(),
        required=False
    )
    quadri = forms.DecimalField(
        max_digits=7,
        decimal_places=4,
        label=_('quadri').capitalize(),
        validators=[MinValueValidator(1), MaxValueValidator(9999)],
    )

    def __init__(self, *args, user: User, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)


class EventModelingView(HtmxMixin, LoginRequiredMixin, TemplateView):
    name = 'EventModelingView'
    # TemplateView
    template_name = "mockup/event_modeling.html"
    htmx_template_name = "mockup/blocks/tab_contenu.html"

    def get_context_data(self, **kwargs):
        context = {
            **super().get_context_data(**kwargs),
            'search_form': self.get_search_form(),
            'search_result': self.get_search_result(),
        }
        return context

    def get_search_form(self):
        return SearchForm(data=self.request.GET or None, user=self.request.user)

    def get_search_result(self):
        # TODO :: message_bus.invoke(Command)
        return data


from base.models.utils.utils import ChoiceEnum


class TypeAjustement(ChoiceEnum):
    SUPPRESSION = _('SUPPRESSION')
    MODIFICATION = _('MODIFICATION')
    AJOUT = _('AJOUT')

data = [
    {
        'code_ue': 'LESPO1113',
        'intitule': 'Sociologie et anthropologie des mondes contemporains',
        'volumes': '10',
        'bloc': '1',
        'quadri': 'Q1',
        'credits': '5/5',
        'session': '',
        'obligatoire': 'Oui',
        'commentaire_fr': """Lorem Ipsum est un générateur de faux textes aléatoires. Vous choisissez le nombre de paragraphes, de mots ou de listes. Vous obtenez alors un texte aléatoire que vous pourrez ensuite utiliser librement dans vos maquettes.
                    Le texte généré est du pseudo latin et peut donner l'impression d'être du vrai texte.
                    Faux-Texte est une réalisation du studio de création de sites internet indépendant Prélude Prod.
                    Si vous aimez la photographie d'art et l'esprit zen, jetez un œil sur le site de ce photographe à Palaiseau, en Essonne (France).
                """,
        'commentaire_en': '',
        'type_ajustement': TypeAjustement.SUPPRESSION.name,
    },
    {
        'code_ue': 'LESPO1321',
        'intitule': 'Economic, Political and Social Ethics',
        'volumes': '15+10',
        'bloc': '1',
        'quadri': 'Q1',
        'credits': '4/5',
        'session': '',
        'obligatoire': 'Oui',
        'commentaire_fr': '',
        'commentaire_en': '',
        'type_ajustement': TypeAjustement.SUPPRESSION.name,
    },
    {
        'code_ue': 'LESPO1114',
        'intitule': 'Political Science',
        'volumes': '30',
        'bloc': '2',
        'quadri': 'Q1',
        'credits': '5/5',
        'session': '',
        'obligatoire': 'Oui',
        'commentaire_fr': '',
        'commentaire_en': '',
        'type_ajustement': TypeAjustement.MODIFICATION.name,
    },
    {
        'code_ue': 'LECGE1115',
        'intitule': 'Economie politique',
        'volumes': '30',
        'bloc': '2',
        'quadri': 'Q2',
        'credits': '3/3',
        'session': '',
        'obligatoire': 'Oui',
        'commentaire_fr': '',
        'commentaire_en': '',
        'type_ajustement': None,
    },
    {
        'code_ue': 'LINGE1122',
        'intitule': 'Physique 1',
        'volumes': '30',
        'bloc': '1',
        'quadri': 'Q2',
        'credits': '3/3',
        'session': '',
        'obligatoire': 'Oui',
        'commentaire_fr': '',
        'commentaire_en': '',
        'type_ajustement': TypeAjustement.AJOUT.name,
    },
    {
        'code_ue': 'LINGE1125',
        'intitule': 'Séminaire de travail universitaire en gestion',
        'volumes': '25',
        'bloc': '1',
        'quadri': 'Q2',
        'credits': '5/5',
        'session': '',
        'obligatoire': 'Non',
        'commentaire_fr': '',
        'commentaire_en': '',
        'type_ajustement': TypeAjustement.AJOUT.name,
    },
]


from typing import List

from django.views.generic import TemplateView
from rules.contrib.views import LoginRequiredMixin


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
                'block': 'Bloc',
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
                                                'children': [],
                                                'block': 1,
                                            },
                                            {
                                                'id': '11112',
                                                'text': 'LESPO1321 - Economic, Political and Social Ethics',
                                                'obligatoire': True,
                                                'type_ajustement': TypeAjustement.SUPPRESSION.name,
                                                'children': [],
                                                'block': 1,
                                            },
                                            {
                                                'id': '11113',
                                                'text': 'LESPO1114 - Political Science',
                                                'obligatoire': True,
                                                'type_ajustement': TypeAjustement.MODIFICATION.name,
                                                'children': [],
                                                'block': 1,
                                            },
                                            {
                                                'id': '11115',
                                                'text': 'LECGE1115 - Economie politique',
                                                'obligatoire': True,
                                                'type_ajustement': None,
                                                'children': [],
                                                'block': 2,
                                            },
                                            {
                                                'id': '11114',
                                                'text': 'LINGE1122 - Physique 1',
                                                'obligatoire': True,
                                                'type_ajustement': TypeAjustement.AJOUT.name,
                                                'children': [],
                                                'block': 1,
                                            },
                                            {
                                                'id': '11116',
                                                'text': 'LINGE1125 - Séminaire de travail universitaire en gestion',
                                                'obligatoire': False,
                                                'type_ajustement': TypeAjustement.AJOUT.name,
                                                'children': [],
                                                'block': 1,
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
