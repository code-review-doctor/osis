##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)
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
import re

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from base.forms.utils.acronym_field import AcronymField, PartimAcronymField, split_acronym
from base.forms.utils.choice_field import add_blank
from base.models.campus import find_main_campuses
from base.models.enums import learning_unit_year_subtypes
from base.models.enums.learning_container_year_types import LEARNING_CONTAINER_YEAR_TYPES_FOR_FACULTY, EXTERNAL
from base.models.enums.learning_container_year_types import LEARNING_CONTAINER_YEAR_TYPES_WITHOUT_EXTERNAL, INTERNSHIP
from base.models.enums.learning_unit_external_sites import LearningUnitExternalSite
from base.models.enums.learning_unit_year_subtypes import FULL, PARTIM
from base.models.learning_container import LearningContainer
from base.models.learning_container_year import LearningContainerYear
from base.models.learning_unit import LearningUnit, REGEX_BY_SUBTYPE
from base.models.learning_unit_year import LearningUnitYear, MAXIMUM_CREDITS
from osis_common.forms.widgets import FloatFormatInput
from reference.models.language import find_all_languages

CRUCIAL_YEAR_FOR_CREDITS_VALIDATION = 2018


def _create_learning_container_year_type_list():
    return add_blank(LEARNING_CONTAINER_YEAR_TYPES_WITHOUT_EXTERNAL)


def _create_faculty_learning_container_type_list():
    return add_blank(LEARNING_CONTAINER_YEAR_TYPES_FOR_FACULTY)


class LearningUnitModelForm(forms.ModelForm):

    def save(self, **kwargs):
        self.instance.learning_container = kwargs.pop('learning_container')
        self.instance.start_year = kwargs.pop('start_year')
        return super().save(**kwargs)

    class Meta:
        model = LearningUnit
        fields = ('faculty_remark', 'other_remark')
        widgets = {
            'faculty_remark': forms.Textarea(attrs={'rows': '5'}),
            'other_remark': forms.Textarea(attrs={'rows': '5'})
        }


# TODO Is it really useful ?
class LearningContainerModelForm(forms.ModelForm):
    class Meta:
        model = LearningContainer
        fields = ()


