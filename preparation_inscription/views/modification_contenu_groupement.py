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
from gettext import ngettext
from typing import List

from django import forms
from django.contrib import messages
from django.forms import formset_factory
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.functional import cached_property
from django.views.generic import FormView
from django.utils.translation import gettext_lazy as _

from base.ddd.utils.business_validator import MultipleBusinessExceptions
from base.utils.htmx import HtmxMixin
from ddd.logic.preparation_programme_annuel_etudiant.commands import GetContenuGroupementCommand, \
    ModifierUEDuGroupementCommand, ModifierUniteEnseignementCommand
from ddd.logic.preparation_programme_annuel_etudiant.dtos import GroupementContenantDTO
from education_group.models.group_year import GroupYear
from infrastructure.messages_bus import message_bus_instance
from osis_role.contrib.views import PermissionRequiredMixin
from preparation_inscription.views.consulter_contenu_groupement import RAFRAICHIR_GROUPEMENT_CONTENANT


class ModifierProprietesContenuForm(forms.Form):
    code = forms.CharField(widget=forms.HiddenInput)
    bloc = forms.CharField(required=False)


class ModifierProprietesContenuView(PermissionRequiredMixin, HtmxMixin, FormView):
    name = 'modifier_proprietes_contenu_view'

    # PermissionRequiredMixin
    permission_required = 'preparation_programme.can_modifier_contenu_groupement'
    raise_exception = True

    # HtmxMixin
    htmx_template_name = "preparation_inscription/modification_unites_enseignement.html"

    # FormView
    template_name = "preparation_inscription/preparation_inscription.html"
    form_class = ModifierProprietesContenuForm

    @cached_property
    def contenu(self) -> GroupementContenantDTO:
        cmd = GetContenuGroupementCommand(
            code_formation=self.kwargs['code_programme'],
            annee=self.kwargs['annee'],
            code=self.kwargs.get('code_groupement', self.kwargs['code_programme']),
        )
        return message_bus_instance.invoke(cmd)

    def get_form_class(self):
        return formset_factory(ModifierProprietesContenuForm, extra=0)

    def get_initial(self) -> List:
        return [
            {
                'code': element.code,
                'bloc': element.bloc,
            }
            for element in self.contenu.elements_contenus
        ]

    def form_valid(self, formset):
        cmd = ModifierUEDuGroupementCommand(
            annee=self.kwargs['annee'],
            code_programme=self.kwargs['code_programme'],
            ajuster_dans=self.kwargs.get('code_groupement', self.kwargs['code_programme']),
            unites_enseignements=[
             ModifierUniteEnseignementCommand(
                    code=form.cleaned_data['code'],
                    annee=self.kwargs['annee'],
                    bloc=form.cleaned_data['bloc'],
                ) for form in formset if form.has_changed()
            ]
        )

        if cmd.unites_enseignements:
            try:
                message_bus_instance.invoke(cmd)
            except MultipleBusinessExceptions as e:
                for exception in e.exceptions:
                    form = next(
                        form for form in formset
                        if form.has_changed() and form.cleaned_data['code'] == exception.code
                    )
                    form.add_error('bloc', exception.message)

        self.display_success_error_counter(cmd, formset)
        if formset.is_valid():
            return redirect(self.get_success_url())
        return self.render_to_response(self.get_context_data(form=formset))

    def display_success_error_counter(self, cmd: ModifierUEDuGroupementCommand, formset):
        error_counter = sum(1 for form in formset if form.has_changed() and not form.is_valid())
        success_counter = len(cmd.unites_enseignements) - error_counter

        if error_counter > 0:
            messages.error(
                self.request,
                ngettext(
                    "There is %(error_counter)s error in form",
                    "There are %(error_counter)s errors in form",
                    error_counter
                ) % {'error_counter': error_counter}
            )
        if success_counter > 0:
            messages.success(self.request,  _('The learning units have been modified'))

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**self.kwargs),
            'contenu': self.contenu.elements_contenus,
            'intitule_groupement': self.get_intitule_groupement(),
            'intitule_complet_groupement': self.get_intitule_complet_groupement(),
            'annee': self.kwargs['annee'],
            'code_programme': self.kwargs['code_programme'],
            'code_groupement': self.kwargs['code_groupement']
        }

    def get_intitule_groupement(self) -> str:
        return self.contenu.intitule

    def get_intitule_complet_groupement(self) -> str:
        return self.contenu.intitule_complet

    def get_success_url(self) -> str:
        return reverse(
            'consulter_contenu_groupement_view',
            args=self.args,
            kwargs=self.kwargs
        ) + "?{}=1".format(RAFRAICHIR_GROUPEMENT_CONTENANT)

    def get_permission_object(self):
        return GroupYear.objects.get(
            partial_acronym=self.kwargs['code_programme'],
            academic_year__year=self.kwargs['annee']
        )
