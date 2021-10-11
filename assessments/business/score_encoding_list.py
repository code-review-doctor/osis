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
import unicodedata


def sort_encodings(exam_enrollments):
    """
    Sort the list by
     0. LearningUnitYear.acronym
     1. EducationGroupYear.acronym
     2. student.lastname
     3. sutdent.firstname
    :param exam_enrollments: List of examEnrollments to sort
    :return:
    """

    def _sort(key):
        learn_unit_acronym = key.learning_unit_enrollment.learning_unit_year.acronym
        off_enroll = key.learning_unit_enrollment.offer_enrollment
        acronym = off_enroll.education_group_year.acronym
        last_name = off_enroll.student.person.last_name
        first_name = off_enroll.student.person.first_name
        last_name = _normalize_string(last_name) if last_name else None
        first_name = _normalize_string(first_name) if first_name else None
        return "%s %s %s %s" % (learn_unit_acronym if learn_unit_acronym else '',
                                acronym if acronym else '',
                                last_name.upper() if last_name else '',
                                first_name.upper() if first_name else '')

    return sorted(exam_enrollments, key=lambda k: _sort(k))


def _normalize_string(string):
    """
    Remove accents in the string passed in parameter.
    For example : 'é - è' ==> 'e - e'  //  'àç' ==> 'ac'
    :param string: The string to normalize.
    :return: The normalized string
    """
    string = string.replace(" ", "")
    return ''.join((c for c in unicodedata.normalize('NFD', string) if unicodedata.category(c) != 'Mn'))
