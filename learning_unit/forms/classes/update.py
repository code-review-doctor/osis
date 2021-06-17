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
from typing import List

from django import forms
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from base.forms.learning_unit.edition_volume import VolumeField
from base.forms.utils.choice_field import BLANK_CHOICE_DISPLAY, add_blank
from base.models.enums import quadrimesters
from base.models.enums.internship_subtypes import InternshipSubtype
from base.models.enums.learning_unit_year_periodicity import PeriodicityEnum
from base.models.enums.learning_unit_year_session import DerogationSession
from base.utils.mixins_for_forms import DisplayExceptionsByFieldNameMixin
from ddd.logic.learning_unit.commands import CreateEffectiveClassCommand, UpdateEffectiveClassCommand
from ddd.logic.learning_unit.domain.model.effective_class import EffectiveClass
from ddd.logic.learning_unit.domain.model.learning_unit import LearningUnit
from ddd.logic.learning_unit.domain.validator import exceptions
from ddd.logic.shared_kernel.campus.commands import SearchUclouvainCampusesCommand
from ddd.logic.shared_kernel.campus.domain.model.uclouvain_campus import UclouvainCampus
from ddd.logic.shared_kernel.language.commands import SearchLanguagesCommand
from ddd.logic.shared_kernel.language.domain.model.language import Language
from education_group.forms.fields import UpperCaseCharField
from infrastructure.messages_bus import message_bus_instance
from osis_common.forms.widgets import DecimalFormatInput


