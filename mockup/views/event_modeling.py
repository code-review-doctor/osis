from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


# class EventModelingView(LoginRequiredMixin, TemplateView):
#     name = 'event-modeling-view'
# 
#     # TemplateView
#     template_name = "mockup/event_modeling.html"
# 
#     def get_context_data(self, **kwargs):
#         return {
#             **super().get_context_data(**kwargs),
#             'element': self.get_element(),
#         }
# 
#     def get_element(self):
#         return {
#             'code_ue': '1',
#             'intitule': '2',
#             'volumes': '3',
#             'bloc': '4',
#             'quadri': '5',
#             'credits': '6',
#         }


from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from dal import autocomplete
from django import forms
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.translation import gettext_lazy as _

from base.forms.utils.choice_field import add_blank
from base.models.enums.active_status import ActiveStatusEnum
from education_group.forms.fields import MainEntitiesVersionChoiceField, UpperCaseCharField


class SearchForm(forms.Form):
    autocomplete = forms.ChoiceField(
        required=False,
        label=_('Label').capitalize(),
        widget=autocomplete.ListSelect2(
            url='venetmodeling-autocomplete',
            attrs={'data-html': True, 'data-placeholder': _('Name')},
        )
    )
    code_ue = UpperCaseCharField(max_length=15, label=_("code_ue").capitalize())
    intitule = forms.ChoiceField(
        initial=ActiveStatusEnum.ACTIVE.name,
        choices=add_blank(list(ActiveStatusEnum.choices())),
        label=_("intitule").capitalize(),
    )
    volumes = forms.IntegerField(
        label=_("volumes").capitalize(),
        required=False,
    )
    bloc = forms.BooleanField(label=_('bloc').capitalize())
    management_entity = MainEntitiesVersionChoiceField(
        queryset=None,
        label=_('management_entity').capitalize(),
        required=False
    )
    quadri = forms.DecimalField(
        max_digits=7,
        decimal_places=4,
        label=_('quadri').capitalize(),
        validators=[MinValueValidator(1), MaxValueValidator(9999)],
    )

    def __init__(self, *args, user: User, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)


class EventModelingView(LoginRequiredMixin, TemplateView):
    name = 'EventModelingView'
    # TemplateView
    template_name = "mockup/event_modeling.html"

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            'search_form': self.get_search_form(),
            'search_result': self.get_search_result(),
        }

    def get_search_form(self):
        return SearchForm(data=self.request.GET or None, user=self.request.user)

    def get_search_result(self):
        data = [
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
        ]  # TODO :: message_bus.invoke(Command)
        return data


from base.models.utils.utils import ChoiceEnum


class TypeAjustement(ChoiceEnum):
    SUPPRESSION = _('SUPPRESSION')
    MODIFICATION = _('MODIFICATION')
    AJOUT = _('AJOUT')
