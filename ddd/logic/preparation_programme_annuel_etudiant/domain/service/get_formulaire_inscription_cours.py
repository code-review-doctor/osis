##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2022 Université catholique de Louvain (http://www.uclouvain.be)
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
from ddd.logic.preparation_programme_annuel_etudiant.commands import GetFormulaireInscriptionCoursCommand
from ddd.logic.preparation_programme_annuel_etudiant.domain.service.i_catalogue_formations import \
    ICatalogueFormationsTranslator
from ddd.logic.preparation_programme_annuel_etudiant.dtos import FormulaireInscriptionCoursDTO, ContenuGroupementDTO, \
    GroupementDTO
from osis_common.ddd import interface


class GetFormulaireInscriptionCours(interface.DomainService):
    @classmethod
    def get_formulaire_inscription_cours(
        cls,
        cmd: 'GetFormulaireInscriptionCoursCommand',
        catalogue_formations_translator: 'ICatalogueFormationsTranslator'
    ) -> 'FormulaireInscriptionCoursDTO':
        formation = catalogue_formations_translator.get_formation(
            sigle=cmd.sigle_formation,
            annee=cmd.annee_formation,
            version=cmd.version_formation,
            transition_name=cmd.transition_formation
        )
        unites_enseignement_contenues = formation.racine.unites_enseignement_contenues
        groupements_contenus = formation.racine.groupements_contenus
        return FormulaireInscriptionCoursDTO(
            annee_formation=formation.annee,
            sigle_formation=formation.sigle,
            version_formation=formation.version,
            intitule_complet_formation=formation.intitule_complet,
            racine=ContenuGroupementDTO(
                groupement_contenant=formation.racine.groupement_contenant,
                unites_enseignement_contenues=unites_enseignement_contenues,
                groupements_contenus=groupements_contenus
            )
        )
