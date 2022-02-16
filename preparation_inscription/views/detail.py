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

from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.functional import cached_property
from django.views.generic import TemplateView
from rules.contrib.views import PermissionRequiredMixin

from ddd.logic.preparation_programme_annuel_etudiant.commands import GetFormationCommand
from education_group.models.group_year import GroupYear
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
    def group_year(self) -> 'GroupYear':
        return get_object_or_404(GroupYear, academic_year__year=self.annee, partial_acronym=self.code_programme)

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            'tree_view_url': self.get_tree_view_url(),
            'tree_panel_header': self.get_tree_panel_header(),
            'tree_panel_title': self.get_tree_panel_title(),
            'annee': self.annee,
            'code_programme': self.code_programme,
            'code_groupement':  self.code_groupement,
            'group_year': self.group_year
        }

    def get_tree_view_url(self) -> str:
        return reverse('program-tree-view', kwargs={
            'annee': self.annee,
            'code_programme': self.code_programme,
        })

    def get_tree_panel_header(self) -> str:
        header = self.formation.sigle
        if self.formation.version and self.formation.transition_name:
            header += "[{} - {}]".format(self.formation.version, self.formation.transition_name)
        elif self.formation.version:
            header += "[{}]".format(self.formation.version)
        elif self.formation.transition_name:
            header += "[{}]".format(self.formation.transition_name)
        header += ' (RE) - {annee}'.format(annee=display_as_academic_year(self.formation.annee))
        return header

    def get_tree_panel_title(self) -> str:
        return self.formation.intitule_formation

    @cached_property
    def formation(self) -> Optional['ProgrammeDeFormationDTO']:
        cmd = GetFormationCommand(
            annee=self.annee,
            code=self.code_programme
        )
        formation = message_bus_instance.invoke(cmd)
        if not formation:
            raise Http404
        return formation
