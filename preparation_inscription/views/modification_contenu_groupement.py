from django import forms
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView
from rules.contrib.views import LoginRequiredMixin

from base.forms.utils.choice_field import add_blank
from base.models.enums.active_status import ActiveStatusEnum
from base.utils.htmx import HtmxMixin
from education_group.forms.fields import MainEntitiesVersionChoiceField, UpperCaseCharField
from preparation_inscription.views.consulter_contenu_groupement import TypeAjustement


class ModifierProprietesContenuForm(forms.Form):
    # autocomplete = forms.ChoiceField(
    #     required=False,
    #     label=_('Label').capitalize(),
    #     widget=autocomplete.ListSelect2(
    #         url='-autocomplete',
    #         attrs={'data-html': True, 'data-placeholder': _('Name')},
    #     )
    # )
    champs1 = UpperCaseCharField(max_length=15, label=_("champs1").capitalize())
    champs2 = forms.ChoiceField(
        initial=ActiveStatusEnum.ACTIVE.name,
        choices=add_blank(list(ActiveStatusEnum.choices())),
        label=_("champs2").capitalize(),
    )
    champs3 = forms.IntegerField(
        label=_("champs3").capitalize(),
        required=False,
    )
    champs4 = forms.BooleanField(label=_('champs4').capitalize())
    management_entity = MainEntitiesVersionChoiceField(
        queryset=None,
        label=_('champs4').capitalize(),
    )
    champs5 = forms.DecimalField(
        max_digits=7,
        decimal_places=4,
        label=_('champs5').capitalize(),
        validators=[MinValueValidator(1), MaxValueValidator(9999)],
    )

    def __init__(self, *args, user: User, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)


class ModifierProprietesContenuView(LoginRequiredMixin, HtmxMixin, FormView):
    name = 'modifier_proprietes_contenu_view'

    # FormView
    template_name = "preparation_inscription/preparation_inscription.html"
    htmx_template_name = "preparation_inscription/modification_unites_enseignement.html"

    form_class = ModifierProprietesContenuForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, formset):
        # TODO :: to implement
        # cmd = Command(...)
        # message__bus.invoke(cmd)
        # display_error_messages(self.request, messages)
        # display_success_messages(self.request, messages)
        # self.render_to_response(self.get_context_data(form=self.get_form(self.form_class)))
        return super().form_valid(formset)

    def get_success_url(self):
        # TODO :: to implement or to remove
        return super().get_success_url()

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**self.kwargs),
            'search_result': self.get_contenu_groupement_modifiable(),
            'form': self.get_form(self.form_class),
            'intitule_groupement': self.get_intitule_groupement(),
            'intitule_programme': self.get_intitule_programme(),
        }

    def get_contenu_groupement_modifiable(self):
        data = [
            {
                'code_ue': 'LESPO1113',
                'intitule': 'Sociologie et anthropologie des mondes contemporains',
                'volumes': '10',
                'bloc': '1',
                'quadri': 'Q1',
                'credits': '5/5',
                'session': 'Oui',
                'obligatoire': 'Oui',
                'commentaire_fr': """Lorem Ipsum est un générateur de faux textes aléatoires. Vous choisissez le nombre de paragraphes, de mots ou de listes. Vous obtenez alors un texte aléatoire que vous pourrez ensuite utiliser librement dans vos maquettes.
                    Le texte généré est du pseudo latin et peut donner l'impression d'être du vrai texte.
                    Faux-Texte est une réalisation du studio de création de sites internet indépendant Prélude Prod.
                    Si vous aimez la photographie d'art et l'esprit zen, jetez un œil sur le site de ce photographe à Palaiseau, en Essonne (France).
                """,
                'commentaire_en': '',
                'type_ajustement': TypeAjustement.SUPPRESSION.name,
            },
            {
                'code_ue': 'LESPO1321',
                'intitule': 'Economic, Political and Social Ethics',
                'volumes': '15+10',
                'bloc': '1',
                'quadri': 'Q1',
                'credits': '4/5',
                'session': 'Oui',
                'obligatoire': 'Oui',
                'commentaire_fr': '',
                'commentaire_en': '',
                'type_ajustement': TypeAjustement.SUPPRESSION.name,
            },
            {
                'code_ue': 'LESPO1114',
                'intitule': 'Political Science',
                'volumes': '30',
                'bloc': '2',
                'quadri': 'Q1',
                'credits': '5/5',
                'session': 'Oui',
                'obligatoire': 'Oui',
                'commentaire_fr': '',
                'commentaire_en': '',
                'type_ajustement': TypeAjustement.MODIFICATION.name,
            },
            {
                'code_ue': 'LINGE1122',
                'intitule': 'Physique 1',
                'volumes': '30',
                'bloc': '1',
                'quadri': 'Q2',
                'credits': '3/3',
                'session': 'Oui',
                'obligatoire': 'Oui',
                'commentaire_fr': '',
                'commentaire_en': '',
                'type_ajustement': TypeAjustement.AJOUT.name,
            },
            {
                'code_ue': 'LINGE1125',
                'intitule': 'Séminaire de travail universitaire en gestion',
                'volumes': '25',
                'bloc': '1',
                'quadri': 'Q2',
                'credits': '5/5',
                'session': 'Oui',
                'obligatoire': 'Non',
                'commentaire_fr': '',
                'commentaire_en': '',
                'type_ajustement': TypeAjustement.AJOUT.name,
            },
        ]  # TODO :: message_bus.invoke(Command)
        return data

    def get_intitule_groupement(self):
        # TODO :: to implement
        return "Intitulé groupement"

    def get_intitule_programme(self):
        # TODO :: to implement
        return "Intitulé programme"
