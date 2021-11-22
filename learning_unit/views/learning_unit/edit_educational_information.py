##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2021 Université catholique de Louvain (http://www.uclouvain.be)
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

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Prefetch
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView

from base.business.learning_unit import CMS_LABEL_PEDAGOGY_FR_ONLY
from base.forms.learning_unit_pedagogy import LearningUnitPedagogyEditForm
from base.models.learning_unit_year import LearningUnitYear
from base.models.person import get_user_interface_language, Person
from base.views.common import display_success_messages
from base.views.learning_units.common import get_text_label_translated, get_common_context_learning_unit_year
from base.views.learning_units.pedagogy.update import build_success_message
from cms.models.text_label import TextLabel
from osis_role.contrib.views import PermissionRequiredMixin
from reference.models.language import find_language_in_settings


class EditEducationalInformation(LoginRequiredMixin, PermissionRequiredMixin, FormView):
    permission_required = 'base.can_edit_learningunit_pedagogy'
    raise_exception = True
    template_name = "learning_unit/educational_information_edit.html"
    form_class = LearningUnitPedagogyEditForm
    http_method_names = ['get', 'post']

    @cached_property
    def learning_unit_year(self) -> LearningUnitYear:
        return get_object_or_404(
            LearningUnitYear.objects.all().select_related('learning_container_year', 'academic_year'),
            pk=self.kwargs['learning_unit_year_id']
        )

    def get_permission_object(self) -> LearningUnitYear:
        return self.learning_unit_year

    @cached_property
    def person(self) -> Person:
        return get_object_or_404(Person, user=self.request.user)

    @cached_property
    def user_language(self) -> str:
        return get_user_interface_language(self.request.user)

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            **get_common_context_learning_unit_year(self.person, self.kwargs['learning_unit_year_id']),
            'text_label_translated': get_text_label_translated(self.text_label, self.user_language),
            'language_translated': find_language_in_settings(self.language),
            'cms_label_pedagogy_fr_only': CMS_LABEL_PEDAGOGY_FR_ONLY,
            'label_name': self.label_name
        }

    @property
    def language(self) -> str:
        return self.request.GET.get('language')

    @property
    def label_name(self) -> str:
        return self.request.GET.get('label')

    @cached_property
    def text_label(self) -> TextLabel:
        return TextLabel.objects.prefetch_related(
            Prefetch('translatedtextlabel_set', to_attr="translated_text_labels")
        ).get(label=self.label_name)

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs.update({
            'learning_unit_year': self.learning_unit_year,
            'language': self.language,
            'text_label': self.text_label
        })
        return form_kwargs

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        if self.request.GET:
            form = form_class(**self.get_form_kwargs())
            form.load_initial()
        else:
            form = form_class(data=self.request.POST or None)
        return form

    def form_valid(self, form):
        form.save()
        last_academic_year_reported = form.luys[-1] if len(form.luys) >= 2 else None
        msg = build_success_message(last_academic_year_reported, form.luys[0])
        display_success_messages(self.request, msg)
        return HttpResponse()


class EditEducationalInformationForceMajeure(EditEducationalInformation):
    permission_required = 'base.can_edit_learningunit_pedagogy_force_majeur'

    def form_valid(self, form):
        form.save(postpone=False)
        display_success_messages(self.request, _("The learning unit has been updated (without report)."))
        return HttpResponse()
