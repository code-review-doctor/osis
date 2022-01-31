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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django import forms
from django.utils.translation import gettext_lazy

from base.forms.exceptions import InvalidFormException
from base.models.entity_version import EntityVersion
from ddd.logic.encodage_des_notes.soumission.commands import GetChoixEntitesAdresseFeuilleDeNotesCommand, \
    EncoderAdresseFeuilleDeNotesSpecifique, \
    EncoderAdresseEntiteCommeAdresseFeuilleDeNotes, SupprimerAdresseFeuilleDeNotesPremiereAnneeDeBachelier
from ddd.logic.encodage_des_notes.soumission.domain.validator.exceptions import \
    EntiteAdressePremiereAnneeDeBachelierIdentiqueAuBachlierException, \
    AdresseSpecifiquePremiereAnneeDeBachelierIdentiqueAuBachlierException
from ddd.logic.encodage_des_notes.soumission.dtos import AdresseFeuilleDeNotesDTO
from infrastructure.messages_bus import message_bus_instance
from reference.models.country import Country


class EntityVersionModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj: 'EntityVersion') -> str:
        return "{} - {}".format(obj.acronym, obj.title)


class ScoreSheetAddressForm(forms.Form):
    entity = forms.ChoiceField(
        required=False,
        label=gettext_lazy('Please select an address'),
    )
    recipient = forms.CharField(max_length=255, label=gettext_lazy('Recipient'), required=False)
    location = forms.CharField(max_length=255, label=gettext_lazy('Street and number'), required=False)
    postal_code = forms.CharField(max_length=255, label=gettext_lazy('Postal code'), required=False)
    city = forms.CharField(max_length=255, label=gettext_lazy('City'), required=False)
    country = forms.ModelChoiceField(
        queryset=Country.objects.all(),
        required=False,
        label=gettext_lazy('Country'),
        to_field_name="name"
    )
    phone = forms.CharField(max_length=64, label=gettext_lazy('Phone'), required=False)
    fax = forms.CharField(max_length=64, label=gettext_lazy('Fax'), required=False)
    email = forms.EmailField(max_length=128, label=gettext_lazy('Email'), required=False)

    def __init__(self, *args, nom_cohorte: str, **kwargs):
        super().__init__(*args, **kwargs)
        self.nom_cohorte = nom_cohorte
        self._init_entity_field()

    def _init_entity_field(self):
        cmd = GetChoixEntitesAdresseFeuilleDeNotesCommand(nom_cohorte=self.nom_cohorte)
        entite_dtos = message_bus_instance.invoke(cmd)

        choices = entite_dtos.choix
        choices.append((None, gettext_lazy('Customized')))

        self.fields['entity'].choices = tuple(choices)
        self._get_initial_entity_field()

    def _get_initial_entity_field(self):
        self.initial['entity'] = next(
            (choice[0] for choice in self.fields['entity'].choices if choice[1] == self.initial['recipient']),
            None
        )

    def clean(self):
        cleaned_data = super().clean()

        entity = cleaned_data.get('entity')
        if not entity:
            self.check_field_required(cleaned_data, "recipient")
            self.check_field_required(cleaned_data, "location")
            self.check_field_required(cleaned_data, "postal_code")
            self.check_field_required(cleaned_data, "city")

    def check_field_required(self, cleaned_data, field_name):
        error_message = self.fields[field_name].error_messages['required']

        if not cleaned_data.get(field_name):
            self.add_error(field_name, error_message)

    def save(self):
        try:
            if self.cleaned_data['entity']:
                return self._encoder_adresse_entite_comme_adresse()
            return self._encoder_adresse_specifique()
        except EntiteAdressePremiereAnneeDeBachelierIdentiqueAuBachlierException as e:
            self.add_error("entity", e.message)
            raise InvalidFormException()
        except AdresseSpecifiquePremiereAnneeDeBachelierIdentiqueAuBachlierException as e:
            self.add_error(None, e.message)
            raise InvalidFormException()

    def _encoder_adresse_specifique(self):
        cmd = EncoderAdresseFeuilleDeNotesSpecifique(
            nom_cohorte=self.nom_cohorte,
            destinataire=self.cleaned_data['recipient'],
            rue_numero=self.cleaned_data['location'],
            code_postal=self.cleaned_data['postal_code'],
            ville=self.cleaned_data['city'],
            pays=self.cleaned_data['country'].name if self.cleaned_data['country'] else '',
            telephone=self.cleaned_data['phone'],
            fax=self.cleaned_data['fax'],
            email=self.cleaned_data['email']
        )
        return message_bus_instance.invoke(cmd)

    def _encoder_adresse_entite_comme_adresse(self):
        cmd = EncoderAdresseEntiteCommeAdresseFeuilleDeNotes(
            nom_cohorte=self.nom_cohorte,
            type_entite=self.cleaned_data['entity'],
            email=self.cleaned_data['email']
        )
        return message_bus_instance.invoke(cmd)


class FirstYearBachelorScoreSheetAddressForm(ScoreSheetAddressForm):
    specific_address = forms.BooleanField(
        label=gettext_lazy(
            "Define a specific address for the first year of bachelor (if different from the addresse of the bachelor)"
        ),
        required=False
    )

    def __init__(
            self,
            *args,
            adresse_bachelier: 'AdresseFeuilleDeNotesDTO',
            nom_cohorte_premiere_annee: str,
            **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.adresse_bachelier = adresse_bachelier
        self.nom_cohorte = nom_cohorte_premiere_annee

    def save(self):
        if not self.cleaned_data['specific_address']:
            return self._supprimer_adresse_par_adresse_bachelier()
        return super().save()

    def _supprimer_adresse_par_adresse_bachelier(self):
        cmd = SupprimerAdresseFeuilleDeNotesPremiereAnneeDeBachelier(nom_cohorte=self.nom_cohorte)
        return message_bus_instance.invoke(cmd)
