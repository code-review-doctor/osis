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

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.forms import Form
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView, FormView

from base.models.utils.utils import ChoiceEnum
from base.utils.htmx import HtmxMixin
from base.views.mixins import AjaxTemplateMixin
from ddd.logic.preparation_programme_annuel_etudiant.commands import GetContenuGroupementCommand, \
    AnnulerAjustementDAjoutCommand
from ddd.logic.preparation_programme_annuel_etudiant.dtos import GroupementContenantDTO
from education_group.models.group_year import GroupYear
from infrastructure.messages_bus import message_bus_instance
from preparation_inscription.perms import AJOUTER_UNITE_ENSEIGNEMENT_PERMISSION
from preparation_inscription.views.consulter_contenu_groupement import ConsulterContenuGroupementView

RAFRAICHIR_GROUPEMENT_CONTENANT = 'rafraichir_groupement_contenant'


class AnnulerAjustementCommonView(HtmxMixin, PermissionRequiredMixin, LoginRequiredMixin, TemplateView, FormView):

    # PermissionRequiredMixin
    permission_required = "preparation_inscription.can_annuler_action_sur_unite_enseignement_du_programme"

    raise_exception = True

    # TemplateView
    template_name = "preparation_inscription/preparation_inscription.html"
    htmx_template_name = "preparation_inscription/consulter_contenu_groupement.html"
    form_class = Form

    @cached_property
    def annee(self) -> int:
        return self.kwargs['annee']

    @cached_property
    def code_programme(self) -> str:
        return self.kwargs['code_programme']

    @cached_property
    def code_groupement(self) -> str:
        return self.kwargs.get('code_groupement', self.kwargs['code_programme'])

    @cached_property
    def code_ue(self) -> str:
        return self.kwargs['code_ue']

    @cached_property
    def group_year(self) -> 'GroupYear':
        return get_object_or_404(GroupYear, academic_year__year=self.annee, partial_acronym=self.code_programme)

    def get_success_url(self):
        return reverse(ConsulterContenuGroupementView.name, kwargs={
            'code_programme': self.code_programme,
            'code_groupement': self.code_groupement,
            'annee': self.annee
        })


def get_content_fake():
    return [
        {
            'code': 'LESPO1113',
            'intitule': 'Sociologie...',
            'volumes': '10',
            'bloc': '1',
            'quadri': 'Q1',
            'credits': '5/5',
            'session': 'Oui',
            'obligatoire': '',
            'commentaire_fr': '',
            'commentaire_en': '',
        },
        {
            'code_ue': 'LESPO1321',
            'intitule': 'Economic...',
            'volumes': '15+10',
            'bloc': '1',
            'quadri': 'Q1',
            'credits': '4/5',
            'session': 'Oui',
            'obligatoire': '',
            'commentaire_fr': '',
            'commentaire_en': '',
            'modifie': True,
        },
        {
            'code_ue': 'LESPO1114',
            'intitule': 'Political...',
            'volumes': '30',
            'bloc': '2',
            'quadri': 'Q1',
            'credits': '5/5',
            'session': 'Oui',
            'obligatoire': '',
            'commentaire_fr': '',
            'commentaire_en': '',
            'ajoute': True,
        },
        {
            'code_ue': 'LINGE1122',
            'intitule': 'Physique...',
            'volumes': '30',
            'bloc': '1',
            'quadri': 'Q2',
            'credits': '3/3',
            'session': 'Oui',
            'obligatoire': '',
            'commentaire_fr': '',
            'commentaire_en': '',
        },
        {
            'code_ue': 'LINGE1125',
            'intitule': 'Séminaire...',
            'volumes': '25',
            'bloc': '1',
            'quadri': 'Q2',
            'credits': '5/5',
            'session': 'Oui',
            'obligatoire': '',
            'commentaire_fr': '',
            'commentaire_en': '',
        },
    ]
