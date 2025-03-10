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
import abc
from typing import Set, List

from ddd.logic.encodage_des_notes.shared_kernel.dtos import EnseignantDTO
from ddd.logic.encodage_des_notes.soumission.dtos import AttributionEnseignantDTO
from osis_common.ddd import interface


class IAttributionEnseignantTranslator(interface.DomainService):

    @classmethod
    @abc.abstractmethod
    def search_attributions_enseignant(
            cls,
            code_unite_enseignement: str,
            annee: int,
    ) -> Set['AttributionEnseignantDTO']:
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def search_attributions_enseignant_par_nom_prenom_annee(
            cls,
            annee: int,
            nom_prenom: str,
    ) -> Set['AttributionEnseignantDTO']:
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def search_attributions_enseignant_par_matricule(
            cls,
            annee: int,
            matricule_enseignant: str,
    ) -> Set['AttributionEnseignantDTO']:
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def search_enseignants_par_nom_prenom_annee(
            cls,
            annee: int,
            nom_prenom: str,
    ) -> List['EnseignantDTO']:
        raise NotImplementedError
