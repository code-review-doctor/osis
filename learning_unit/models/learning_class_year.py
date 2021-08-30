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
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from reversion.admin import VersionAdmin

from base.ddd.utils.business_validator import MultipleBusinessExceptions
from base.models.enums.component_type import LECTURING
from base.models.enums import quadrimesters, learning_unit_year_session
from ddd.logic.learning_unit.commands import GetEffectiveClassCommand
from learning_unit.business.create_class_copy_report import create_class_copy_report
from osis_common.models import osis_model_admin
from base.models.enums.learning_component_year_type import  PRACTICAL_EXERCISES


def copy_to_next_year(modeladmin, request, queryset):
    from ddd.logic.learning_unit.commands import CreateEffectiveClassCommand
    from infrastructure.messages_bus import message_bus_instance
    qs = queryset.select_related("learning_component_year")

    report = []
    for obj in qs:
        classe_source = "{}{}{} — {}".format(
            obj.learning_component_year.learning_unit_year.acronym,
            '_' if obj.learning_component_year.type == PRACTICAL_EXERCISES else '-',
            obj.acronym,
            obj.learning_component_year.learning_unit_year.academic_year
        )
        classe_result = ''
        copy_exception = ''

        cmd = CreateEffectiveClassCommand(
            class_code=obj.acronym,
            learning_unit_code=obj.learning_component_year.learning_unit_year.acronym,
            year=obj.learning_component_year.learning_unit_year.academic_year.year+1,
            title_fr=obj.title_fr,
            title_en=obj.title_en,
            teaching_place_uuid=obj.campus.uuid,
            derogation_quadrimester=obj.quadrimester,
            session_derogation=obj.session,
            volume_first_quadrimester=obj.hourly_volume_partial_q1,
            volume_second_quadrimester=obj.hourly_volume_partial_q2

        )
        try:
            new_classe_identity = message_bus_instance.invoke(cmd)
            cmd_get_effective_class_created = GetEffectiveClassCommand(
                class_code=new_classe_identity.class_code,
                learning_unit_code=new_classe_identity.learning_unit_identity.code,
                learning_unit_year=new_classe_identity.learning_unit_identity.academic_year.year
            )
            effective_class_created = message_bus_instance.invoke(cmd_get_effective_class_created)
            classe_result = "{} — {}".format(
                effective_class_created.complete_acronym,
                effective_class_created.entity_id.learning_unit_identity.academic_year
            )

        except MultipleBusinessExceptions as multiple_exceptions:
            copy_exception = ", ". join([ex.message for ex in list(multiple_exceptions.exceptions)])

        report.append({
            'source': classe_source,
            'result': classe_result,
            'exception': copy_exception})

    return create_class_copy_report(request.user, report)


copy_to_next_year.short_description = _("Copy to next year")


class LearningClassYearAdmin(VersionAdmin, osis_model_admin.OsisModelAdmin):
    list_display = ('learning_component_year', 'year', 'acronym')
    search_fields = ['acronym', 'learning_component_year__learning_unit_year__acronym']

    actions = [copy_to_next_year]


class LearningClassYearManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related(
            'learning_component_year',
            'learning_component_year__learning_unit_year'
        )


ALPHANUMERIC_REGEX = r'^[a-zA-Z0-9]$'
only_alphanumeric_validator = RegexValidator(ALPHANUMERIC_REGEX, _('Only alphanumeric characters are allowed.'))


class LearningClassYear(models.Model):
    external_id = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    changed = models.DateTimeField(null=True, auto_now=True)
    learning_component_year = models.ForeignKey(
        'base.LearningComponentYear',
        on_delete=models.CASCADE
    )
    acronym = models.CharField(max_length=1, validators=[only_alphanumeric_validator])

    title_fr = models.CharField(max_length=255, blank=True, verbose_name=_('Title in French'))
    title_en = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('Title in English'))

    hourly_volume_partial_q1 = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True,
                                                   verbose_name=_("hourly volume partial q1"))
    hourly_volume_partial_q2 = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True,
                                                   verbose_name=_("hourly volume partial q2"))
    quadrimester = models.CharField(max_length=9, blank=True, verbose_name=_('Quadrimester'), null=True,
                                    choices=quadrimesters.DerogationQuadrimester.choices())
    session = models.CharField(max_length=50, blank=True, null=True,
                               choices=learning_unit_year_session.LEARNING_UNIT_YEAR_SESSION,
                               verbose_name=_('Session derogation'))

    campus = models.ForeignKey('base.Campus', verbose_name=_("Learning location"), on_delete=models.PROTECT)

    objects = LearningClassYearManager()

    def __str__(self):
        return u'{}{}-{}'.format(
            self.learning_component_year.learning_unit_year.acronym,
            self.acronym,
            self.learning_component_year.get_type_display()
        )

    @property
    def effective_class_complete_acronym(self):
        return "{}{}{}".format(
            self.learning_component_year.learning_unit_year.acronym,
            '-' if self.learning_component_year.type == LECTURING else '_',
            self.acronym
        )

    @property
    def volume_annual(self):
        volume_total_of_classes = 0
        volume_total_of_classes += self.hourly_volume_partial_q1 or 0
        volume_total_of_classes += self.hourly_volume_partial_q2 or 0
        return volume_total_of_classes

    @property
    def year(self):
        return self.learning_component_year.learning_unit_year.academic_year.year
