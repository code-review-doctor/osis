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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.db.models import Q

from base.models.education_group_year import EducationGroupYear
from base.models.group_element_year import GroupElementYear
from cms.enums import entity_name
from cms.models.translated_text import TranslatedText
from education_group.models.cohort_year import CohortYear
from education_group.models.group_year import GroupYear
from program_management.models.education_group_version import EducationGroupVersion
from program_management.tasks import postpone_programs_until_n_plus_6

FROM_YEAR = 2022


def timeit(f):
    def _func(*args, **kwargs):
        import time
        start = time.time()
        f(*args, **kwargs)
        time_taken = time.time() - start
        print('Took {} seconds for {}'.format(time_taken, f.__name__))
    return _func


@timeit
def delete_datas(from_year: int):
    delete_links(from_year)
    delete_education_group_years(from_year)
    delete_group_years(from_year)


@timeit
def delete_links(from_year: int):
    qs = GroupElementYear.objects.filter(
        Q(parent_element__group_year__academic_year__year__gte=from_year) |
        Q(child_element__group_year__academic_year__year__gte=from_year)
    ).exclude(

    )
    for link in qs:
        link.delete()


@timeit
def delete_group_years(from_year: int):
    qs = GroupYear.objects.filter(
        academic_year__year__gte=from_year
    ).exclude(
        educationgroupversion__isnull=False
    ).select_related(
        "element"
    )
    delete_group_year_cms(qs)
    for group in qs:
        delete_elements(group)
        group.delete()


def delete_elements(gy: 'GroupYear'):
    if hasattr(gy, 'element'):
        gy.element.delete()


def delete_group_year_cms(gy_qs):
    qs = TranslatedText.objects.filter(
        entity=entity_name.GROUP_YEAR,
        reference__in=gy_qs.values_list('id', flat=True)
    ).defer('text')
    qs.delete()


@timeit
def delete_education_group_years(from_year: int):
    egys_to_delete = EducationGroupYear.objects.filter(
        academic_year__year__gte=from_year
    ).prefetch_related(
        'cohortyear_set',
        'educationgroupversion_set',
    ).exclude(
        partnerships__isnull=False
    )

    delete_education_group_year_cms(egys_to_delete)

    for egy in egys_to_delete:
        delete_cohorts(egy)
        delete_version(egy)
        egy.delete()


def delete_education_group_year_cms(egy_qs):
    qs = TranslatedText.objects.filter(
        entity=entity_name.OFFER_YEAR,
        reference__in=egy_qs.values_list('id', flat=True)
    ).defer('text')
    qs.delete()


def delete_cohorts(egy: 'EducationGroupYear'):
    for cohort in egy.cohortyear_set.all():
        cohort.delete()


def delete_version(egy: 'EducationGroupVersion'):
    for version in egy.educationgroupversion_set.all():
        version.delete()


def delete_cohorts_linked_to_11ba():
    qs = CohortYear.objects.filter(
        education_group_year__partial_acronym__contains='11BA'
    )

    for cohort in qs:
        cohort.delete()


def main_delete_datas():
    print('Delete datas')
    delete_datas(FROM_YEAR)


def main_postpone_programs():
    print('Postpone programs until n+6')
    timeit(postpone_programs_until_n_plus_6.run)()

    print('Delete cohorts linked to 11ba')
    timeit(delete_cohorts_linked_to_11ba)()

    print('Postpone coorganizations data')
    for year in range(FROM_YEAR, FROM_YEAR+5):
        timeit(postpone_programs_until_n_plus_6.postpone_coorganizations_data)(year)


def main_postpone_cms():
    print('Copy cms')
    for year in range(FROM_YEAR, FROM_YEAR+5):
        timeit(postpone_programs_until_n_plus_6.postpone_to_n_publication_datas)(year)
