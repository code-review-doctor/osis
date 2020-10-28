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
import html

import bleach
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db.models import Prefetch, Case, When, Value, IntegerField, Subquery, CharField, Q
from django.db.models.expressions import F
from django.db.models.functions import Cast, Concat, Upper
from django.utils.translation import gettext_lazy as _
from openpyxl.styles import Alignment, Style
from openpyxl.utils import get_column_letter
from reversion.models import Version

from backoffice.settings.base import LANGUAGE_CODE_FR, LANGUAGE_CODE_EN
from base.business.learning_unit import CMS_LABEL_PEDAGOGY_FR_ONLY, \
    CMS_LABEL_PEDAGOGY, CMS_LABEL_PEDAGOGY_FR_AND_EN, CMS_LABEL_PEDAGOGY_FORCE_MAJEURE
from base.business.learning_unit import CMS_LABEL_SPECIFICATIONS, get_achievements_group_by_language
from base.business.learning_unit_xls import annotate_qs
from base.business.xls import get_name_or_username
from base.models.person import get_user_interface_language
from base.models.teaching_material import TeachingMaterial
from base.views.learning_unit import get_specifications_context
from cms.enums.entity_name import LEARNING_UNIT_YEAR
from cms.models.text_label import TextLabel
from cms.models.translated_text import TranslatedText
from cms.models.translated_text_label import TranslatedTextLabel
from osis_common.document import xls_build

XLS_DESCRIPTION = _('Learning units list')
XLS_FILENAME = _('LearningUnitsList')
WORKSHEET_TITLE = _('Learning units list')
WRAP_TEXT_STYLE = Style(alignment=Alignment(wrapText=True, vertical="top"), )
CMS_ALLOWED_TAGS = []

RAW_SQL_TO_GET_LAST_UPDATE_FICHE_DESCRIPTIVE = """
    WITH last_update_info AS (
        SELECT upper(person.last_name) || ' ' || person.first_name as author, revision.date_created AS last_update
        FROM reversion_version version
        JOIN reversion_revision revision ON version.revision_id = revision.id
        JOIN auth_user users ON revision.user_id = users.id
        JOIN base_person person ON person.user_id = users.id
        join django_content_type ct on version.content_type_id = ct.id
        left join cms_translatedtext tt on cast(version.object_id as integer) = tt.id and ct.model = 'translatedtext'
        left join cms_textlabel tl on tt.text_label_id = tl.id
        left join base_teachingmaterial tm on cast(version.object_id as integer) = tm.id and ct.model = 'teachingmaterial'
        join base_learningunityear luy on luy.id = tm.learning_unit_year_id or luy.id = tt.reference
        where "base_groupelementyear"."child_leaf_id" = luy.id
        and tl.label in {labels_to_check} and ct.model in ({models_to_check})
        order by revision.date_created desc limit 1
    )
"""

LAST_UPDATE_FORCE_MAJEURE = RAW_SQL_TO_GET_LAST_UPDATE_FICHE_DESCRIPTIVE.format(
    labels_to_check=repr(tuple(map(str, CMS_LABEL_PEDAGOGY_FORCE_MAJEURE))),
    models_to_check=','.join(["'translatedtext'"])
) + """
SELECT {field_to_select} FROM last_update_info
"""


def create_xls_educational_information_and_specifications(user, learning_units, request):
    titles = _get_titles()

    working_sheet_data = prepare_xls_educational_information_and_specifications(learning_units, request)

    parameters = {xls_build.DESCRIPTION: XLS_DESCRIPTION,
                  xls_build.USER: get_name_or_username(user),
                  xls_build.FILENAME: XLS_FILENAME,
                  xls_build.HEADER_TITLES: titles,
                  xls_build.WS_TITLE: WORKSHEET_TITLE,
                  xls_build.ROW_HEIGHT: {'height': 30,
                                         'start': 2,
                                         'stop': (len(learning_units)) + 1
                                         },
                  xls_build.STYLED_CELLS: {
                      WRAP_TEXT_STYLE: _get_wrapped_cells_educational_information_and_specifications(
                          learning_units, len(titles)
                      )
                  }
                  }

    return xls_build.generate_xls(xls_build.prepare_xls_parameters_list(working_sheet_data, parameters))


