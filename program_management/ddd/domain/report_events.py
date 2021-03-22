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

import attr
from django.utils.translation import gettext_lazy as _

from program_management.ddd.domain.academic_year import AcademicYear
from program_management.ddd.domain.report import ReportEvent


@attr.s(frozen=True, slots=True)
class CopyLearningUnitNotExistForYearEvent(ReportEvent):
    code = attr.ib(type=str)
    copy_year = attr.ib(type=int)
    year = attr.ib(type=int)

    def __str__(self):
        return _("LU %(code)s does not exist in %(copy_year)s. LU is copied with %(year)s as year of reference.") % {
            "code": self.code,
            "copy_year": self.copy_year,
            "year": self.year
        }


@attr.s(frozen=True, slots=True)
class NotCopyTrainingMiniTrainingNotExistForYearEvent(ReportEvent):
    code = attr.ib(type=str)
    acronym = attr.ib(type=str)
    end_year = attr.ib(type=AcademicYear)
    copy_year = attr.ib(type=AcademicYear)

    def __str__(self):
        return _("Training/Mini-Training %(title)s is closed in %(end_year)s. "
                 "This training/mini-training is not copied in %(copy_year)s.") % {
            "title": "{} - {}".format(self.code, self.acronym),
            "copy_year": self.copy_year,
            "end_year": self.end_year
        }


@attr.s(frozen=True, slots=True)
class NotCopyTrainingMiniTrainingNotExistingEvent(ReportEvent):
    title = attr.ib(type=str)
    copy_year = attr.ib(type=int)

    def __str__(self):
        return _("Training/Mini-Training %(title)s is inconsistent."
                 "This training/mini-training is not copied in %(copy_year)s.") % {
                   "title": self.title,
                   "copy_year": self.copy_year,
               }


@attr.s(frozen=True, slots=True)
class CopyReferenceGroupEvent(ReportEvent):
    title = attr.ib(type=str)

    def __str__(self):
        return _("The reference group %(title)s has not yet been copied. Its content is still empty.") % {
            "title": self.title,
        }


@attr.s(frozen=True, slots=True)
class CopyReferenceEmptyEvent(ReportEvent):
    title = attr.ib(type=str)

    def __str__(self):
        return _("The reference element %(title)s is still empty.") % {
            "title": self.title,
        }


@attr.s(frozen=True, slots=True)
class NodeAlreadyCopiedEvent(ReportEvent):
    title = attr.ib(type=str)
    copy_year = attr.ib(type=int)

    def __str__(self):
        return _(
            "The element %(title)s has already been copied in %(copy_year)s in the context of an other training."
            "Its content may have changed."
        ) % {
            "title": self.title,
            "copy_year": self.copy_year
        }


@attr.s(frozen=True, slots=True)
class CannotCopyPrerequisiteAsLearningUnitNotPresent(ReportEvent):
    prerequisite_code = attr.ib(type=str)
    learning_unit_code = attr.ib(type=str)
    training_acronym = attr.ib(type=str)
    copy_year = attr.ib(type=int)

    def __str__(self):
        return _(
            "The prerequisite of %(prerequisite_code)s is not copied in %(copy_year)s: %(learning_unit_code)s "
            "does not exist anymore in %(training_acronym) in %(copy_year)s."
        ) % {
            "prerequisite_code": self.prerequisite_code,
            "learning_unit_code": self.learning_unit_code,
            "copy_year": self.copy_year,
            "training_acronym": self.training_acronym
        }
