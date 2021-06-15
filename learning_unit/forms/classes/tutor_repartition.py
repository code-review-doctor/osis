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
from ddd.logic.attribution.commands import DistributeClassToTutorCommand
from ddd.logic.attribution.domain.model.tutor import Tutor
from ddd.logic.learning_unit.commands import CreateEffectiveClassCommand
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


class ClassTutorRepartitionForm(DisplayExceptionsByFieldNameMixin, forms.Form):

    field_name_by_exception = {
        exceptions.AnnualVolumeInvalidException: ('volume',),
    }

    full_name = forms.CharField(max_length=255, required=False, label=_('Tutor (full)'))
    function = forms.CharField(max_length=255, required=False, label=_('Function'))
    # attribution.models.enums.function.Functions
    class_volume = VolumeField(
        widget=DecimalFormatInput(render_value=True),
        required=False,
    )
    volume = VolumeField(
        widget=DecimalFormatInput(render_value=True),
        required=True,
    )

    class_type = forms.CharField(required=False)
    substitute = forms.CharField(required=False)

    def __init__(self,
                 *args,
                 learning_unit_attribution: 'LearningUnitAttribution' = None,
                 effective_class: 'EffectiveClass' = None,
                 tutor: 'Tutor' = None,
                 user: User,
                 **kwargs
                 ):
        self.user = user
        super().__init__(*args, **kwargs)

        self.learning_unit_attribution = learning_unit_attribution
        self.effective_class = effective_class
        self.tutor = tutor
        if self.tutor:
            self.fields['full_name'].initial = "{}, {}".format(tutor.last_name, tutor.first_name)
        if self.learning_unit_attribution:
            self.fields['function'].initial = \
                self.learning_unit_attribution.function.value if self.learning_unit_attribution.function else ''
        if self.effective_class:
            self.fields['class_volume'].initial = \
                (self.effective_class.volumes.volume_first_quadrimester or 0) + \
                (self.effective_class.volumes.volume_second_quadrimester or 0)
        self.fields['substitute'].initial = '???'

    def get_command(self) -> DistributeClassToTutorCommand:
        return DistributeClassToTutorCommand(
            tutor_personal_id_number=self.tutor.entity_id.personal_id_number,
            learning_unit_attribution_uuid=self.learning_unit_attribution.entity_id.uuid,
            class_code=self.effective_class.entity_id.class_code,
            distributed_volume=self.cleaned_data['volume'] or 0,
        )
