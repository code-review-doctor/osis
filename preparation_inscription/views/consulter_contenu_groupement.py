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
from decimal import Decimal
from typing import List, Dict, Union

from django.contrib.auth.mixins import LoginRequiredMixin
from django.template.defaultfilters import yesno
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

from base.utils.htmx import HtmxMixin
from ddd.logic.preparation_programme_annuel_etudiant.commands import GetContenuGroupementCommand
from ddd.logic.preparation_programme_annuel_etudiant.dtos import ContenuGroupementDTO
from infrastructure.messages_bus import message_bus_instance
from preparation_inscription.utils.chiffres_significatifs_de_decimal import get_chiffres_significatifs
from base.models.utils.utils import ChoiceEnum


class TypeAjustement(ChoiceEnum):
    SUPPRESSION = _('SUPPRESSION')
    MODIFICATION = _('MODIFICATION')
    AJOUT = _('AJOUT')


CODE = 'code'
INTITULE = 'intitule'
VOLUMES = 'volumes'
BLOC = 'bloc'
QUADRI = 'quadri'
CREDITS = 'credits'
SESSION = 'session'
OBLIGATOIRE = 'obligatoire'

RAFRAICHIR_GROUPEMENT_CONTENANT = 'rafraichir_groupement_contenant'


class ConsulterContenuGroupementView(HtmxMixin, LoginRequiredMixin, TemplateView):
    name = 'consulter_contenu_groupement_view'
    # TemplateView
    template_name = "preparation_inscription/preparation_inscription.html"
    htmx_template_name = "preparation_inscription/consulter_contenu_groupement.html"

    def get_context_data(self, **kwargs):
        context = {
            **super().get_context_data(**kwargs),
            # TODO code_groupement_racine :: à implémenter quand la story "afficher contenu" est développée
            'code_programme': self.kwargs['code_programme'],
            'code_groupement': self.kwargs['code_groupement'],
            RAFRAICHIR_GROUPEMENT_CONTENANT: self.request.GET.get(RAFRAICHIR_GROUPEMENT_CONTENANT),
            'intitule_programme': self.get_intitule_programme(),
        }

        context.update(self.get_content())
        return context

    def get_content(self):
        cmd = GetContenuGroupementCommand(
            code_formation=self.kwargs['code_programme'],
            annee=self.kwargs['annee'],
            code=self.kwargs.get('code_groupement', self.kwargs['code_programme']),
        )

        contenu_groupement_DTO = message_bus_instance.invoke(cmd)  # return ContenuGroupementDTO

        return {
            'search_result': self._build_donnees_contenus(contenu_groupement_DTO.contenu),
            'intitule_groupement':
                contenu_groupement_DTO.groupement_contenant.intitule if contenu_groupement_DTO else '',
            'intitule_complet_groupement':
                contenu_groupement_DTO.groupement_contenant.intitule_complet if contenu_groupement_DTO else '',
        }

    def _build_donnees_des_unites_enseignement_contenues(
            self, unites_enseignement_contenues: List['UniteEnseignementDTO']
    ) -> List[Dict]:
        donnees = []
        for ue_contenue in unites_enseignement_contenues:
            donnees.append(
                {
                    CODE: ue_contenue.code,
                    INTITULE: ue_contenue.intitule_complet,
                    VOLUMES: '{}{}{}'.format(
                        get_chiffres_significatifs(ue_contenue.volume_annuel_pm),
                        '+' if ue_contenue.volume_annuel_pm and ue_contenue.volume_annuel_pp else '',
                        get_chiffres_significatifs(ue_contenue.volume_annuel_pp)
                    ),
                    BLOC: ue_contenue.bloc,
                    QUADRI: ue_contenue.quadrimestre_texte,
                    CREDITS: _get_credits(ue_contenue.credits_relatifs, ue_contenue.credits_absolus),
                    SESSION: ue_contenue.session_derogation,
                    OBLIGATOIRE: yesno(ue_contenue.obligatoire),
                }
            )
        return donnees

    def _build_donnees_contenus(
            self,
            elements_contenus: List[Union['UniteEnseignementDTO', 'ContenuGroupementDTO']]
    ) -> List[Dict]:
        donnees = []
        for element_contenu in elements_contenus:
            if isinstance(element_contenu, ContenuGroupementDTO):
                donnees.append(_build_donnees_groupement(element_contenu))
            else:
                donnees.append(_build_donnees_ue(element_contenu))
        return donnees

    def get_intitule_programme(self):
        # TODO :: to implement
        return "Intitulé programme"


def _get_credits(credits_relatifs: int, credits_absolus: Decimal) -> str:
    if credits_relatifs:
        if credits_relatifs != credits_absolus:
            return "{}({})".format(credits_relatifs, get_chiffres_significatifs(credits_absolus))
        return "{}".format(credits_relatifs)
    return get_chiffres_significatifs(credits_absolus)


def _build_donnees_ue(ue_contenue: 'UniteEnseignementDTO') -> Dict:
    return {
        CODE: ue_contenue.code,
        INTITULE: ue_contenue.intitule_complet,
        VOLUMES: '{}{}{}'.format(
            ue_contenue.volume_annuel_pm,
            '+' if ue_contenue.volume_annuel_pm and ue_contenue.volume_annuel_pp else '',
            ue_contenue.volume_annuel_pp
        ),
        BLOC: ue_contenue.bloc,
        QUADRI: ue_contenue.quadrimestre_texte,
        CREDITS: _get_credits(ue_contenue.credits_relatifs, ue_contenue.credits_absolus),
        SESSION: ue_contenue.session_derogation,
        OBLIGATOIRE: yesno(ue_contenue.obligatoire),
    }


def _build_donnees_groupement(groupement_contenu: 'ContenuGroupementDTO') -> Dict:
    return {
        CODE: groupement_contenu.groupement_contenant.intitule,
        INTITULE: groupement_contenu.groupement_contenant.intitule_complet,
        OBLIGATOIRE: yesno(groupement_contenu.groupement_contenant.obligatoire),
    }
