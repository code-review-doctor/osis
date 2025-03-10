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
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

from base.utils.htmx import HtmxMixin


RAFRAICHIR_GROUPEMENT_CONTENANT = 'rafraichir_groupement_contenant'


class ConsulterContenuGroupementView(HtmxMixin, PermissionRequiredMixin, TemplateView):
    name = 'consulter_contenu_groupement_view'

    # PermissionRequiredMixin
    permission_required = "preparation_inscription.view_preparation_inscription_cours"
    raise_exception = True

    # TemplateView
    template_name = "preparation_inscription/preparation_inscription.html"
    htmx_template_name = "preparation_inscription/consulter_contenu_groupement.html"

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            # TODO code_groupement_racine :: à implémenter quand la story "afficher contenu" est développée
            'code_groupement_racine': 'LECGE100T',
            RAFRAICHIR_GROUPEMENT_CONTENANT: self.request.GET.get(RAFRAICHIR_GROUPEMENT_CONTENANT),
            'search_result': self.get_content(),
            'intitule_groupement': self.get_intitule_groupement(),
            'intitule_programme': self.get_intitule_programme(),
        }

    def get_content(self):
        data = [
            {
                'code_ue': 'LESPO1113',
                'intitule': 'Sociologie et anthropologie des mondes contemporains',
                'volumes': '10',
                'bloc': '1',
                'quadri': 'Q1',
                'credits': '5/5',
                'session': 'Oui',
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
                'session': 'Oui',
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
                'session': 'Oui',
                'obligatoire': 'Oui',
                'commentaire_fr': '',
                'commentaire_en': '',
                'type_ajustement': TypeAjustement.MODIFICATION.name,
            },
            {
                'code_ue': 'LECGE1115',
                'intitule': 'Economie politique',
                'volumes': '30',
                'bloc': '1',
                'quadri': 'Q2',
                'credits': '3/3',
                'session': 'Oui',
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
                'session': 'Oui',
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
                'session': 'Oui',
                'obligatoire': 'Non',
                'commentaire_fr': '',
                'commentaire_en': '',
                'type_ajustement': TypeAjustement.AJOUT.name,
            },
        ]  # TODO :: message_bus.invoke(Command)
        return data

    def get_intitule_groupement(self):
        # TODO :: to implement
        return "Intitulé groupement"

    def get_intitule_programme(self):
        # TODO :: to implement
        return "Intitulé programme"


from base.models.utils.utils import ChoiceEnum


class TypeAjustement(ChoiceEnum):
    SUPPRESSION = _('Deletion')
    MODIFICATION = _('Modification')
    AJOUT = _('Addition')
