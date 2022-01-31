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

from django.views.generic import TemplateView
from rules.contrib.views import LoginRequiredMixin

from ddd.logic.preparation_programme_annuel_etudiant.commands import GetProgrammeInscriptionCoursCommand
from ddd.logic.preparation_programme_annuel_etudiant.dtos import ProgrammeInscriptionCoursDTO
from infrastructure.messages_bus import message_bus_instance


class ProgramTreeHTMLView(LoginRequiredMixin, TemplateView):
    name = 'program-tree-view'

    # TemplateView
    template_name = "preparation_inscription/blocks/tree_recursif.html"

    def get_context_data(self, **kwargs):
        id = self.request.GET.get('id')
        if id and id != "#":
            tree = self.get_node_of_tree(self.request.GET['id'])
        else:
            tree = self.get_tree()

        return {
            **super().get_context_data(**kwargs),
            'tree': tree
        }

    def get_tree(self) -> 'ProgrammeInscriptionCoursDTO':
        cmd = GetProgrammeInscriptionCoursCommand(
            annee=self.kwargs['annee'],
            code_programme=self.kwargs['code_programme'],
        )
        tree_dto = message_bus_instance.invoke(cmd)
        return tree_dto

    def get_node_of_tree(self, node_id: str) -> 'ProgrammeInscriptionCoursDTO':
        return self.get_tree()  # TODO :: à implémenter - charger uniquement le node modifié (et pas tout l'arbre)