class ClassForm(DisplayExceptionsByFieldNameMixin, forms.Form):
    EMPTY_LABEL = BLANK_CHOICE_DISPLAY
    field_name_by_exception = {
        exceptions.AnnualVolumeInvalidException: ('hourly_volume_partial_q1', 'hourly_volume_partial_q2'),
    }

    class_code = UpperCaseCharField(max_length=1, required=True, label=_('Code'))

    title_fr = forms.CharField(max_length=255, required=True, label=_('Class specific complement'))
    title_en = forms.CharField(max_length=255, required=False, label=_('Class specific complement'))

    hourly_volume_partial_q1 = VolumeField(
        label=_('Vol. Q1'),
        widget=DecimalFormatInput(render_value=True),
        required=False,
    )
    hourly_volume_partial_q2 = VolumeField(
        label=_('Vol. Q2'),
        widget=DecimalFormatInput(render_value=True),
        required=False,
    )
    session = forms.ChoiceField(
        required=False,
        label=_("Derogation's session")
    )
    quadrimester = forms.ChoiceField(
        choices=add_blank(quadrimesters.DerogationQuadrimester.choices()),
        required=False,
        label=_("Quadrimester")
    )

    class_type = forms.CharField(disabled=True, required=False)

    learning_unit_year = forms.ChoiceField(disabled=True, label=_('Academic year'), required=False)
    learning_unit_code = forms.CharField(disabled=True, max_length=15, required=False)
    learning_unit_type = forms.ChoiceField(disabled=True, label=_('Type'), required=False)
    learning_unit_internship_subtype = forms.ChoiceField(disabled=True, label=_('Internship subtype'), required=False)
    learning_unit_credits = forms.CharField(
        disabled=True,
        label=_('Credits'),
        required=False,
        widget=DecimalFormatInput(render_value=True)
    )
    learning_unit_periodicity = forms.ChoiceField(disabled=True, label=_('Periodicity'), required=False)
    learning_unit_state = forms.BooleanField(disabled=True, label=_('Active'), required=False)
    learning_unit_language = forms.ChoiceField(disabled=True, label=_('Language'), required=False)
    learning_unit_professional_integration = forms.BooleanField(
        disabled=True,
        label=_('Professional integration'),
        required=False
    )
    learning_unit_common_title_fr = forms.CharField(disabled=True, label=_('Common part'), required=False)
    learning_unit_common_title_en = forms.CharField(disabled=True, label=_('Common part'), required=False)
    learning_unit_remarks_faculty = forms.CharField(
        disabled=True,
        label=_('Faculty remark (unpublished)'),
        required=False
    )
    learning_unit_remarks_publication_fr = forms.CharField(
        disabled=True,
        label=_('Other remark (intended for publication)'),
        required=False
    )
    learning_unit_remarks_publication_en = forms.CharField(
        disabled=True,
        label=_('Other remark in english (intended for publication)'),
        required=False
    )
    volume_total_annual = VolumeField(
        label=_('Vol. annual'),
        widget=DecimalFormatInput(render_value=True),
        required=False,
        disabled=True
    )
    planned_classes = forms.IntegerField(
        label=_('Planned classes'),
        disabled=True,
        widget=forms.TextInput(),
        required=False
    )
    repartition_volume_requirement_entity = forms.CharField(disabled=True, required=False)

    learning_unit_campus = forms.ChoiceField(label=_("Learning location"))
    learning_unit_responsible_entity = forms.ChoiceField(
        required=False,
        disabled=True,
        label=_('Requirement entity')
    )
    learning_unit_allocation_entity = forms.ChoiceField(
        required=False,
        disabled=True,
        label=_('Allocation entity')
    )

    def __init__(self, *args, learning_unit: 'LearningUnit' = None, user: User, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

        self.learning_unit = learning_unit
        learning_unit = self.learning_unit
        self.fields['learning_unit_code'].initial = learning_unit.code
        self.__init_year_choices(learning_unit)
        self.fields['learning_unit_credits'].initial = learning_unit.credits
        self.fields['learning_unit_type'].choices = [('CLASS', _("Class"))]
        self.fields['learning_unit_type'].initial = 'CLASS'
        self.__init_internship_subtype(learning_unit)
        self.__init_periodicity(learning_unit)
        self.fields['learning_unit_state'].initial = self.learning_unit.is_active
        self.__init_language_choices()
        self.fields['learning_unit_professional_integration'].initial = self.learning_unit.professional_integration
        self.__init_titles(learning_unit)
        self.__init_remarks(learning_unit)
        self.__init_volumes()
        self.__init_learning_unit_responsible_field()
        self.__init_learning_unit_campus()

    def __init_volumes(self):
        if self.learning_unit.has_practical_volume() and not self.learning_unit.has_lecturing_volume():
            volumes = self.learning_unit.practical_part.volumes
            self.fields['class_type'].initial = _('Practical exercises')
        else:
            volumes = self.learning_unit.lecturing_part.volumes
            self.fields['class_type'].initial = _('Lecturing')

        # Fields not editable from LearningUnit
        repartition = volumes.volumes_repartition
        self.fields['planned_classes'].initial = volumes.planned_classes
        self.fields['repartition_volume_requirement_entity'].initial = repartition.repartition_volume_responsible_entity
        attribution_entity_code = self.learning_unit.attribution_entity_identity.code
        self.fields['learning_unit_allocation_entity'].choices = [(attribution_entity_code, attribution_entity_code)]
        self.fields['learning_unit_allocation_entity'].initial = attribution_entity_code

        # Fields editable for class, pre-filled from LearningUnit values
        quadri = self.learning_unit.derogation_quadrimester
        self.fields['quadrimester'].initial = quadri.name if quadri else None
        self.__init_session()
        self.fields['hourly_volume_partial_q1'].initial = volumes.volume_first_quadrimester
        self.fields['hourly_volume_partial_q2'].initial = volumes.volume_second_quadrimester
        self.fields['volume_total_annual'].initial = volumes.volume_annual

    def __init_remarks(self, learning_unit):
        self.fields['learning_unit_remarks_faculty'].initial = learning_unit.remarks.faculty
        self.fields['learning_unit_remarks_publication_fr'].initial = learning_unit.remarks.publication_fr
        self.fields['learning_unit_remarks_publication_en'].initial = learning_unit.remarks.publication_en

    def __init_titles(self, learning_unit):
        self.fields['learning_unit_common_title_fr'].initial = learning_unit.complete_title_fr
        self.fields['learning_unit_common_title_en'].initial = learning_unit.complete_title_en

    def __init_periodicity(self, learning_unit):
        self.fields['learning_unit_periodicity'].choices = add_blank(PeriodicityEnum.choices())
        self.fields['learning_unit_periodicity'].initial = learning_unit.periodicity.name

    def __init_internship_subtype(self, learning_unit):
        self.fields['learning_unit_internship_subtype'].choices = add_blank(InternshipSubtype.choices())
        subtype = learning_unit.internship_subtype
        self.fields['learning_unit_internship_subtype'].initial = subtype.name if subtype else None

    def __init_year_choices(self, learning_unit):
        self.fields['learning_unit_year'].choices = [(learning_unit.year, str(learning_unit.entity_id.academic_year))]
        self.initial['learning_unit_year'] = learning_unit.year

    def __init_learning_unit_campus(self):
        campuses = message_bus_instance.invoke(SearchUclouvainCampusesCommand())  # type: List[UclouvainCampus]
        choices = [(campus.entity_id.uuid, str(campus)) for campus in campuses]
        self.fields['learning_unit_campus'].choices = choices
        campus = next(
            (campus for campus in campuses if campus.entity_id == self.learning_unit.teaching_place),
            None
        )
        self.initial['learning_unit_campus'] = campus.entity_id.uuid

    def get_command(self) -> CreateEffectiveClassCommand:
        return CreateEffectiveClassCommand(
            class_code=self.cleaned_data['class_code'],
            learning_unit_code=self.learning_unit.code,
            year=self.learning_unit.year,
            title_fr=self.cleaned_data['title_fr'],
            title_en=self.cleaned_data['title_en'],
            teaching_place_uuid=self.cleaned_data['learning_unit_campus'],
            derogation_quadrimester=self.cleaned_data['quadrimester'],
            session_derogation=self.cleaned_data['session'],
            volume_first_quadrimester=self.cleaned_data['hourly_volume_partial_q1'] or 0,
            volume_second_quadrimester=self.cleaned_data['hourly_volume_partial_q2'] or 0,
        )

    def __init_language_choices(self):
        all_languages = message_bus_instance.invoke(SearchLanguagesCommand())  # type: List[Language]
        choices = add_blank([(lang.code_iso, lang.name) for lang in all_languages])
        self.fields['learning_unit_language'].choices = choices
        self.fields['learning_unit_language'].initial = self.learning_unit.language_id.code_iso

    def __init_learning_unit_responsible_field(self):
        self.fields['learning_unit_responsible_entity'].choices = [
            (self.learning_unit.responsible_entity_identity.code, self.learning_unit.responsible_entity_identity.code),
        ]
        self.fields['learning_unit_responsible_entity'].initial = self.learning_unit.responsible_entity_identity.code

    def __init_session(self):
        session_choices = []
        for session_choice in DerogationSession.choices():
            session_choices.append((session_choice[1], session_choice[1]))
        self.fields['session'].choices = add_blank(session_choices)
        session = self.learning_unit.derogation_session
        self.fields['session'].initial = session.value if session else None


class UpdateClassForm(ClassForm):

    class_code = UpperCaseCharField(max_length=1, disabled=True, required=False, label=_('Code'))

    def __init__(
            self,
            *args,
            learning_unit: 'LearningUnit' = None,
            effective_class: 'EffectiveClass' = None,
            user: User,
            **kwargs
    ):
        super().__init__(*args, learning_unit=learning_unit, user=user, **kwargs)
        self.__init_effective_class_fields_for_update(effective_class)

    def __init_effective_class_fields_for_update(self, effective_class: EffectiveClass):
        self.fields['class_code'].initial = effective_class.entity_id.class_code
        quadri = effective_class.derogation_quadrimester
        self.fields['quadrimester'].initial = quadri.name if quadri else None
        session = effective_class.session_derogation
        self.fields['session'].initial = session.value if session else None
        self.fields['title_fr'].initial = effective_class.titles.fr
        self.fields['title_en'].initial = effective_class.titles.en
        self.fields['hourly_volume_partial_q1'].initial = effective_class.volumes.volume_first_quadrimester
        self.fields['hourly_volume_partial_q2'].initial = effective_class.volumes.volume_second_quadrimester
        self.__init_learning_unit_campus(effective_class.teaching_place)

    def get_command(self) -> UpdateEffectiveClassCommand:
        return UpdateEffectiveClassCommand(
            class_code=self.cleaned_data['class_code'],
            learning_unit_code=self.learning_unit.code,
            year=self.learning_unit.year,
            title_fr=self.cleaned_data['title_fr'],
            title_en=self.cleaned_data['title_en'],
            teaching_place_uuid=self.cleaned_data['learning_unit_campus'],
            derogation_quadrimester=self.cleaned_data['quadrimester'],
            session_derogation=self.cleaned_data['session'],
            volume_first_quadrimester=self.cleaned_data['hourly_volume_partial_q1'],
            volume_second_quadrimester=self.cleaned_data['hourly_volume_partial_q2'],
        )

    def __init_learning_unit_campus(self, teaching_place):
        campuses = message_bus_instance.invoke(SearchUclouvainCampusesCommand())  # type: List[UclouvainCampus]
        choices = [(campus.entity_id.uuid, str(campus)) for campus in campuses]
        self.fields['learning_unit_campus'].choices = choices
        campus = next(
            (campus for campus in campuses if campus.entity_id == teaching_place),
            None
        )
        self.initial['learning_unit_campus'] = campus.entity_id.uuid
