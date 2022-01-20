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
import itertools
from typing import Set

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
from django.db.models import Sum, Prefetch
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

from attribution.business import attribution_charge_new
from attribution.models.attribution_charge_new import AttributionChargeNew
from attribution.models.enums.function import Functions
from base.models.enums import learning_unit_year_subtypes
from base.models.learning_container_year import LearningContainerYear
from base.models.learning_unit_year import LearningUnitYear
from base.models.person import Person
from base.views.common import display_warning_messages
from base.views.learning_units.common import get_common_context_for_learning_unit_year
from osis_role.contrib.views import PermissionRequiredMixin


class LearningUnitAttributions(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = "attribution/attributions.html"
    permission_required = "base.can_access_learningunit"
    raise_exception = True

    @cached_property
    def learning_unit_year(self):
        query_set = LearningUnitYear.objects.all().select_related(
            'learning_unit',
            'learning_container_year'
        ).prefetch_related(
            Prefetch(
                'learning_unit__learningunityear_set',
                queryset=LearningUnitYear.objects.select_related('academic_year')
            )
        )
        if self.learning_unit_year_id:
            return get_object_or_404(query_set, pk=self.learning_unit_year_id)
        return query_set.get(acronym=self.code, academic_year__year=self.year)

    @cached_property
    def person(self):
        return self.request.user.person

    @property
    def learning_unit_year_id(self):
        return self.kwargs.get('learning_unit_year_id')

    @property
    def code(self):
        return self.kwargs.get('code')

    @property
    def year(self):
        return self.kwargs.get('year')

    def get_context_permissions(self):
        return {
            "can_add_charge_repartition": self.request.user.has_perm(
                'base.can_add_charge_repartition',
                self.learning_unit_year
            ),
            "can_change_attribution": self.request.user.has_perm(
                'base.can_change_attribution',
                self.learning_unit_year
            ),
            "can_delete_attribution": self.request.user.has_perm(
                'base.can_delete_attribution',
                self.learning_unit_year
            ),
        }

    def get_context_data(self, **kwargs):
        warning_msgs = get_charge_repartition_warning_messages(self.learning_unit_year.learning_container_year)
        warning_msgs.extend(_get_classes_charge_repartition_warning_messages(self.learning_unit_year))
        display_warning_messages(self.request, warning_msgs)
        return {
            **super().get_context_data(**kwargs),
            **get_common_context_for_learning_unit_year(self.person, self.learning_unit_year),
            **self.get_context_permissions(),
            'attributions': attribution_charge_new.find_attributions_with_charges(self.learning_unit_year.id),
        }


def get_charge_repartition_warning_messages(learning_container_year):
    msgs = []

    charges_by_attribution = _get_charges_by_attribution_and_type_or_func(learning_container_year)

    for attribution_key, charges in charges_by_attribution:
        charges = list(charges)
        full_total_charges = next(
            (
                charge.total_volume for charge in charges
                if charge.learning_component_year.learning_unit_year.subtype == learning_unit_year_subtypes.FULL
            ), 0
        )
        partim_total_charges = next(
            (
                charge.total_volume for charge in charges
                if charge.learning_component_year.learning_unit_year.subtype == learning_unit_year_subtypes.PARTIM
            ), 0
        )

        partim_total_charges = partim_total_charges or 0
        full_total_charges = full_total_charges or 0
        if partim_total_charges > full_total_charges:
            msg = _("The sum of volumes for the partims for professor %(tutor)s is superior to the "
                    "volume of full UE for this professor") % {"tutor": _get_tutor_name_with_function(charges[0])}
            msgs.append(msg)
    return msgs


def _get_classes_charge_repartition_warning_messages(learning_unit_year: LearningUnitYear) -> Set[str]:
    msgs = set()

    charges_by_attribution_and_type = _get_charges_by_attribution_and_type_or_func(
        learning_unit_year.learning_container_year,
        with_classes=True
    )

    msg_warning = _("The sum of volumes for the classes for professor %(tutor)s is superior to the volume of "
                    "UE(%(ue_type)s) for this professor")

    for attribution_key, charges in charges_by_attribution_and_type:
        for charge in list(charges):
            if _get_component_volume_total_of_classes(charge) > (charge.total_volume or 0):
                msgs.add(msg_warning % {
                    "tutor": _get_tutor_name_with_function(charge),
                    "ue_type": learning_unit_year.get_subtype_display().lower()
                })

    return msgs


def _get_charges_by_attribution_and_type_or_func(learning_container_year: LearningContainerYear, with_classes=False):
    total_charges = AttributionChargeNew.objects.filter(
        attribution__learning_container_year=learning_container_year,
    ).annotate(total_volume=Sum("allocation_charge"))

    if with_classes:
        total_charges = total_charges.prefetch_related(
            models.Prefetch('learning_component_year__learningclassyear_set', to_attr="classes")
        )

    charges_by_attribution_and_type_or_func = itertools.groupby(
        total_charges, lambda rec: "{}_{}_{}".format(
            rec.attribution.tutor,
            rec.attribution.start_year,
            rec.learning_component_year.type if with_classes else rec.attribution.function
        )
    )

    return charges_by_attribution_and_type_or_func


def _get_component_volume_total_of_classes(charge: AttributionChargeNew) -> float:
    return sum([
        class_attrib.allocation_charge
        for class_attrib in charge.attributionclass_set.all()
        if class_attrib.allocation_charge
    ])


def _get_tutor_name_with_function(charge: AttributionChargeNew) -> str:
    tutor_name = Person.get_str(charge.attribution.tutor.person.first_name, charge.attribution.tutor.person.last_name)
    return "{} ({})".format(tutor_name, getattr(Functions, charge.attribution.function).value)
