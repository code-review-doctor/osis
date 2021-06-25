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

from django import forms
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from attribution.models.enums.function import Functions
from base.forms.learning_unit.edition_volume import VolumeField
from base.utils.mixins_for_forms import DisplayExceptionsByFieldNameMixin
from ddd.logic.attribution.commands import DistributeClassToTutorCommand
from ddd.logic.attribution.dtos import TutorAttributionToLearningUnitDTO
from ddd.logic.learning_unit.domain.model.effective_class import EffectiveClass
from ddd.logic.learning_unit.domain.validator import exceptions
from osis_common.forms.widgets import DecimalFormatInput


class ClassTutorRepartitionForm(DisplayExceptionsByFieldNameMixin, forms.Form):

    field_name_by_exception = {
        exceptions.AnnualVolumeInvalidException: ('volume',),
    }

    full_name = forms.CharField(max_length=255, required=False)
    function = forms.CharField(max_length=255, required=False, label=_('Function'))
    class_volume = VolumeField(
        widget=DecimalFormatInput(render_value=True),
        required=False,
    )
    volume = VolumeField(
        widget=DecimalFormatInput(render_value=True),
        required=True,
    )

    class_type = forms.CharField(required=False)

    def __init__(self,
                 *args,
                 effective_class: 'EffectiveClass' = None,
                 tutor: 'TutorAttributionToLearningUnitDTO' = None,
                 user: User,
                 **kwargs
                 ):
        self.user = user
        super().__init__(*args, **kwargs)

        self.effective_class = effective_class
        self.tutor = tutor

        if self.tutor:
            self.fields['full_name'].initial = tutor.full_name
        self.__init_function()
        if self.effective_class:
            self.fields['class_volume'].initial = \
                (self.effective_class.volumes.volume_first_quadrimester or 0) + \
                (self.effective_class.volumes.volume_second_quadrimester or 0)

    def __init_function(self):
        if self.tutor:
            self.fields['function'].initial = Functions.get_value(
                self.tutor.function) if self.tutor.function else ''

    def get_command(self) -> DistributeClassToTutorCommand:
        return DistributeClassToTutorCommand(
            tutor_personal_id_number=self.tutor.personal_id_number,
            learning_unit_attribution_uuid=self.tutor.attribution_uuid,
            class_code=self.effective_class.entity_id.class_code,
            distributed_volume=self.cleaned_data['volume'] or 0,
            learning_unit_code=self.effective_class.entity_id.learning_unit_identity.code,
            learning_unit_year=self.effective_class.entity_id.learning_unit_identity.year
        )
    # TODO : je pense qu'il faut ici un minimum de validation, mais je n'arrive pas à faire fonctionner ???
    # def clean_volume(self):
    #     print('clean_volume')
    #     volume = self.cleaned_data['volume']
    #     print(volume)
    #     if volume:
    #         if volume < 0:
    #             raise ValidationError(_('The volume value should be greather or equal to 0'))
    #         if volume > 10:
    #             print('ici')
    #             raise ValidationError(
    #                 _('The volume should be less than the class volume (%(class_volume)d)') %{
    #                     'class_volume': self.fields['class_volume'].initial
    #                 }
    #             )
    #     return volume
