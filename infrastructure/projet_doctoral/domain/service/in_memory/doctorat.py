# ##############################################################################
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
# ##############################################################################

# ##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
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
# ##############################################################################

from ddd.logic.projet_doctoral.domain.model.doctorat import Doctorat
from ddd.logic.projet_doctoral.domain.service.i_doctorat import IDoctoratTranslator
from ddd.logic.projet_doctoral.domain.validator.exceptions import DoctoratNonTrouveException
from ddd.logic.projet_doctoral.test.factory.doctorat import DoctoratCDSCFactory, DoctoratCDEFactory


class DoctoratInMemoryTranslator(IDoctoratTranslator):

    doctorats = [
        DoctoratCDEFactory(
            entity_id__sigle='ECGE3DP',
            entity_id__annee=2020,
        ),
        DoctoratCDSCFactory(
            entity_id__sigle='AGRO3DP',
            entity_id__annee=2020,
        ),
    ]

    @classmethod
    def get(cls, sigle: str, annee: int) -> Doctorat:
        try:
            return next(doc for doc in cls.doctorats if doc.entity_id.sigle == sigle and doc.entity_id.annee == annee)
        except StopIteration:
            raise DoctoratNonTrouveException()
