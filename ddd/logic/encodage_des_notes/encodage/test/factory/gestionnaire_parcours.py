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
import random

import factory

from ddd.logic.encodage_des_notes.encodage.domain.model.gestionnaire_parcours import GestionnaireParcours, \
    IdentiteGestionnaire


def generate_matricule_fgs() -> str:
    first_digit = str(random.randint(1, 9))
    other_digits = [str(random.randint(0, 9)) for _ in range(8)]
    return "".join([first_digit] + other_digits)


class _IdentiteGestionnaireFactory(factory.Factory):
    class Meta:
        model = IdentiteGestionnaire
        abstract = False

    matricule_fgs_gestionnaire = generate_matricule_fgs()


class _GestionnaireParcoursFactory(factory.Factory):
    class Meta:
        model = GestionnaireParcours
        abstract = False

    entity_id = factory.SubFactory(_IdentiteGestionnaireFactory)
    cohortes_gerees = {}


class GestionnaireParcoursDROI1BAFactory(_GestionnaireParcoursFactory):
    cohortes_gerees = {"DROI1BA"}
