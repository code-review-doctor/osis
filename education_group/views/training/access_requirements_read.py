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
from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse

from base.utils.cache import cache
from base.utils.cache_keys import get_tab_lang_keys
from education_group.views.serializers import access_requirements
from education_group.views.training.common_read import TrainingRead, Tab


class TrainingReadAccessRequirements(TrainingRead):
    template_name = "education_group_app/training/access_requirements_read.html"
    active_tab = Tab.ACCESS_REQUIREMENTS

    def get(self, request, *args, **kwargs):
        if not self.have_access_requirements_tab():
            return redirect(reverse('training_identification', kwargs=self.kwargs))
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        training = self.training
        context = {
            **super().get_context_data(**kwargs),
            "can_edit_information":
                self.request.user.has_perm("base.change_admissioncondition", self.get_permission_object()),
            "update_text_url": self.get_update_text_url(),
            "common_access_requirements": self.get_common_access_requirements(),
            "access_requirements": self.get_access_requirements()
        }

        if training.is_master_60_credits() or training.is_master_120_credits() or training.is_master_180_240_credits():
            current_language = cache.get(get_tab_lang_keys(self.request.user)) or settings.LANGUAGE_CODE_FR
            context.update({
                'language': {
                    'list': self.__get_language_list(),
                    'current_language': current_language,
                },
                "access_requirements_lines": self.get_access_requirements_lines(current_language),

                # TODO: Switch to DDD (Use in case of URL on admission_condition_table_row block)
                "education_group_year": self.education_group_version.offer,
                "root": self.education_group_version.offer
            })
        return context

    def __get_language_list(self):
        return [
            {'text': "fr-be", 'url':  reverse('tab_lang_edit', args=[self.node_identity.year,
                                                                     self.node_identity.code, 'fr-be'])},
            {'text': "en", 'url': reverse('tab_lang_edit', args=[self.node_identity.year,
                                                                 self.node_identity.code, 'en'])}
        ]

    def get_common_access_requirements(self):
        training = self.training
        return access_requirements.get_common_access_requirements(
            training.type.name,
            training.year
        )

    def get_access_requirements(self):
        training = self.training
        return access_requirements.get_access_requirements(
            training.acronym,
            training.year
        )

    def get_access_requirements_lines(self, language: str):
        training = self.training
        return access_requirements.get_access_requirements_lines(
            training.acronym,
            training.year,
            language
        )

    def get_update_text_url(self) -> str:
        return reverse(
            'education_group_year_access_requirements_update_text',
            kwargs={
                'year': self.node_identity.year,
                'code': self.node_identity.code
            }
        )
