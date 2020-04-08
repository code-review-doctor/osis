##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from osis_role.contrib.views import PermissionRequiredMixin

from base.business.education_groups import delete
from base.models.education_group import EducationGroup
from base.views import common
from base.views.mixins import DeleteViewWithDependencies


class DeleteGroupEducationView(PermissionRequiredMixin, DeleteViewWithDependencies):
    # DeleteView
    model = EducationGroup
    success_url = reverse_lazy('education_groups')
    pk_url_kwarg = "education_group_year_id"
    template_name = "education_group/delete.html"
    context_object_name = "education_group"
    permission_required = 'base.delete_all_educationgroup'

    # DeleteViewWithDependencies
    success_message = _("The education group has been deleted.")
    protected_template = "education_group/protect_delete.html"

    # FlagMixin
    flag = 'education_group_delete'
    education_group_years = []

    def get_protected_messages(self):
        """This function will return all protected message ordered by year"""
        self.education_group_years = delete.get_education_group_years_to_delete(self.get_object())
        protected_messages = []
        for education_group_year in self.education_group_years:
            protected_message = delete.get_protected_messages_by_education_group_year(education_group_year)
            if protected_message:
                protected_messages.append({
                    'education_group_year': education_group_year,
                    'messages': protected_message
                })
        return protected_messages

    def delete(self, request, *args, **kwargs):
        for education_group_year in delete.get_education_group_years_to_delete(self.get_object()):
            delete.start(education_group_year)
        common.display_success_messages(request, self.success_message)
        return JsonResponse({'success': True, 'success_url': self.success_url})