class LearningUnitYearModelForm(forms.ModelForm):

    def __init__(self, data, person, subtype, *args, external=False, **kwargs):
        super().__init__(data, *args, **kwargs)

        self.external = external
        self.instance.subtype = subtype
        self.person = person

        acronym = self.initial.get('acronym')
        if acronym:
            self.initial['acronym'] = split_acronym(acronym, subtype, instance=self.instance)

        if subtype == learning_unit_year_subtypes.PARTIM:
            self.fields['acronym'] = PartimAcronymField()
            self.fields['specific_title'].label = _('Title proper to the partim')
            self.fields['specific_title_english'].label = _('English title proper to the partim')

        # Disabled fields when it's an update
        if self.instance.pk:
            self.fields['academic_year'].disabled = True

            # we cannot edit the internship subtype if the container_type is not internship
            if 'internship_subtype' in self.fields and \
                    self.instance.learning_container_year.container_type != INTERNSHIP:
                self.fields['internship_subtype'].disabled = True

        if not external:
            self.fields['campus'].queryset = find_main_campuses()
        self.fields['language'].queryset = find_all_languages()

    class Meta:
        model = LearningUnitYear
        fields = ('academic_year', 'acronym', 'specific_title', 'specific_title_english', 'credits',
                  'session', 'quadrimester', 'status', 'internship_subtype', 'attribution_procedure',
                  'professional_integration', 'campus', 'language', 'periodicity')
        field_classes = {'acronym': AcronymField}
        error_messages = {
            'credits': {
                # Override unwanted DecimalField standard error messages
                'max_digits': _('Ensure this value is less than or equal to %(limit_value)s.') % {
                    'limit_value': MAXIMUM_CREDITS
                },
                'max_whole_digits': _('Ensure this value is less than or equal to %(limit_value)s.') % {
                    'limit_value': MAXIMUM_CREDITS
                }
            }
        }
        widgets = {
            'credits': FloatFormatInput(render_value=True),
            # 'credits': forms.TextInput(),
        }

    def __clean_acronym_external(self):
        acronym = self.data["acronym_0"] if "acronym_0" in self.data else LearningUnitExternalSite.E.value
        if not self.instance.subtype == PARTIM:
            acronym = acronym + self.data["acronym_1"]
        else:
            acronym = acronym + self.data["acronym_1"] + self.data["acronym_2"]
        acronym = acronym.upper()
        if not re.match(REGEX_BY_SUBTYPE[EXTERNAL], acronym) and self.instance.subtype == FULL:
            raise ValidationError(_('Invalid code'))
        if not re.match(REGEX_BY_SUBTYPE[PARTIM], acronym) and self.instance.subtype == PARTIM:
            raise ValidationError(_('Invalid code'))
        return acronym

    def clean_acronym(self):
        if self.external:
            self.cleaned_data["acronym"] = self.__clean_acronym_external()
        elif not self.external and not re.match(REGEX_BY_SUBTYPE[self.instance.subtype], self.cleaned_data["acronym"]):
            raise ValidationError(_('Invalid code'))
        return self.cleaned_data["acronym"]

    def post_clean(self, container_type):
        if "internship_subtype" in self.fields \
                and container_type != INTERNSHIP \
                and self.instance.internship_subtype:
            self.add_error("internship_subtype", _("This field cannot be set"))

        return not self.errors

    # TODO :: Move assignment to self.instance from save into __init__
    # TODO :: Make these kwarg to args (learning_container_year, learning_unit, ... are required args)
    def save(self, **kwargs):
        self.instance.learning_container_year = kwargs.pop('learning_container_year')
        self.instance.academic_year = self.instance.learning_container_year.academic_year
        self.instance.learning_unit = kwargs.pop('learning_unit')
        instance = super().save(**kwargs)
        return instance

    def clean_credits(self):
        credits_ = self.cleaned_data['credits']
        if self.instance.id is None or self.instance.academic_year.year >= CRUCIAL_YEAR_FOR_CREDITS_VALIDATION:
            if not float(credits_).is_integer():
                raise ValidationError(_('The credits value should be an integer'))
        return credits_


class LearningUnitYearPartimModelForm(LearningUnitYearModelForm):
    class Meta(LearningUnitYearModelForm.Meta):
        labels = {
            'specific_title': _('Title proper to the partim'),
            'specific_title_english': _('English title proper to the partim')
        }
        field_classes = {
            'acronym': PartimAcronymField
        }


class LearningContainerYearModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.person = kwargs.pop('person')
        self.proposal = kwargs.pop('proposal', False)
        self.is_create_form = kwargs['instance'] is None
        super().__init__(*args, **kwargs)
        self.prepare_fields()

    def prepare_fields(self):
        self.fields['container_type'].widget.attrs = {'onchange': 'showInternshipSubtype()'}

        # Limit types for faculty_manager only if simple creation of learning_unit
        if self.person.is_faculty_manager and not self.proposal and self.is_create_form:
            self.fields["container_type"].choices = _create_faculty_learning_container_type_list()
        else:
            self.fields["container_type"].choices = _create_learning_container_year_type_list()

    def save(self, **kwargs):
        self.instance.learning_container = kwargs.pop('learning_container')
        self.instance.acronym = kwargs.pop('acronym')
        self.instance.academic_year = kwargs.pop('academic_year')
        return super().save(**kwargs)

    class Meta:
        model = LearningContainerYear
        fields = ('container_type', 'common_title', 'common_title_english',
                  'type_declaration_vacant', 'team', 'is_vacant')

    def post_clean(self, specific_title):
        if not self.instance.common_title and not specific_title:
            self.add_error("common_title", _("You must either set the common title or the specific title"))

        return not self.errors