def _get_titles():
    titles = [
        str(_('Code')),
        str(_('Title')),
        str(_('Req. Entity')),
    ]
    titles = titles + _add_cms_title_fr_en(CMS_LABEL_PEDAGOGY_FR_AND_EN, True)
    titles = titles + [str(_('Teaching material'))]
    titles = titles + _add_cms_title_fr_en(CMS_LABEL_PEDAGOGY_FR_ONLY, False)
    titles = titles + [str("{}".format(_('Last update description fiche by'))),
                       str("{}".format(_('Last update description fiche on')))]
    titles = titles + _add_cms_title_fr_en(CMS_LABEL_PEDAGOGY_FORCE_MAJEURE, True)
    titles = titles + [str("{}".format(_('Last update description fiche (force majeure) by'))),
                       str("{}".format(_('Last update description fiche (force majeure) on')))]
    titles = titles + _add_cms_title_fr_en(CMS_LABEL_SPECIFICATIONS, True)
    titles = titles + [str("{} - {}".format(_('Learning achievements'), LANGUAGE_CODE_FR.upper())),
                       str("{} - {}".format('Learning achievements', LANGUAGE_CODE_EN.upper()))]
    return titles


def _add_cms_title_fr_en(cms_labels, with_en=True):
    titles = []
    for label_key in cms_labels:
        a_text_label = TextLabel.objects.filter(label=label_key).first()
        titles.append(_add_text_label(a_text_label, LANGUAGE_CODE_FR))
        if with_en:
            titles.append(_add_text_label(a_text_label, LANGUAGE_CODE_EN))
    return titles


def get_html_to_text(text_to_convert):
    text_to_convert = text_to_convert or ''
    return bleach.clean(html.unescape(text_to_convert),
                        strip=True, tags=CMS_ALLOWED_TAGS).lstrip()


def prepare_xls_educational_information_and_specifications(learning_unit_years, request):
    qs = annotate_qs(learning_unit_years)
    user_language = get_user_interface_language(request.user)

    result = []

    for learning_unit_yr in qs:
        translated_labels_with_text = _get_translated_labels_with_text(
            learning_unit_yr.id,
            user_language,
            CMS_LABEL_PEDAGOGY
        )
        teaching_materials = TeachingMaterial.objects.filter(learning_unit_year=learning_unit_yr).order_by('order')

        line = [
            learning_unit_yr.acronym,
            learning_unit_yr.complete_title,
            learning_unit_yr.entity_requirement,
        ]

        for label_key in CMS_LABEL_PEDAGOGY_FR_AND_EN:
            _add_pedagogies_forces_major(label_key, line, translated_labels_with_text)

        if teaching_materials:
            line.append("\n".join(
                [get_html_to_text(teaching_material.title) for teaching_material in
                 teaching_materials]))
        else:
            line.append('')

        for label_key in CMS_LABEL_PEDAGOGY_FR_ONLY:
            translated_label = translated_labels_with_text.filter(text_label__label=label_key).first()

            if translated_label:
                line.append(
                    get_html_to_text(translated_label.text_label.text_fr[0].text)
                    if translated_label.text_label.text_fr and translated_label.text_label.text_fr[0].text else ''
                )

            else:
                line.append('')

        _add_revision_informations(learning_unit_yr, line, CMS_LABEL_PEDAGOGY)

        translated_labels_force_majeure_with_text = _get_translated_labels_with_text(
            learning_unit_yr.id,
            user_language,
            CMS_LABEL_PEDAGOGY_FORCE_MAJEURE
        )
        for label_key in CMS_LABEL_PEDAGOGY_FORCE_MAJEURE:
            _add_pedagogies_forces_major(label_key, line, translated_labels_force_majeure_with_text)

        _add_revision_informations(learning_unit_yr, line, CMS_LABEL_PEDAGOGY_FORCE_MAJEURE)

        _add_specifications(learning_unit_yr, line, request)

        line.extend(_add_achievements(learning_unit_yr))

        result.append(line)

    return result


