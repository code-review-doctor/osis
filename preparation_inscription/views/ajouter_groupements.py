

from dal import autocomplete
from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

from education_group.forms.fields import MainEntitiesVersionChoiceField, UpperCaseCharField


class SearchGroupementsForm(forms.Form):
    autocomplete = forms.ChoiceField(
        required=False,
        label=_('Label').capitalize(),
        widget=autocomplete.ListSelect2(
            url='-autocomplete',
            attrs={'data-html': True, 'data-placeholder': _('Name')},
        )
    )
    code = UpperCaseCharField(max_length=15, label=_("code").capitalize(), required=False)
    sigle = UpperCaseCharField(max_length=15, label=_("sigle").capitalize(), required=False)
    # sigle = forms.ChoiceField(
    #     initial=ActiveStatusEnum.ACTIVE.name,
    #     choices=add_blank(list(ActiveStatusEnum.choices())),
    #     label=_("sigle").capitalize(),
    # )
    intitule = UpperCaseCharField(max_length=15, label=_("intitule").capitalize(), required=False)
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


class AjouterGroupementsView(LoginRequiredMixin, TemplateView):
    name = 'ajouter-groupements-view'

    # TemplateView
    template_name = "preparation_inscription/ajouter_groupements.html"
    htmx_template_name = "preparation_inscription/ajouter_groupements.html"

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            'search_form': self.get_search_form(),
            'search_results': self.get_search_result(),
            'annee': 2020,
            'code_programme': 'LECGE100B'
        }

    def get_search_form(self):
        return SearchGroupementsForm(data=self.request.GET or None, user=self.request.user)

    def get_search_result(self):
        data = [
            {
                'code': 'LECGE101R',
                'sigle': 'MAT2ECGE',
                'intitule': 'Economie et gestion',
            },
            {
                'code': 'LECGE102R',
                'sigle': 'MAT3ECGE',
                'intitule': 'Informatique et méthodes en économie et en gestion',
            },
        ]  # TODO :: message_bus.invoke(Command)
        return data
