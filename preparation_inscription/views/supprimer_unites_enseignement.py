from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import gettext as _
from django.views.generic import TemplateView

from base.ddd.utils.business_validator import MultipleBusinessExceptions
from base.utils.htmx import HtmxMixin
from base.views.common import display_success_messages, display_error_messages
from ddd.logic.preparation_programme_annuel_etudiant.commands import SupprimerUEDuProgrammeCommand, \
    GetUniteEnseignementCommand, GetContenuGroupementCommand
from education_group.models.group_year import GroupYear
from infrastructure.messages_bus import message_bus_instance
from osis_role.contrib.views import PermissionRequiredMixin


class SupprimerUnitesEnseignementView(PermissionRequiredMixin, LoginRequiredMixin, HtmxMixin, TemplateView):
    name = 'supprimer_unites_enseignement_view'
    permission_required = 'preparation_inscription.can_delete_unites_enseignement_du_programme'
    template_name = "preparation_inscription/supprimer_unites_enseignement.html"
    htmx_template_name = "preparation_inscription/supprimer_unites_enseignement.html"

    @cached_property
    def code_groupement(self):
        return self.kwargs.get('code_groupement', self.code_programme)

    @cached_property
    def code_programme(self):
        return self.kwargs['code_programme']

    @cached_property
    def annee(self):
        return self.kwargs['annee']

    @cached_property
    def contenu(self):
        return message_bus_instance.invoke(
            GetContenuGroupementCommand(
                code_formation=self.code_programme,
                annee=self.annee,
                code=self.code_groupement,
            )
        )

    @cached_property
    def intitule_groupement(self):
        return self.contenu.intitule

    @cached_property
    def intitule_programme(self):
        return self.contenu.intitule_complet

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            'deletable_content': self.get_deletable_content(),
            'intitule_groupement': self.intitule_groupement,
            'intitule_complet_groupement': self.intitule_programme,
            'annee': self.annee,
            'code_programme': self.code_programme,
            'code_groupement': self.code_groupement
        }

    def get_deletable_content(self):
        return [ue for ue in self.contenu.elements_contenus if not ue.supprime]

    def post(self, request, *args, **kwargs):
        to_delete = request.POST.getlist('to_delete')
        cmd = self._get_command(to_delete)
        try:
            message_bus_instance.invoke(cmd)
            success_message = _('The learning units {} have been deleted').format(', '.join(to_delete))
            display_success_messages(self.request, success_message)
        except MultipleBusinessExceptions as exceptions:
            messages = [exception.message for exception in exceptions.exceptions]
            display_error_messages(self.request, messages)
            return self.get(request, *args, **kwargs)
        return redirect(self.get_consulter_contenu_groupement_url())

    def _get_command(self, to_delete):
        return SupprimerUEDuProgrammeCommand(
            code_programme=self.kwargs['code_programme'],
            annee=self.kwargs['annee'],
            retirer_de=self.kwargs['code_groupement'],
            unites_enseignements=[GetUniteEnseignementCommand(code=code) for code in to_delete]
        )

    def get_consulter_contenu_groupement_url(self):
        return reverse('consulter_contenu_groupement_view', args=self.args, kwargs=self.kwargs)

    def get_permission_object(self):
        return GroupYear.objects.get(
            partial_acronym=self.kwargs['code_programme'],
            academic_year__year=self.kwargs['annee']
        )