def _add_revision_informations(learning_unit_yr, line, cms_label):
    translated_texts = TranslatedText.objects.filter(
        reference=learning_unit_yr.id,
        entity=LEARNING_UNIT_YEAR,
        text_label__label__in=cms_label
    )
    ids = [translated_text.id for translated_text in translated_texts]
    version = Version.objects.filter(
        content_type=ContentType.objects.get_for_model(TranslatedText),
        object_id__in=ids
    ).select_related(
        "revision",
        "revision__user__person"
    ).annotate(
        author=Concat(
            Upper(F('revision__user__person__last_name')), Value(' '), F('revision__user__person__first_name'),
            output_field=CharField()
        )
    ).order_by("-revision__date_created")
    if version:
        line.append(version.values('author')[:1][0]["author"])
        line.append(version.values('revision__date_created')[:1][0]["revision__date_created"].date())


def _add_pedagogies_forces_major(label_key, line, translated_labels_force_majeure_with_text):
    translated_label = translated_labels_force_majeure_with_text.filter(text_label__label=label_key).first()
    if translated_label:
        line.append(
            get_html_to_text(translated_label.text_label.text_fr[0].text)
            if translated_label.text_label.text_fr and translated_label.text_label.text_fr[0].text else ''
        )
        line.append(
            get_html_to_text(translated_label.text_label.text_en[0].text)
            if translated_label.text_label.text_en and translated_label.text_label.text_en[0].text else '')
    else:
        line.append('')
        line.append('')


def _add_achievements(learning_unit_yr):
    achievements = get_achievements_group_by_language(learning_unit_yr)
    achievements_fr = (achievements.get('achievements_FR', None))
    achievements_en = (achievements.get('achievements_EN', None))
    return ["\n".join([get_html_to_text(achievement.text) for achievement in
                       achievements_fr]) if achievements_fr else '',
            "\n".join([get_html_to_text(achievement.text) for achievement in
                       achievements_en]) if achievements_en else ''
            ]


def _add_specifications(learning_unit_yr, line, request):
    specifications = get_specifications_context(learning_unit_yr, request)
    obj_fr = specifications.get('form_french')
    obj_en = specifications.get('form_english')
    for label_key in CMS_LABEL_SPECIFICATIONS:
        line.append(get_html_to_text(getattr(obj_fr, label_key, '')))
        line.append(get_html_to_text(getattr(obj_en, label_key, '')))


def _get_translated_labels_with_text(learning_unit_year_id, user_language, cms_labels):
    translated_labels_with_text = TranslatedTextLabel.objects.filter(
        language=user_language,
        text_label__label__in=cms_labels
    ).prefetch_related(
        Prefetch(
            "text_label__translatedtext_set",
            queryset=TranslatedText.objects.filter(
                language=settings.LANGUAGE_CODE_FR,
                entity=LEARNING_UNIT_YEAR,
                reference=learning_unit_year_id
            ),
            to_attr="text_fr"
        ),
        Prefetch(
            "text_label__translatedtext_set",
            queryset=TranslatedText.objects.filter(
                language=settings.LANGUAGE_CODE_EN,
                entity=LEARNING_UNIT_YEAR,
                reference=learning_unit_year_id
            ),
            to_attr="text_en"
        )
    ).annotate(
        label_ordering=Case(
            *[When(text_label__label=label, then=Value(i)) for i, label in enumerate(cms_labels)],
            default=Value(len(cms_labels)),
            output_field=IntegerField()
        )
    ).select_related(
        "text_label"
    ).order_by(
        "label_ordering"
    )
    return translated_labels_with_text


def _get_wrapped_cells_educational_information_and_specifications(learning_units, nb_col):
    dict_wrapped_styled_cells = []

    for idx, luy in enumerate(learning_units, start=2):
        column_number = 1
        while column_number <= nb_col:
            dict_wrapped_styled_cells.append("{}{}".format(get_column_letter(column_number), idx))
            column_number += 1
    return dict_wrapped_styled_cells


def _add_text_label(a_text_label, language_code):
    a_label = TranslatedTextLabel.objects.filter(text_label=a_text_label, language=language_code).first()
    return "{} - {}".format(a_label if a_label else '', language_code.upper())
