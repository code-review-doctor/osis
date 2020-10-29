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
from base.models import entity
from base.models import entity_version, offer_year_entity
from base.models.entity_version_address import EntityVersionAddress

SERVICE_COURSE = 'SERVICE_COURSE'


def find_from_offer_year(offer_year):
    return [entity_version.get_last_version(off_year_entity.entity)
            for off_year_entity in offer_year_entity.search(offer_year=offer_year).distinct('entity')]


def find_entity_version_according_academic_year(entity_versions, academic_year):
    """This function can be use after a prefetech_related"""
    return next((entity_vers for entity_vers in entity_versions
                 if entity_vers.start_date <= academic_year.end_date and
                 (entity_vers.end_date is None or entity_vers.end_date > academic_year.end_date)), None)


def update_entity(existing_entity, data):
    fields_to_update = ['website', 'location', 'postal_code', 'city', 'country_id', 'phone', 'fax']
    for f_name in fields_to_update:
        value = data.get(f_name)
        setattr(existing_entity, f_name, value)
    existing_entity.save()


def create_versions_of_existing_entity(entityversion_data, same_entity):
    new_versions_count = 0
    for version in entityversion_data:
        identical_versions_count = entity_version.count_identical_versions(same_entity, version)
        if not identical_versions_count:
            parent = entity.get_by_internal_id(version.pop('parent'))
            addresses_versions = version.pop('entityversionaddress_set')
            entity_v = create_version(version, same_entity, parent)
            if entity_v is None:
                continue
            [create_address_version(address_row, entity_v) for address_row in addresses_versions]
            new_versions_count += 1

    return new_versions_count


def update_end_date_of_existing_versions(entityversion_data, same_entity):
    updated_versions_count = 0
    for version in entityversion_data:
        to_update_versions = entity_version.find_update_candidates_versions(same_entity, version)
        for to_update_version in to_update_versions:
            to_update_version.end_date = version.get('end_date')
            to_update_version.save()
            updated_versions_count += 1

    return updated_versions_count


def create_version(version, same_entity, parent):
    try:
        new_version = entity_version.EntityVersion.objects.create(entity=same_entity, parent=parent, **version)
    except AttributeError:
        new_version = None
    return new_version


def create_address_version(address_version, entity_version):
    try:
        new_address_version = EntityVersionAddress.objects.create(entity_version=entity_version, **address_version)
    except AttributeError:
        new_address_version = None
    return new_address_version
