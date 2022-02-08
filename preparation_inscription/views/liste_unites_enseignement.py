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

from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.functional import cached_property
from django.views.generic import TemplateView

from base.utils.htmx import HtmxMixin
from ddd.logic.preparation_programme_annuel_etudiant.commands import GetUnitesEnseignementContenuesCommand
from infrastructure.messages_bus import message_bus_instance


class ListeUnitesEnseignementView(HtmxMixin, LoginRequiredMixin, TemplateView):
    name = 'liste_unites_enseignement_view'
    # TemplateView
    template_name = "preparation_inscription/liste_unites_enseignement.html"
    htmx_template_name = "preparation_inscription/liste_unites_enseignement.html"

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            # TODO code_groupement_racine :: à implémenter quand la story "afficher contenu" est développée
            'search_result': self.get_content(),
        }

    def get_content(self) -> List['UniteEnseignementDTO']:
        cmd = GetUnitesEnseignementContenuesCommand(code=self.code_programme, annee=self.annee)
        return message_bus_instance.invoke(cmd)

    @cached_property
    def code_programme(self) -> str:
        return self.kwargs['code_programme']

    @cached_property
    def annee(self) -> str:
        return self.kwargs['annee']
