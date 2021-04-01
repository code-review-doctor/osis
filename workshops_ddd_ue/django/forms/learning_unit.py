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

from base.forms.utils.choice_field import BLANK_CHOICE
from base.forms.utils.fields import OsisRichTextFormField
from base.models.academic_year import AcademicYear
from base.models.enums.internship_subtypes import InternshipSubtype
from base.models.enums.learning_container_year_types import LearningContainerYearType
from base.models.enums.learning_unit_year_periodicity import PeriodicityEnum
from base.utils.mixins_for_forms import DisplayExceptionsByFieldNameMixin
from ddd.logic.learning_unit.commands import CreateLearningUnitCommand
from ddd.logic.learning_unit.domain.validator import exceptions
from education_group.forms import fields
from education_group.forms.fields import UpperCaseCharField
from osis_common.ddd.interface import CommandRequest
from reference.models.language import Language, FR_CODE_LANGUAGE


class LearningUnitCreateForm(DisplayExceptionsByFieldNameMixin, forms.Form):

    field_name_by_exception = {
        # exceptions.EmptyRequiredFieldsException: ('code',
        #                                           'academic_year',
        #                                           'common_title_fr',
        #                                           'specific_title_fr',
        #                                           'credits',
        #                                           'internship_subtype',
        #                                           'responsible_entity',
        #                                           'periodicity',
        #                                           'language',),
        exceptions.AcademicYearLowerThan2019Exception: ('academic_year',),
        exceptions.CreditsShouldBeGreatherThanZeroException: ('credits',),
        exceptions.InternshipSubtypeMandatoryException: ('internship_subtype',),
        # exceptions.LearningUnitAlreadyExistsException: ('code', 'academic_year',),
        exceptions.LearningUnitCodeAlreadyExistsException: ('code', 'academic_year',),
        exceptions.InvalidResponsibleEntityTypeOrCodeException: ('responsible_entity',),
        exceptions.LearningUnitCodeStructureInvalidException: ('code',),
        # exceptions.SubdivisionAlreadyExistException: ('code',),
    }

    code = UpperCaseCharField(max_length=15, label=_("Code"), required=True)
    academic_year = forms.ModelChoiceField(
        queryset=AcademicYear.objects.all(),
        label=_("Validity"),
        required=True
    )  # FIXME
    type = forms.ChoiceField(
        choices=BLANK_CHOICE + list(LearningContainerYearType.choices()),
        label=_("Learning unit type"),
        required=True,
    )
    abbreviated_title = UpperCaseCharField(
        max_length=40,
        label=_("Acronym/Short title"),
        required=False
    )
    common_title_fr = forms.CharField(max_length=240, label=_("Common title in French"), required=True)
    specific_title_fr = forms.CharField(max_length=240, label=_("Specific title in French"), required=True)
    common_title_en = forms.CharField(max_length=240, label=_("Common title in English"), required=False)
    specific_title_en = forms.CharField(max_length=240, label=_("Specific title in English"), required=False)
    credits = fields.CreditField(required=False)
    internship_subtype = forms.ChoiceField(
        choices=BLANK_CHOICE + list(InternshipSubtype.choices()),
        label=_("Internship subtype"),
        required=False,
    )
    responsible_entity = forms.CharField(required=True)  # FIXME
    periodicity = forms.ChoiceField(
        choices=BLANK_CHOICE + list(PeriodicityEnum.choices()),
        label=_("Periodicity"),
        required=True,
    )
    language = forms.ModelChoiceField(
        queryset=Language.objects.all().order_by('name'),  # FIXME
        label=_('Primary language'),
        to_field_name="name",
        initial=FR_CODE_LANGUAGE
    )
    remark_faculty = OsisRichTextFormField(
        config_name='link_only',
        label=_("Remark faculty"),
        required=False
    )
    remark_publication_fr = OsisRichTextFormField(
        config_name='link_only',
        label=_("Remark for publication (fr)"),
        required=False,
    )
    remark_publication_en = OsisRichTextFormField(
        config_name='link_only',
        label=_("remark for publication (en)"),
        required=False,
    )

    def __init__(self, *args, user: User, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        self.__init_requirement_entity_field()

    def __init_requirement_entity_field(self):
        self.fields['responsible_entity'] = fields.ManagementEntitiesModelChoiceField(
            person=self.user.person,
            initial=self.initial.get('responsible_entity'),
            disabled=self.fields['responsible_entity'].disabled,
            required=False
        )  # FIXME

    def clean_academic_year(self):
        if self.cleaned_data['academic_year']:
            return self.cleaned_data['academic_year'].year
        return None

    def clean_language(self):
        if self.cleaned_data['language']:
            return self.cleaned_data['language'].code
        return None

    # def clean_responsible_entity(self):
    #     if self.cleaned_data['responsible_entity']:
    #         return self.cleaned_data['responsible_entity'].acronym
    #     return None

    def get_command(self) -> CommandRequest:
        return CreateLearningUnitCommand(
            code=self.cleaned_data['code'],
            academic_year=self.cleaned_data['academic_year'],
            type=self.cleaned_data['type'],
            common_title_fr=self.cleaned_data['common_title_fr'],
            specific_title_fr=self.cleaned_data['specific_title_fr'],
            common_title_en=self.cleaned_data['common_title_en'],
            specific_title_en=self.cleaned_data['specific_title_en'],
            credits=self.cleaned_data['credits'],
            internship_subtype=self.cleaned_data['internship_subtype'],
            responsible_entity_code=self.cleaned_data['responsible_entity'],
            periodicity=self.cleaned_data['periodicity'],
            iso_code=self.cleaned_data['language'],
            remark_faculty=self.cleaned_data['remark_faculty'],
            remark_publication_fr=self.cleaned_data['remark_publication_fr'],
            remark_publication_en=self.cleaned_data['remark_publication_en'],
        )
