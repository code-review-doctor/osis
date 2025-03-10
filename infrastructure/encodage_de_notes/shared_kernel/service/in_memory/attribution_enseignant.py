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

from ddd.logic.encodage_des_notes.shared_kernel.domain.service.i_attribution_enseignant import \
    IAttributionEnseignantTranslator
from ddd.logic.encodage_des_notes.shared_kernel.dtos import EnseignantDTO
from ddd.logic.encodage_des_notes.soumission.dtos import AttributionEnseignantDTO


class AttributionEnseignantTranslatorInMemory(IAttributionEnseignantTranslator):

    attributions_dtos = {
        AttributionEnseignantDTO(
            matricule_fgs_enseignant="00321234",
            code_unite_enseignement="LDROI1001",
            annee=2020,
            nom="Smith",
            prenom="Charles",
        ),
        AttributionEnseignantDTO(
            matricule_fgs_enseignant="12345678",
            code_unite_enseignement="LDROI1001",
            annee=2020,
            nom="Jolypas",
            prenom="Michelle",
        ),
    }  # type: Set[AttributionEnseignantDTO]

    @classmethod
    def search_attributions_enseignant(
            cls,
            code_unite_enseignement: str,
            annee: int,
    ) -> Set['AttributionEnseignantDTO']:
        return set(
            filter(
                lambda dto: dto.code_unite_enseignement == code_unite_enseignement and dto.annee == annee,
                cls.attributions_dtos,
            )
        )

    @classmethod
    def search_attributions_enseignant_par_matricule(
            cls,
            annee: int,
            matricule_enseignant: str,
    ) -> Set['AttributionEnseignantDTO']:
        return set(
            filter(
                lambda dto: dto.matricule_fgs_enseignant == matricule_enseignant,
                cls.attributions_dtos,
            )
        )

    @classmethod
    def search_enseignants_par_nom_prenom_annee(cls, annee: int, nom_prenom: str) -> List['EnseignantDTO']:
        attributions = cls.search_attributions_enseignant_par_nom_prenom_annee(annee, nom_prenom)
        enseignants = {EnseignantDTO(nom=attrib.nom, prenom=attrib.prenom) for attrib in attributions}
        return list(
            sorted(
                enseignants,
                key=lambda ens: ens.nom + ens.prenom
            )
        )

    @classmethod
    def search_attributions_enseignant_par_nom_prenom_annee(
            cls,
            annee: int,
            nom_prenom: str,
    ) -> Set['AttributionEnseignantDTO']:
        return {
            attrib for attrib in cls.attributions_dtos
            if attrib.annee == annee
            and any((mot in attrib.nom or mot in attrib.prenom) for mot in nom_prenom.split(' '))
        }
