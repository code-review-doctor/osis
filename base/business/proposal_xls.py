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
from typing import Dict, List

from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from openpyxl.styles import Font, Color

from base.business.xls import get_name_or_username
from base.models.enums.learning_unit_year_periodicity import PERIODICITY_TYPES
from base.models.learning_unit_year import LearningUnitYearQuerySet
from base.models.proposal_learning_unit import find_by_learning_unit_year
from osis_common.document import xls_build

WORKSHEET_TITLE = _('Proposals')
XLS_FILENAME = _('Proposals')
XLS_DESCRIPTION = _("List proposals")

PROPOSAL_TITLES = [str(_('Req. Entity')), str(_('Code')), str(_('Title')), str(_('Type')),
                   str(_('Proposal type')), str(_('Proposal status')), str(_('Folder num.')),
                   str(_('Decision')), str(_('Periodicity')), str(_('Credits')),
                   str(_('Alloc. Ent.')), str(_('Proposals date'))]

COMPARISON_WORKSHEET_TITLE = _("Proposals comparison")
XLS_COMPARISON_FILENAME = _('Proposals_comparison')
XLS_DESCRIPTION_COMPARISON = _("List of comparison between proposals and UE")
BLANK_VALUE = '-'
BOLD_FONT = Font(bold=True)
BLACK_FONT_STRIKETHROUGH = Font(color=Color('00000000'), strikethrough=True)
REQUIREMENT_ENTITY_COL = 'A'
ALLOCATION_ENTITY_COL = 'K'


def basic_titles_part_1():
    return [
        str(_('Code')),
        str(_('Ac yr.')),
        str(_('Type')),
        str(_('Active')),
        str(_('Subtype')),
        str(_('Internship subtype')),
        str(_('Credits')),
        str(_('Language')),
        str(_('Periodicity')),
        str(_('Quadrimester')),
        str(_('Session derogation')),
        str(_('Title common part')),
        str(_('Title specific complement')),
        str(_('English title common part')),
        str(_('English title specific complement')),
        str(_('Req. Entities')),
        str(_('Alloc. Ent.')),
        str(_('Add. requ. ent. 1')),
        str(_('Add. requ. ent. 2')),
        str(_('Profes. integration')),
        str(_('Institution')),
        str(_('Learning location')),
    ]


def basic_titles_part_2():
    return [
        str(_("Faculty remark (unpublished)")),
        str(_("Other remark (intended for publication)")),
        str(_("Other remark in english (intended for publication)")),
        str(_("Team management")),
        str(_("Vacant")),
        str(_("Decision")),
        str(_("Procedure")),
    ]


def components_titles():
    return [
        "PM {}".format(_('Vol. Q1')),
        "PM {}".format(_('Vol. Q2')),
        "PM {}".format(_('Vol. annual')),
        "PM {}".format(_('Real classes')),
        "PM {}".format(_('Planned classes')),
        "PM {}".format(_('Vol. global')),
        "PM {}".format(_('Req. Entities')),
        "PM {}".format(_('Add. requ. ent. 1')),
        "PM {}".format(_('Add. requ. ent. 2')),
        "PP {}".format(_('Vol. Q1')),
        "PP {}".format(_('Vol. Q2')),
        "PP {}".format(_('Vol. annual')),
        "PP {}".format(_('Real classes')),
        "PP {}".format(_('Planned classes')),
        "PP {}".format(_('Vol. global')),
        "PP {}".format(_('Req. Entities')),
        "PP {}".format(_('Add. requ. ent. 1')),
        "PP {}".format(_('Add. requ. ent. 2'))
    ]


def basic_titles():
    return basic_titles_part_1() + [str(_('Partims'))] + basic_titles_part_2()


COMPARISON_PROPOSAL_TITLES = \
    [''] + \
    basic_titles_part_1() + \
    basic_titles_part_2() + \
    components_titles()


def prepare_xls_content(proposals: List):
    return [extract_xls_data_from_proposal(proposal) for proposal in proposals]


def extract_xls_data_from_proposal(luy):
    proposal = find_by_learning_unit_year(luy)

    return [
        luy.ent_requirement_acronym if luy.ent_requirement_acronym else BLANK_VALUE,
        luy.acronym,
        luy.complete_title,
        luy.learning_container_year.get_container_type_display(),
        proposal.get_type_display(),
        proposal.get_state_display(),
        proposal.folder,
        luy.learning_container_year.get_type_declaration_vacant_display(),
        dict(PERIODICITY_TYPES)[luy.periodicity],
        luy.credits,
        luy.ent_allocation_acronym if luy.ent_allocation_acronym else BLANK_VALUE,
        proposal.date.strftime('%d-%m-%Y')
    ]


def prepare_xls_parameters_list(user, working_sheets_data):
    return {xls_build.LIST_DESCRIPTION_KEY: _(XLS_DESCRIPTION),
            xls_build.FILENAME_KEY: _(XLS_FILENAME),
            xls_build.USER_KEY: get_name_or_username(user),
            xls_build.WORKSHEETS_DATA:
                [{xls_build.CONTENT_KEY: working_sheets_data,
                  xls_build.HEADER_TITLES_KEY: PROPOSAL_TITLES,
                  xls_build.WORKSHEET_TITLE_KEY: _(WORKSHEET_TITLE),
                  }
                 ]}


def create_xls(user, proposals: QuerySet, filters):
    proposals = LearningUnitYearQuerySet.annotate_entities_status(proposals)
    ws_data = xls_build.prepare_xls_parameters_list(
        prepare_xls_content(list(proposals)),
        configure_parameters(user, list(proposals))
    )
    return xls_build.generate_xls(ws_data, filters)


def configure_parameters(user, proposals: List) -> Dict:
    return {
        xls_build.DESCRIPTION: XLS_DESCRIPTION,
        xls_build.USER: get_name_or_username(user),
        xls_build.FILENAME: XLS_FILENAME,
        xls_build.HEADER_TITLES: PROPOSAL_TITLES,
        xls_build.WS_TITLE: WORKSHEET_TITLE,
        xls_build.FONT_CELLS: {
            BLACK_FONT_STRIKETHROUGH: _get_font_for_entities_columns(proposals)
        },
        xls_build.FONT_ROWS: {BOLD_FONT: [0]}
    }


def _get_font_for_entities_columns(proposals: List) -> List[str]:
    cells_strike_with_black_font = []
    for row, learning_unit_yr in enumerate(proposals, start=2):
        if not learning_unit_yr.active_entity_requirement_version:
            cells_strike_with_black_font.append(
                "{}{}".format(REQUIREMENT_ENTITY_COL, row)
            )
        if not learning_unit_yr.active_entity_allocation_version:
            cells_strike_with_black_font.append(
                "{}{}".format(ALLOCATION_ENTITY_COL, row)
            )
    return cells_strike_with_black_font
