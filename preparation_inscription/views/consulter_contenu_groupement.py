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
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

from base.models.utils.utils import ChoiceEnum
from base.utils.htmx import HtmxMixin
from ddd.logic.preparation_programme_annuel_etudiant.commands import GetContenuGroupementCommand
from ddd.logic.preparation_programme_annuel_etudiant.dtos import GroupementContenantDTO
from infrastructure.messages_bus import message_bus_instance


class TypeAjustement(ChoiceEnum):
    SUPPRESSION = _('SUPPRESSION')
    MODIFICATION = _('MODIFICATION')
    AJOUT = _('AJOUT')


RAFRAICHIR_GROUPEMENT_CONTENANT = 'rafraichir_groupement_contenant'


class ConsulterContenuGroupementView(HtmxMixin, PermissionRequiredMixin, LoginRequiredMixin, TemplateView):

    # PermissionRequiredMixin
    permission_required = "preparation_inscription.view_preparation_inscription_cours"
    raise_exception = True

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

        contenu_groupement_DTO = message_bus_instance.invoke(cmd)  # type: GroupementContenantDTO
        return {
            'search_result': contenu_groupement_DTO.elements_contenus,
            'intitule_groupement':
                contenu_groupement_DTO.intitule if contenu_groupement_DTO else '',
            'intitule_complet_groupement':
                contenu_groupement_DTO.intitule_complet if contenu_groupement_DTO else '',
        }

    def get_intitule_programme(self):
        # TODO :: to implement
        return "Intitulé programme"
