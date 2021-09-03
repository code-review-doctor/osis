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
from typing import Set, List

from base.models.enums.peps_type import PepsTypes
from ddd.logic.encodage_des_notes.shared_kernel.domain.service import \
    ISignaletiqueEtudiantTranslator
from ddd.logic.encodage_des_notes.soumission.dtos import SignaletiqueEtudiantDTO
from ddd.logic.encodage_des_notes.shared_kernel.dtos import EtudiantPepsDTO


class SignaletiqueEtudiantTranslatorInMemory(ISignaletiqueEtudiantTranslator):

    signaletique_dtos = {
        SignaletiqueEtudiantDTO(
            noma='11111111',
            nom="Dupont",
            prenom="Marie",
            peps=EtudiantPepsDTO(
                type_peps=PepsTypes.ARRANGEMENT_JURY.name,
                tiers_temps=True,
                copie_adaptee=True,
                local_specifique=True,
                autre_amenagement=True,
                details_autre_amenagement="Details autre aménagement",
                accompagnateur="Accompagnateur",
            ),
        ),
        SignaletiqueEtudiantDTO(
            noma='99999999',
            nom="Arogan",
            prenom="Adrien",
            peps=EtudiantPepsDTO(
                type_peps=PepsTypes.ARRANGEMENT_JURY.name,
                tiers_temps=False,
                copie_adaptee=False,
                local_specifique=True,
                autre_amenagement=True,
                details_autre_amenagement="Detail",
                accompagnateur="Thomas",
            ),
        ),
    }

    @classmethod
    def search(
            cls,
            nomas: List[str],
            nom: str = None,
            prenom: str = None,
    ) -> Set['SignaletiqueEtudiantDTO']:
        nomas_as_set = set(nomas)
        if not (nomas_as_set or nom or prenom):
            return set()

        result = cls.signaletique_dtos

        if nomas_as_set:
            result = {signaletique for signaletique in result if signaletique.noma in nomas_as_set}
        if nom:
            result = {signaletique for signaletique in result if nom in signaletique.nom}
        if prenom:
            result = {signaletique for signaletique in result if prenom in signaletique.prenom}
        return result
