##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)
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
from education_group.views.training.common_read import TrainingRead, Tab
from program_management.ddd.service import tree_service


class TrainingReadUtilization(TrainingRead):
    template_name = "education_group_app/training/utilization_read.html"
    active_tab = Tab.UTILIZATION

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        node = self.get_object()
        tree_versions = tree_service.search_tree_versions_using_node(node)

        context['utilization_rows'] = []
        for tree_version in tree_versions:
            context['utilization_rows'] += [
                {'link': link, 'tree_versions': [tree_version]}
                for link in tree_version.get_tree().get_links_using_node(node)
            ]
        context['utilization_rows'] = sorted(context['utilization_rows'], key=lambda row: row['link'].parent.code)
        print(context['utilization_rows'])
        return context
