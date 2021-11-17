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
from typing import Optional

import attr

from assessments.models.enums.score_sheet_address_choices import ScoreSheetAddressEntityType
from osis_common.ddd import interface


@attr.s(frozen=True, slots=True)
class IdentiteAdresseFeuilleDeNotes(interface.EntityIdentity):
    nom_cohorte = attr.ib(type=str)
    annee_academique = attr.ib(type=int)


@attr.s(slots=True)
class AdresseFeuilleDeNotes(interface.RootEntity):
    entity_id = attr.ib(type=IdentiteAdresseFeuilleDeNotes)
    type_entite = attr.ib(type=Optional[ScoreSheetAddressEntityType])
    destinataire = attr.ib(type=str)
    rue_numero = attr.ib(type=str)
    code_postal = attr.ib(type=str)
    ville = attr.ib(type=str)
    pays = attr.ib(type=str)
    telephone = attr.ib(type=str)
    fax = attr.ib(type=str)
    email = attr.ib(type=str)

    @property
    def nom_cohorte(self):
        return self.entity_id.nom_cohorte

    @property
    def annee_academique(self):
        return self.entity_id.annee_academique

    def est_identique_a(self, autre_adresse: 'AdresseFeuilleDeNotes') -> bool:
        if self.type_entite:
            return autre_adresse.type_entite and self.destinataire == autre_adresse.destinataire

        return self.type_entite == autre_adresse.type_entite and \
            self.destinataire == autre_adresse.destinataire and \
            self.rue_numero == autre_adresse.rue_numero and \
            self.code_postal == autre_adresse.code_postal and \
            self.ville == autre_adresse.ville and \
            self.pays == autre_adresse.pays and \
            self.telephone == autre_adresse.telephone and \
            self.fax == autre_adresse.fax and \
            self.email == autre_adresse.email
