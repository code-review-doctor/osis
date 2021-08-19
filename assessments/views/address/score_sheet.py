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
from django.contrib import messages
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView

from assessments.forms.score_sheet_address_new import ScoreSheetAddressForm, FirstYearBachelorScoreSheetAddressForm
from base.auth.roles import program_manager
from base.forms.exceptions import InvalidFormException
from base.models import academic_year
from base.models.education_group_year import EducationGroupYear
from ddd.logic.encodage_des_notes.soumission.commands import GetAdresseFeuilleDeNotesServiceCommand
from ddd.logic.encodage_des_notes.soumission.dtos import AdresseFeuilleDeNotesDTO
from education_group.models.cohort_year import CohortYear
from infrastructure.messages_bus import message_bus_instance
from osis_role.contrib.views import PermissionRequiredMixin


class ScoreSheetAddressView(PermissionRequiredMixin, FormView):
    form_class = ScoreSheetAddressForm
    permission_required = "assessments.can_access_scoreencoding"  # also base.can_access_education_group
    template_name = "assessments/address/score_sheet.html"

    @property
    def nom_cohorte(self) -> str:
        return self.kwargs['acronym']

    @cached_property
    def education_group_year(self):
        return EducationGroupYear.objects.select_related('education_group').get(
            acronym=self.nom_cohorte,
            academic_year=academic_year.current_academic_year()
        )

    @cached_property
    def score_sheet_address(self) -> 'AdresseFeuilleDeNotesDTO':
        cmd = GetAdresseFeuilleDeNotesServiceCommand(nom_cohorte=self.nom_cohorte)
        return message_bus_instance.invoke(cmd)

    def get_initial(self):
        initial = super().get_initial()
        initial.update({
            "entity": self.score_sheet_address.entite,
            "recipient": self.score_sheet_address.destinataire,
            "location": self.score_sheet_address.rue_numero,
            "postal_code": self.score_sheet_address.code_postal,
            "city": self.score_sheet_address.ville,
            "country": self.score_sheet_address.pays,
            "phone": self.score_sheet_address.telephone,
            "fax": self.score_sheet_address.fax,
            "email": self.score_sheet_address.email,
        })
        return initial

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs['nom_cohorte'] = self.nom_cohorte
        return form_kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({
            "nom_cohorte": self.nom_cohorte,
            "intitule": self.education_group_year.title,
            "est_gestionnaire_de_programme": program_manager.is_program_manager(
                self.request.user,
                education_group=self.education_group_year.education_group
            ),
        })

        return context

    def form_valid(self, form: 'ScoreSheetAddressForm'):
        try:
            form.save()
        except InvalidFormException:
            return self.form_invalid(form)
        messages.add_message(self.request, messages.SUCCESS, _("Score sheet address was successfully saved."))
        return super().form_valid(form)

    def get_success_url(self):
        return ""


class FirstYearBachelorScoreSheetAddressView(ScoreSheetAddressView):
    form_class = FirstYearBachelorScoreSheetAddressForm
    template_name = "assessments/address/first_year_bachelor_score_sheet.html"

    @property
    def nom_cohorte_bachelier(self) -> str:
        return self.nom_cohorte.replace("11BA", "1BA")

    @cached_property
    def first_year_bachelor(self) -> 'CohortYear':
        return CohortYear.objects.get_first_year_bachelor(
            education_group_year__acronym=self.nom_cohorte_bachelier,
            education_group_year__academic_year=academic_year.current_academic_year()
        )

    @cached_property
    def education_group_year(self) -> 'EducationGroupYear':
        return self.first_year_bachelor.education_group_year

    @cached_property
    def bachelor_score_sheet_address_dto(self) -> 'AdresseFeuilleDeNotesDTO':
        cmd = GetAdresseFeuilleDeNotesServiceCommand(nom_cohorte=self.nom_cohorte_bachelier)
        return message_bus_instance.invoke(cmd)

    def get_initial(self):
        initial = super().get_initial()
        initial.update({
            "specific_address": self.score_sheet_address.specifique_a_la_premiere_annee_de_bachelier
        })
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({
            "addresse_bachelier": self.bachelor_score_sheet_address_dto,
            "nom_cohorte_bachelier": self.nom_cohorte_bachelier,
        })

        return context
