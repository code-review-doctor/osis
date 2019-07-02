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
#############################################################################
import itertools

from django.core import validators
from django.db import models
from django.utils.functional import lazy
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from reversion.admin import VersionAdmin

from base.models import learning_unit, learning_unit_year
from base.models.enums import prerequisite_operator
from base.models.enums.prerequisite_operator import OR, AND
from osis_common.models.osis_model_admin import OsisModelAdmin

AND_OPERATOR = "ET"
OR_OPERATOR = 'OU'
ACRONYM_REGEX = learning_unit.LEARNING_UNIT_ACRONYM_REGEX_ALL.lstrip('^').rstrip('$')
NO_PREREQUISITE_REGEX = r''
UNIQUE_PREREQUISITE_REGEX = r'{acronym_regex}'.format(acronym_regex=ACRONYM_REGEX)
ELEMENT_REGEX = r'({acronym_regex}|\({acronym_regex}( {secondary_operator} {acronym_regex})+\))'
MULTIPLE_PREREQUISITES_REGEX = '{element_regex}( {main_operator} {element_regex})+'
MULTIPLE_PREREQUISITES_REGEX_OR = MULTIPLE_PREREQUISITES_REGEX.format(
    main_operator=OR_OPERATOR,
    element_regex=ELEMENT_REGEX.format(acronym_regex=ACRONYM_REGEX, secondary_operator=AND_OPERATOR)
)
MULTIPLE_PREREQUISITES_REGEX_AND = MULTIPLE_PREREQUISITES_REGEX.format(
    main_operator=AND_OPERATOR,
    element_regex=ELEMENT_REGEX.format(acronym_regex=ACRONYM_REGEX, secondary_operator=OR_OPERATOR)
)
PREREQUISITE_SYNTAX_REGEX = r'^(?i)({no_element_regex}|' \
                            r'{unique_element_regex}|' \
                            r'{multiple_elements_regex_and}|' \
                            r'{multiple_elements_regex_or})$'.format(
                                no_element_regex=NO_PREREQUISITE_REGEX,
                                unique_element_regex=UNIQUE_PREREQUISITE_REGEX,
                                multiple_elements_regex_and=MULTIPLE_PREREQUISITES_REGEX_AND,
                                multiple_elements_regex_or=MULTIPLE_PREREQUISITES_REGEX_OR
                            )
mark_safe_lazy = lazy(mark_safe, str)
prerequisite_syntax_validator = validators.RegexValidator(regex=PREREQUISITE_SYNTAX_REGEX,
                                                          message=mark_safe_lazy(_("Prerequisites are invalid")))


class PrerequisiteAdmin(VersionAdmin, OsisModelAdmin):
    list_display = ('learning_unit_year', 'education_group_year')
    raw_id_fields = ('learning_unit_year', 'education_group_year')
    list_filter = ('education_group_year__academic_year',)
    search_fields = ['learning_unit_year__acronym', 'education_group_year__acronym',
                     'education_group_year__partial_acronym']
    readonly_fields = ('prerequisite_string',)


class Prerequisite(models.Model):
    external_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        db_index=True
    )
    changed = models.DateTimeField(
        null=True,
        auto_now=True
    )

    learning_unit_year = models.ForeignKey(
        "LearningUnitYear", on_delete=models.CASCADE

    )
    education_group_year = models.ForeignKey(
        "EducationGroupYear", on_delete=models.CASCADE
    )
    main_operator = models.CharField(
        choices=prerequisite_operator.PREREQUISITES_OPERATORS,
        max_length=5,
        default=prerequisite_operator.AND
    )

    class Meta:
        unique_together = ('learning_unit_year', 'education_group_year')

    def __str__(self):
        return "{} / {}".format(self.education_group_year, self.learning_unit_year)

    @property
    def prerequisite_string(self):
        return self._get_acronyms_string(False)

    @property
    def prerequisite_string_as_href(self):
        return self._get_acronyms_string(True)

    def _get_acronyms_string(self, as_href=False):
        main_operator = self.main_operator
        secondary_operator = OR if main_operator == AND else AND
        prerequisite_items = self.prerequisiteitem_set.all().order_by('group_number', 'position')
        prerequisites_fragments = []
        for num_group, records_in_group in itertools.groupby(prerequisite_items, lambda rec: rec.group_number):
            list_records = list(records_in_group)
            predicate_format = "({})" if len(list_records) > 1 else "{}"
            join_secondary_operator = " {} ".format(_(secondary_operator))
            predicate = predicate_format.format(
                join_secondary_operator.join(
                    map(
                        lambda rec: _get_acronym_as_href(rec,
                                                         self.learning_unit_year.academic_year)
                        if as_href else rec.learning_unit.acronym,
                        list_records
                    )
                )
            )
            prerequisites_fragments.append(predicate)
        join_main_operator = " {} ".format(_(main_operator))
        return join_main_operator.join(prerequisites_fragments)


def _get_acronym_as_href(prerequisite_item, academic_yr):
    luy = learning_unit_year.search(
        academic_year_id=academic_yr.id,
        learning_unit=prerequisite_item.learning_unit,
    ).first()

    if luy:
        return "<a href='/learning_units/{}/'>{}</a>".format(luy.id, prerequisite_item.learning_unit.acronym)
    return ''
