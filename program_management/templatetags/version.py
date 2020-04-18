##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)
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
from operator import attrgetter

from django import template
from django.shortcuts import reverse
from django.utils.translation import gettext_lazy as _

register = template.Library()

IDENTIFICATION_URL_NAME = 'education_group_read'
CONTENT_URL_NAME = 'education_group_content'
UTILIZATION_URL_NAME = 'education_group_utilization'


@register.simple_tag()
def build_url_identification_tab(a_version):
    return compute_url(IDENTIFICATION_URL_NAME, a_version)


@register.simple_tag()
def build_url_content_tab(a_version):
    return compute_url(CONTENT_URL_NAME, a_version)


@register.simple_tag()
def build_url_utilization_tab(a_version):
    return compute_url(UTILIZATION_URL_NAME, a_version)


def compute_url(basic_url, a_version):
    kwargs = {'education_group_year_id': a_version.offer_id}
    url_name = basic_url
    if a_version.is_transition:
        url_name = '{}_transition'.format(basic_url)

    if a_version.version_name:
        kwargs.update({'version_name': a_version.version_name})

    return reverse(url_name, kwargs=kwargs)


@register.simple_tag(takes_context=True)
def url_dropdown(context, a_version):
    request = context['request']
    return _get_version_url_with_tab_to_show(a_version.version_name,
                                             request.GET.get('tab_to_show'),
                                             a_version.offer_id,
                                             a_version.is_transition)


@register.simple_tag(takes_context=True)
def url_dropdown_academic_year(context, offer_id):
    a_version = context['displayed_version']
    request = context['request']
    return _get_version_url_with_tab_to_show(a_version.version_name,
                                             request.GET.get('tab_to_show'),
                                             offer_id,
                                             a_version.is_transition)


def _get_version_url_with_tab_to_show(version_name, tab_to_show, offer_id, is_transition):
    if tab_to_show == "show_content":
        basic_url = CONTENT_URL_NAME
    elif tab_to_show == 'show_utilization':
        basic_url = UTILIZATION_URL_NAME
    else:
        basic_url = IDENTIFICATION_URL_NAME

    kwargs = {'education_group_year_id': offer_id}
    url_name = basic_url
    if is_transition:
        url_name = '{}_transition'.format(basic_url)

    if version_name:
        kwargs.update({'version_name': version_name})

    return reverse(url_name, kwargs=kwargs)


@register.filter
def version_label(a_version):
    return _('Standard') if a_version.version_name == '' and not a_version.is_transition else a_version.version_label


@register.simple_tag
def ordered_version_list(version_list):
    # List has to be ordered like this
    # Standard version first
    # Transition version second
    # and the particular versions ordered by version_label
    standard_vers = []
    particular_vers = []

    for version in version_list:
        if version.is_standard:
            standard_vers.append(version)
        else:
            particular_vers.append(version)

    return sorted(standard_vers, key=attrgetter("version_label")) + sorted(particular_vers,
                                                                           key=attrgetter("version_label"))
