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
from decimal import Decimal
from typing import List

from ddd.logic.preparation_programme_annuel_etudiant.commands import GetFormulaireInscriptionCoursCommand
from ddd.logic.preparation_programme_annuel_etudiant.domain.model.groupement_ajuste_inscription_cours import \
    GroupementAjusteInscriptionCours
from ddd.logic.preparation_programme_annuel_etudiant.domain.service.i_catalogue_formations import \
    ICatalogueFormationsTranslator
from ddd.logic.preparation_programme_annuel_etudiant.dtos import FormulaireInscriptionCoursDTO, ContenuGroupementDTO, \
    UniteEnseignementDTO
from ddd.logic.preparation_programme_annuel_etudiant.repository.i_groupement_ajuste_inscription_cours import \
    IGroupementAjusteInscriptionCoursRepository
from osis_common.ddd import interface
from program_management.ddd.domain.program_tree_version import ProgramTreeVersionIdentityBuilder


class GetFormulaireInscriptionCours(interface.DomainService):
    @classmethod
    def get_formulaire_inscription_cours(
            cls,
            cmd: 'GetFormulaireInscriptionCoursCommand',
            repo: 'IGroupementAjusteInscriptionCoursRepository',
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

        formulaire_inscription = FormulaireInscriptionCoursDTO(
            annee_formation=formation.annee,
            sigle_formation=formation.sigle,
            version_formation=formation.version,
            intitule_formation=formation.intitule_formation,
            intitule_version_programme=formation.intitule_version_programme,
            racine=ContenuGroupementDTO(
                groupement_contenant=formation.racine.groupement_contenant,
                unites_enseignement_contenues=unites_enseignement_contenues,
                groupements_contenus=groupements_contenus
            )
        )

        groupements_ajustes = repo.search(
            version_programme_id=ProgramTreeVersionIdentityBuilder().build(
                year=cmd.annee_formation,
                offer_acronym=cmd.sigle_formation,
                version_name=cmd.version_formation,
                transition_name=cmd.transition_formation
            )
        )

        return cls._ajuster_formulaire_inscription(
            formulaire_inscription,
            groupements_ajustes
        )

    @classmethod
    def _ajuster_formulaire_inscription(
            cls,
            formulaire_inscription: 'FormulaireInscriptionCoursDTO',
            groupements_ajustes: List['GroupementAjusteInscriptionCours']
            ) -> FormulaireInscriptionCoursDTO:

        for groupement in groupements_ajustes:
            groupement_concernes = cls._rechercher_groupement(formulaire_inscription.racine, groupement)

            for g in groupement_concernes:

                g.unites_enseignement_contenues.extend(
                    [
                        UniteEnseignementDTO(
                            bloc=1,
                            code=ue_ajoutes.code,
                            intitule_complet="tchey",
                            quadrimestre="Q1",
                            quadrimestre_texte="Q1",
                            credits_absolus=Decimal(21),
                            credits_relatifs=21,
                            volume_annuel_pm=10,
                            volume_annuel_pp=10,
                            chemin_acces=g.groupement_contenant.chemin_acces + "|" + ue_ajoutes.code,
                            obligatoire=True,
                            session_derogation="Nope",
                        )
                        for ue_ajoutes in groupement.unites_enseignement_ajoutees
                    ]
                )

        return formulaire_inscription

    @classmethod
    def _rechercher_groupement(
            cls,
            contenu_groupement: 'ContenuGroupementDTO',
            groupement_a_rechercher: 'GroupementAjusteInscriptionCours'
    ) -> List['ContenuGroupementDTO']:
        if groupement_a_rechercher.groupement_id.code in contenu_groupement.groupement_contenant.chemin_acces:
            return [contenu_groupement]

        groupement_trouves = []
        for groupement_contenu in contenu_groupement.groupements_contenus:
            groupement_trouve = cls._rechercher_groupement(groupement_contenu, groupement_a_rechercher)
            if groupement_trouve:
                groupement_trouves.extend(groupement_trouve)

        return groupement_trouves

