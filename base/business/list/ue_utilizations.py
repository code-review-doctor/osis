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
from typing import Dict

from django.db.models import QuerySet
from django.db.models.expressions import RawSQL
from openpyxl.styles import Color, Font

from base.business.learning_unit_xls import WITH_ATTRIBUTIONS, WITH_GRP, HEADER_PROGRAMS, HEADER_TEACHERS, \
    learning_unit_titles_part_1, learning_unit_titles_part2, annotate_qs, get_data_part1, get_data_part2, \
    get_parameters_configurable_list, prepare_proposal_legend_ws_data, title_with_version_title, \
    acronym_with_version_label, BOLD_FONT
from base.business.xls import _get_all_columns_reference
from base.models.learning_unit_year import SQL_RECURSIVE_QUERY_EDUCATION_GROUP_TO_CLOSEST_TRAININGS
from osis_common.document import xls_build

CELLS_WITH_BORDER_TOP = 'cells_with_border_top'

CELLS_WITH_WHITE_FONT = 'cells_with_white_font'

WHITE_FONT = Font(color=Color('00FFFFFF'))


def create_xls_ue_utilizations_with_one_training_per_line(user, learning_units, filters, extra_configuration):
    with_grp = extra_configuration.get(WITH_GRP)
    with_attributions = extra_configuration.get(WITH_ATTRIBUTIONS)
    titles_part1 = learning_unit_titles_part_1()
    titles_part2 = learning_unit_titles_part2()

    if with_grp:
        titles_part2.append(str(HEADER_PROGRAMS))

    if with_attributions:
        titles_part1.append(str(HEADER_TEACHERS))

    data = prepare_xls_content(learning_units, with_grp, with_attributions)
    working_sheets_data = data.get('working_sheets_data')

    titles_part1.extend(titles_part2)
    parameters = _get_parameters(data, learning_units, titles_part1, user)

    ws_data = xls_build.prepare_xls_parameters_list(working_sheets_data,
                                                    parameters)

    ws_data.update(
        {
            xls_build.WORKSHEETS_DATA: [ws_data.get(xls_build.WORKSHEETS_DATA)[0], prepare_proposal_legend_ws_data()]
        }
    )

    return xls_build.generate_xls(ws_data, filters)


def _get_parameters(data: Dict, learning_units, titles_part1, user) -> dict:
    parameters = get_parameters_configurable_list(learning_units, titles_part1, user)
    parameters.update(
        {
            xls_build.FONT_CELLS: {WHITE_FONT: data.get(CELLS_WITH_WHITE_FONT)},
            xls_build.BORDER_CELLS: {xls_build.BORDER_TOP: data.get(CELLS_WITH_BORDER_TOP)},
            xls_build.FONT_ROWS: {BOLD_FONT: [0]}
        }
    )
    return parameters


def prepare_xls_content(learning_unit_years: QuerySet, with_grp=False, with_attributions=False) -> Dict:
    qs = annotate_qs(learning_unit_years)

    if with_grp:
        qs = qs.annotate(
            closest_trainings=RawSQL(SQL_RECURSIVE_QUERY_EDUCATION_GROUP_TO_CLOSEST_TRAININGS, ())
        ).prefetch_related('element')

    lines = []
    cells_with_white_font = []
    cells_with_border_top = []

    for learning_unit_yr in qs:
        lu_data_part1 = get_data_part1(learning_unit_yr)
        lu_data_part2 = get_data_part2(learning_unit_yr, with_attributions)

        if with_grp:
            if hasattr(learning_unit_yr, "element"):
                idx = 0
                for group_element_year in learning_unit_yr.element.children_elements.all():
                    if not learning_unit_yr.closest_trainings or group_element_year.parent_element.group_year is None:
                        break

                    partial_acronym = group_element_year.parent_element.group_year.partial_acronym or ''
                    credits = group_element_year.relative_credits \
                        if group_element_year.relative_credits else group_element_year.child_element.learning_unit_year.credits
                    leaf_credits = "{0:.2f}".format(credits) if credits else '-'
                    nb_parents = '-' if len(learning_unit_yr.closest_trainings) > 0 else ''

                    for training in learning_unit_yr.closest_trainings:
                        if training['gs_origin'] == group_element_year.pk:
                            training_data = _build_training_data(leaf_credits, nb_parents, partial_acronym, training)
                            if training_data:
                                lines.append(lu_data_part1 + lu_data_part2 + [training_data])
                                if idx >= 1:
                                    cells_with_white_font.extend(
                                        ["{}{}".format(letter, len(lines)+1) for letter in _get_all_columns_reference(len(lu_data_part1) + len(lu_data_part2))]
                                    )
                                else:
                                    cells_with_border_top.extend(
                                        ["{}{}".format(letter, len(lines)+1) for letter in _get_all_columns_reference(len(lu_data_part1) + len(lu_data_part2)+1)]
                                    )
                                idx = idx + 1

            else:
                lines.append(lu_data_part1 + lu_data_part2)

        else:
            lu_data_part1.extend(lu_data_part2)
            lines.append(lu_data_part1)

    return {'working_sheets_data': lines,
            CELLS_WITH_WHITE_FONT: cells_with_white_font,
            CELLS_WITH_BORDER_TOP: cells_with_border_top
            }


def _build_training_data(leaf_credits: str, nb_parents: str, partial_acronym: str, training: dict) -> str:
    return "{} ({}) {} {} - {}".format(
        partial_acronym,
        leaf_credits,
        nb_parents,
        acronym_with_version_label(
            training['acronym'], training['transition_name'], training['version_name']
        ),
        title_with_version_title(training['title_fr'], training['version_title_fr']),
    )
