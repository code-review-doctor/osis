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
import logging

from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse
from django.shortcuts import render

from base.business.perms import view_academicactors
from base.models import entity_version as entity_version_mdl

logger = logging.getLogger(settings.DEFAULT_LOGGER)


@login_required
@permission_required('base.is_institution_administrator', raise_exception=True)
def institution(request):
    context = {
        'section': 'institution',
        'view_academicactors': view_academicactors(request.user)
    }
    return render(request, "institution.html", context)


@login_required
@permission_required('base.can_access_mandate', raise_exception=True)
def mandates(request):
    return render(request, "mandates.html", {'section': 'mandates'})


@login_required
def academic_actors(request):
    return render(request, "academic_actors.html", {})


@login_required
def get_entity_address(request, entity_version_id):
    version = entity_version_mdl.find_by_id(entity_version_id)
    entity = version.entity
    response = {
        'entity_version_exists_now': version.exists_now(),
        'recipient': '{} - {}'.format(version.acronym, version.title),
        'address': {}
    }
    if entity and entity.has_address():
        response['address'] = {
            'location': entity.location,
            'postal_code': entity.postal_code,
            'city': entity.city,
            'country_id': entity.country_id,
            'phone': entity.phone,
            'fax': entity.fax,
        }
    return JsonResponse(response)


@login_required
def get_entity_address_by_acronym(request, entity_acronym):
    version = entity_version_mdl.EntityVersion.objects.filter(
        acronym=entity_acronym
    ).order_by("start_date").last()
    entity = version.entity
    response = {
        'entity_version_exists_now': version.exists_now(),
        'recipient': '{} - {}'.format(version.acronym, version.title),
        'address': {}
    }
    if entity and entity.has_address():
        response['address'] = {
            'location': entity.location,
            'postal_code': entity.postal_code,
            'city': entity.city,
            'country': entity.country.name,
            'phone': entity.phone,
            'fax': entity.fax,
        }
    return JsonResponse(response)

