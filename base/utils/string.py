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
import re

from django.utils import translation
from unidecode import unidecode


SPECIAL_CHARACTERS_PATTERN = r"[-'\s]"
SPECIAL_CHARACTERS_REGEX = re.compile(SPECIAL_CHARACTERS_PATTERN)


def unaccent(s: str) -> str:
    string_without_special_characters = re.sub(SPECIAL_CHARACTERS_REGEX, "", s)
    lower_cased_character = str.lower(string_without_special_characters)
    return unidecode(lower_cased_character)


def is_a_translation_of(translated_string: str, translation_string) -> bool:
    """
    Check whether translated_string is a valid translation of translation_string.
    :param translated_string: a string
    :param translation_string: a proxy string
    :return: true if translated_string is a translation of translation_string
    """
    with translation.override('fr-be'):
        fr_value = str(translation_string)
    with translation.override('en'):
        en_value = str(translation_string)
    return translated_string in (fr_value, en_value)
