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
from typing import Set

from ddd.logic.encodage_des_notes.soumission.domain.service.i_contact_feuille_de_notes import \
    IContactFeuilleDeNotesTranslator
from ddd.logic.encodage_des_notes.soumission.dtos import AdresseFeuilleDeNotesDTO


class ContactFeuilleDeNotesTranslatorInMemory(IContactFeuilleDeNotesTranslator):

    contacts = {
        AdresseFeuilleDeNotesDTO(
            nom_cohorte='DROI1BA',
            destinataire='Faculté de Droit',
            rue_et_numero='Rue de la Fac, 19',
            code_postal='1321',
            ville='Louvain-La-Neuve',
            pays='Belgique',
            telephone='0106601122',
            fax='0106601123',
            email='email-fac-droit@email.be',
        ),
    }

    @classmethod
    def search(
            cls,
            noms_cohortes: Set[str]
    ) -> Set['AdresseFeuilleDeNotesDTO']:
        return set(
            filter(
                lambda dto: _filter(dto, noms_cohortes),
                cls.contacts,
            )
        )


def _filter(dto, cohortes: Set[str]):
    return dto.nom_cohorte in cohortes
