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
from typing import Optional

from django.urls import reverse
from django.utils.functional import cached_property
from django.views.generic import TemplateView
from rules.contrib.views import PermissionRequiredMixin

from ddd.logic.preparation_programme_annuel_etudiant.commands import GetFormationCommand
from education_group.templatetags.academic_year_display import display_as_academic_year
from infrastructure.messages_bus import message_bus_instance
from program_management.ddd.dtos import ProgrammeDeFormationDTO


class PreparationInscriptionMainView(PermissionRequiredMixin, TemplateView):
    name = 'preparation-inscription-main-view'

    # PermissionRequiredMixin
    permission_required = "preparation_inscription.view_preparation_inscription_cours"
    raise_exception = True

    # TemplateView
    template_name = "preparation_inscription/preparation_inscription.html"

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            'tree_view_url': self.get_tree_view_url(),
            'tree_panel_header': self.get_tree_panel_header(),
            'tree_panel_title': self.get_tree_panel_title(),
            'annee': self.kwargs['annee'],
            'code_programme': self.kwargs['code_programme']
        }

    def get_tree_view_url(self) -> str:
        return reverse('program-tree-view', kwargs={
            'annee': self.kwargs['annee'],
            'code_programme': self.kwargs['code_programme']
        })

    def get_tree_panel_header(self) -> str:
        return "{sigle}{version} (RE) - {annee}".format(
            sigle=self.formation.sigle,
            version=" [{}]".format(self.formation.version) if self.formation.version else '',
            annee=display_as_academic_year(self.formation.annee),
        )

    def get_tree_panel_title(self) -> str:
        return self.formation.intitule_formation

    @cached_property
    def formation(self) -> Optional['ProgrammeDeFormationDTO']:
        cmd = GetFormationCommand(
            annee=self.kwargs['annee'],
            code=self.kwargs['code_programme']
        )
        return message_bus_instance.invoke(cmd)
