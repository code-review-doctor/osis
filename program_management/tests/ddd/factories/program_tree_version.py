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
import factory.fuzzy

from program_management.ddd.domain.program_tree import ProgramTreeIdentity
from program_management.ddd.domain.program_tree_version import ProgramTreeVersion, ProgramTreeVersionIdentity
from program_management.tests.ddd.factories.program_tree import ProgramTreeFactory


class ProgramTreeVersionFactory(factory.Factory):

    class Meta:
        model = ProgramTreeVersion
        abstract = False

    tree = factory.SubFactory(ProgramTreeFactory)
    entity_identity = None
    program_tree_identity = ProgramTreeIdentity(code="CODE", year=2020)
    program_tree_repository = None
    entity_id = ProgramTreeVersionIdentity(
        offer_acronym="OFFER",
        year=2020,
        version_name="",
        is_transition=False
    )



