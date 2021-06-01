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
from typing import List

from django.contrib.auth.decorators import login_required, permission_required
from django.db import models
from django.db.models import Sum
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from attribution.business import attribution_json, attribution_charge_new
from attribution.models.attribution_charge_new import AttributionChargeNew
from attribution.models.enums.function import Functions
from base.models.enums import learning_unit_year_subtypes
from base.models.learning_component_year import LearningComponentYear
from base.models.learning_unit_year import LearningUnitYear
from base.models.person import Person
from base.views.common import display_warning_messages
from base.views.learning_units.common import get_common_context_learning_unit_year


class RecomputePortalSerializer(serializers.Serializer):
    global_ids = serializers.ListField(child=serializers.CharField(), required=False)


@api_view(['POST'])
def recompute_portal(request):
    serializer = RecomputePortalSerializer(data=request.data)
    if serializer.is_valid():
        global_ids = serializer.data['global_ids'] if serializer.data['global_ids'] else None
        result = attribution_json.publish_to_portal(global_ids)
        if result:
            return Response(status=status.HTTP_202_ACCEPTED)
    return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@login_required
@permission_required('base.can_access_learningunit', raise_exception=True)
def learning_unit_attributions(request, learning_unit_year_id=None, code=None, year=None):
    context = get_common_context_learning_unit_year(request.user.person, learning_unit_year_id, code, year)
    luy = context["learning_unit_year"]
    context['attributions'] = attribution_charge_new.find_attributions_with_charges(luy.id)
    context["can_add_charge_repartition"] = request.user.has_perm('base.can_add_charge_repartition', luy)
    context["can_change_attribution"] = request.user.has_perm('base.can_change_attribution', luy)
    context["can_delete_attribution"] = request.user.has_perm('base.can_delete_attribution', luy)
    context["tab_active"] = "learning_unit_attributions"  # Corresponds to url_name
    warning_msgs = get_charge_repartition_warning_messages(context["learning_unit_year"].learning_container_year)
    warning_msgs.extend(_get_classes_charge_repartition_warning_messages(context["learning_unit_year"]))
    display_warning_messages(request, warning_msgs)
    return render(request, "attribution/attributions.html", context)


def get_charge_repartition_warning_messages(learning_container_year):
    total_charges_by_attribution_and_learning_subtype = AttributionChargeNew.objects \
        .filter(attribution__learning_container_year=learning_container_year) \
        .order_by("attribution__tutor", "attribution__function", "attribution__start_year") \
        .values("attribution__tutor", "attribution__tutor__person__first_name",
                "attribution__tutor__person__middle_name", "attribution__tutor__person__last_name",
                "attribution__function", "attribution__start_year",
                "learning_component_year__learning_unit_year__subtype") \
        .annotate(total_volume=Sum("allocation_charge"))

    charges_by_attribution = itertools.groupby(total_charges_by_attribution_and_learning_subtype,
                                               lambda rec: "{}_{}_{}".format(rec["attribution__tutor"],
                                                                             rec["attribution__start_year"],
                                                                             rec["attribution__function"]))
    msgs = []
    for attribution_key, charges in charges_by_attribution:
        charges = list(charges)
        subtype_key = "learning_component_year__learning_unit_year__subtype"
        full_total_charges = next(
            (charge["total_volume"] for charge in charges if charge[subtype_key] == learning_unit_year_subtypes.FULL),
            0)
        partim_total_charges = next(
            (charge["total_volume"] for charge in charges if charge[subtype_key] == learning_unit_year_subtypes.PARTIM),
            0)
        partim_total_charges = partim_total_charges or 0
        full_total_charges = full_total_charges or 0
        if partim_total_charges > full_total_charges:
            msg = _("The sum of volumes for the partims for professor %(tutor)s is superior to the "
                    "volume of full UE for this professor") % {"tutor": _get_tutor_name_with_function(charges[0])}
            msgs.append(msg)
    return msgs


def _get_classes_charge_repartition_warning_messages(learning_unit_year: LearningUnitYear) -> List[str]:
    msgs = []
    total_charges_by_attribution_and_learning_subtype = AttributionChargeNew.objects \
        .filter(attribution__learning_container_year=learning_unit_year.learning_container_year) \
        .order_by(
            "learning_component_year__type",
            "attribution__tutor",
            "attribution__function",
            "attribution__start_year"
        ) \
        .values("attribution__tutor", "attribution__tutor__person__first_name",
                "attribution__tutor__person__middle_name", "attribution__tutor__person__last_name",
                "attribution__function", "attribution__start_year",
                "learning_component_year__type", "learning_component_year__pk") \
        .annotate(total_volume=Sum("allocation_charge"))

    charges_by_attribution_and_type = itertools.groupby(
        total_charges_by_attribution_and_learning_subtype,
        lambda rec: "{}_{}_{}".format(rec["attribution__tutor"],
                                      rec["attribution__start_year"],
                                      rec["learning_component_year__type"]
                                      )
    )

    components_queryset = LearningComponentYear.objects.filter(
        learning_unit_year__learning_container_year=learning_unit_year.learning_container_year
    )
    all_components = components_queryset.order_by('acronym') \
        .select_related('learning_unit_year') \
        .prefetch_related(models.Prefetch('learningclassyear_set', to_attr="classes"))
    msg_warning = _("The sum of volumes for the classes for professor %(tutor)s is superior to the volume of "
                    "UE(%(ue_type)s) for this professor")
    for component in all_components:
        volume_total_of_classes = _get_component_volume_total_of_classes(component)

        for attribution_key, charges in charges_by_attribution_and_type:
            charges = list(charges)
            for charge in charges:
                if charge['learning_component_year__pk'] == component.pk:
                    if volume_total_of_classes > charge['total_volume']:
                        msgs.append(
                            msg_warning % {
                                "tutor": _get_tutor_name_with_function(charges[0]),
                                "ue_type": learning_unit_year.get_subtype_display().lower()
                            }
                        )

    return msgs


def _get_component_volume_total_of_classes(component: LearningComponentYear) -> float:
    volume_total_of_classes = 0
    for effective_classes in component.classes:
        volume_total_of_classes += effective_classes.hourly_volume_partial_q1 or 0
        volume_total_of_classes += effective_classes.hourly_volume_partial_q2 or 0
    return volume_total_of_classes


def _get_tutor_name_with_function(charge: dict) -> str:
    tutor_name = Person.get_str(charge["attribution__tutor__person__first_name"],
                                charge["attribution__tutor__person__last_name"])
    return "{} ({})".format(
        tutor_name,
        getattr(Functions, charge["attribution__function"]).value
    )
