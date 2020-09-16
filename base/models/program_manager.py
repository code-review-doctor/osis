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
import rules
from django.db import models, IntegrityError
from django.db.models import Prefetch
from django.utils.translation import gettext_lazy
from django.utils.translation import gettext_lazy as _
from reversion.admin import VersionAdmin

from base.models.academic_year import current_academic_year
from base.models.education_group import EducationGroup
from base.models.entity import Entity
from base.models.entity_version import find_parent_of_type_into_entity_structure
from base.models.enums.entity_type import FACULTY
from osis_role.contrib import admin as osis_role_admin
from osis_role.contrib import models as osis_role_models
from osis_role.contrib import predicates as osis_role_predicates
from .learning_unit_enrollment import LearningUnitEnrollment
from ..auth.predicates import is_program_manager_for_offer


class ProgramManagerAdmin(VersionAdmin, osis_role_admin.RoleModelAdmin):
    list_display = ('person', 'offer_year', 'changed', 'education_group')
    raw_id_fields = ('person', 'offer_year', 'education_group')
    search_fields = ['person__first_name', 'person__last_name', 'person__global_id', 'offer_year__acronym']
    list_filter = ('offer_year__academic_year',)


class ProgramManager(osis_role_models.RoleModel):
    external_id = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    changed = models.DateTimeField(null=True, auto_now=True)
    person = models.ForeignKey('Person', on_delete=models.PROTECT, verbose_name=gettext_lazy("person"))
    offer_year = models.ForeignKey('OfferYear', on_delete=models.CASCADE)
    education_group = models.ForeignKey(EducationGroup, on_delete=models.CASCADE)
    is_main = models.BooleanField(default=False, verbose_name=gettext_lazy('Main'))

    @property
    def name(self):
        return self.__str__()

    def __str__(self):
        return "{} - {}".format(self.person, self.offer_year)

    class Meta:
        default_related_name = 'role'
        verbose_name = _("Program manager")
        verbose_name_plural = _("Program managers")
        group_name = "program_managers"
        unique_together = ('person', 'offer_year',)

    def save(self, **kwargs):
        if not hasattr(self, "education_group"):
            corresponding_education_group = EducationGroup.objects.filter(
                educationgroupyear__acronym=self.offer_year.acronym
            ).first()
            if not corresponding_education_group:
                raise IntegrityError("The program manager has no education group.")
            self.education_group = corresponding_education_group

        super().save(**kwargs)

    @classmethod
    def rule_set(cls):
        return rules.RuleSet({
            'assessments.can_access_scoreencoding': rules.always_allow,
            'assessments.change_scoresresponsible': rules.always_allow,
            'assessments.view_scoresresponsible': rules.always_allow,
            'base.can_access_catalog': rules.always_allow,
            'base.can_access_evaluation': rules.always_allow,
            'base.can_access_externallearningunityear': rules.always_allow,
            'base.can_access_learningunit': rules.always_allow,
            'base.can_access_offer': rules.always_allow,
            'base.can_access_student_path': rules.always_allow,
            'base.change_group': osis_role_predicates.always_deny(
                message=_("Program managers are not allowed to modify groups")
            ),
            'base.change_educationgroup': is_program_manager_for_offer,
            'base.change_educationgroupcertificateaim': is_program_manager_for_offer,
            'base.is_institution_administrator': rules.always_allow,
            'base.view_educationgroup': rules.always_allow,
        })


def find_by_person(a_person):
    return ProgramManager.objects.filter(person=a_person).select_related(
        'education_group', 'person', 'offer_year'
    )


def is_program_manager(user, offer_year=None, learning_unit_year=None, education_group=None):
    """
    Args:
        user: an instance of auth.User
        offer_year: an annual offer to check whether the user is its program manager.
        learning_unit_year: an annual learning unit to check whether it is in the managed offers of the user.
        education_group: equals to offer_year (will replace it)

    Returns: True if the user manage an offer. False otherwise.
    """
    if user.has_perm('base.is_administrator'):
        return True

    if offer_year:
        return ProgramManager.objects.filter(person__user=user, offer_year=offer_year).exists()
    elif learning_unit_year:
        offers_user = ProgramManager.objects.filter(person__user=user).values('offer_year')
        return LearningUnitEnrollment.objects.filter(learning_unit_year=learning_unit_year) \
            .filter(offer_enrollment__offer_year__in=offers_user).exists()
    elif education_group:
        return ProgramManager.objects.filter(person__user=user, education_group=education_group).exists()
    else:
        return ProgramManager.objects.filter(person__user=user).exists()


def find_by_offer_year(offer_yr):
    return ProgramManager.objects.filter(offer_year=offer_yr) \
        .order_by('person__last_name', 'person__first_name')


def find_by_user(user, academic_year=None):
    queryset = ProgramManager.objects
    if academic_year:
        queryset = queryset.filter(offer_year__academic_year=academic_year)

    return queryset.filter(person__user=user)


def find_by_management_entity(administration_entity, academic_yr):
    if administration_entity and academic_yr:
        return ProgramManager.objects \
            .filter(offer_year__entity_management__in=administration_entity, offer_year__academic_year=academic_yr) \
            .select_related('person') \
            .order_by('person__last_name', 'person__first_name') \
            .distinct('person__last_name', 'person__first_name')

    return None


def get_learning_unit_years_attached_to_program_managers(programs_manager_qs, entity_structure):
    current_ac = current_academic_year()
    allowed_entities_scopes = set()

    offer_enrollments_education_group_year = LearningUnitEnrollment.objects.filter(
        offer_enrollment__education_group_year__academic_year=current_ac,
        offer_enrollment__education_group_year__education_group__in=programs_manager_qs.values_list('education_group',
                                                                                                    flat=True)
    ).distinct('offer_enrollment__education_group_year') \
        .prefetch_related(
        Prefetch(
            'offer_enrollment__education_group_year__administration_entity',
            queryset=Entity.objects.all().prefetch_related('entityversion_set')
        )
    )
    lu_enrollments = LearningUnitEnrollment.objects.filter(
        offer_enrollment__education_group_year__academic_year=current_ac,
        offer_enrollment__education_group_year__education_group__in=programs_manager_qs.values_list('education_group',
                                                                                                    flat=True)
    ).distinct('learning_unit_year') \
        .prefetch_related(
        Prefetch(
            'offer_enrollment__education_group_year__administration_entity',
            queryset=Entity.objects.all().prefetch_related('entityversion_set')
        )
    )

    for offer_enrollment in offer_enrollments_education_group_year:
        education_group_year = offer_enrollment.offer_enrollment.education_group_year
        administration_fac_level = find_parent_of_type_into_entity_structure(
           education_group_year.administration_entity_version,
           entity_structure,
           FACULTY
        )
        if not administration_fac_level:
            administration_fac_level = education_group_year.administration_entity

        allowed_entities_scopes.add(administration_fac_level.pk)
        allowed_entities_scopes = allowed_entities_scopes.union({
            entity_version.entity_id for entity_version in
            entity_structure[administration_fac_level.pk].get('all_children', [])
        })

    return lu_enrollments.filter(
        learning_unit_year__learning_container_year__requirement_entity__in=allowed_entities_scopes)\
        .values_list('learning_unit_year__id', flat=True)
