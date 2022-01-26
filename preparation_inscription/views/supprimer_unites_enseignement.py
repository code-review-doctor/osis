from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

from base.ddd.utils.business_validator import MultipleBusinessExceptions
from base.utils.htmx import HtmxMixin
from base.views.common import display_success_messages, display_error_messages
from ddd.logic.preparation_programme_annuel_etudiant.commands import RetirerUEDuProgrammeCommand, \
    GetUniteEnseignementCommand
from infrastructure.messages_bus import message_bus_instance
from preparation_inscription.views.consulter_contenu_groupement import TypeAjustement


class SupprimerUnitesEnseignementView(LoginRequiredMixin, HtmxMixin, TemplateView):
    name = 'supprimer_unites_enseignement_view'

    # TemplateView
    template_name = "preparation_inscription/preparation_inscription.html"
    htmx_template_name = "preparation_inscription/supprimer_unites_enseignements.html"

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            'deletable_content': self.get_content(),
            'intitule_groupement': self.get_intitule_groupement(),
            'intitule_programme': self.get_intitule_programme(),
            'consulter_contenu_groupement_url': self.get_consulter_contenu_groupement_url()
        }

    def get_deletable_content(self):
        return [ue for ue in self.get_content() if ue['type_ajustement'] != TypeAjustement.SUPPRESSION.name]

    def get_content(self):
        return [
            {
                'code_ue': 'LESPO1113',
                'intitule': 'Sociologie...',
                'volumes': '10',
                'bloc': '1',
                'quadri': 'Q1',
                'credits': '5/5',
                'session': 'Oui',
                'obligatoire': '',
                'commentaire_fr': '',
                'commentaire_en': '',
                'type_ajustement': TypeAjustement.SUPPRESSION.name,
            },
            {
                'code_ue': 'LESPO1321',
                'intitule': 'Economic...',
                'volumes': '15+10',
                'bloc': '1',
                'quadri': 'Q1',
                'credits': '4/5',
                'session': 'Oui',
                'obligatoire': '',
                'commentaire_fr': '',
                'commentaire_en': '',
                'type_ajustement': TypeAjustement.SUPPRESSION.name,
            },
            {
                'code_ue': 'LESPO1114',
                'intitule': 'Political...',
                'volumes': '30',
                'bloc': '2',
                'quadri': 'Q1',
                'credits': '5/5',
                'session': 'Oui',
                'obligatoire': '',
                'commentaire_fr': '',
                'commentaire_en': '',
                'type_ajustement': TypeAjustement.MODIFICATION.name,
            },
            {
                'code_ue': 'LINGE1122',
                'intitule': 'Physique...',
                'volumes': '30',
                'bloc': '1',
                'quadri': 'Q2',
                'credits': '3/3',
                'session': 'Oui',
                'obligatoire': '',
                'commentaire_fr': '',
                'commentaire_en': '',
                'type_ajustement': TypeAjustement.AJOUT.name,
            },
            {
                'code_ue': 'LINGE1125',
                'intitule': 'Séminaire...',
                'volumes': '25',
                'bloc': '1',
                'quadri': 'Q2',
                'credits': '5/5',
                'session': 'Oui',
                'obligatoire': '',
                'commentaire_fr': '',
                'commentaire_en': '',
                'type_ajustement': TypeAjustement.AJOUT.name,
            },
        ]

    def get_intitule_groupement(self):
        # TODO :: to implement
        return "Intitulé groupement"

    def get_intitule_programme(self):
        # TODO :: to implement
        return "Intitulé programme"

    def post(self, request, *args, **kwargs):
        to_delete = request.POST.getlist('to_delete')
        cmd = self._get_command(to_delete)
        try:
            message_bus_instance.invoke(cmd)
            success_message = _('The learning units {} have been deleted').format(to_delete.join(', '))
            display_success_messages(self.request, success_message)
        except MultipleBusinessExceptions as exceptions:
            messages = [exception.message for exception in exceptions.exceptions]
            display_error_messages(self.request, messages)
            return self.get(request, *args, **kwargs)
        return redirect(self.get_consulter_contenu_groupement_url())

    def _get_command(self, to_delete):
        return RetirerUEDuProgrammeCommand(
            sigle_formation='',
            annee_formation=0,
            version_formation='',
            groupement_uuid='',
            transition_formation='',
            unites_enseignements=[
                GetUniteEnseignementCommand(code=code) for code in to_delete
            ]
        )

    def get_consulter_contenu_groupement_url(self):
        return reverse('consulter_contenu_groupement_view', args=self.args, kwargs=self.kwargs)
