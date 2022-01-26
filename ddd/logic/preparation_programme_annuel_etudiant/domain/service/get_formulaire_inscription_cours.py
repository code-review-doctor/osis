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
    UniteEnseignementDTO, FormationDTO, ContenuGroupementCatalogueDTO, UniteEnseignementCatalogueDTO, \
    GroupementCatalogueDTO, GroupementDTO
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

        formulaire_inscription = cls.convertir_formation_catalogue_en_formulaire_inscription(formation)

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
    def convertir_formation_catalogue_en_formulaire_inscription(
            cls,
            formation: 'FormationDTO'
    ) -> 'FormulaireInscriptionCoursDTO':
        return FormulaireInscriptionCoursDTO(
            annee_formation=formation.annee,
            sigle_formation=formation.sigle,
            version_formation=formation.version,
            intitule_formation=formation.intitule_formation,
            intitule_version_programme=formation.intitule_version_programme,
            racine=cls.convertir_contenu_contenu_groupement_catalogue_dto_en_contenu_groupement_dto(formation.racine)
        )

    @classmethod
    def convertir_contenu_contenu_groupement_catalogue_dto_en_contenu_groupement_dto(
            cls,
            contenu: 'ContenuGroupementCatalogueDTO'
            ) -> 'ContenuGroupementDTO':
        groupement_contenus = [
            cls.convertir_contenu_contenu_groupement_catalogue_dto_en_contenu_groupement_dto(groupement)
            for groupement in contenu.groupements_contenus
        ]
        unites_enseignement_contenues = [
            cls.convertir_unite_enseignement_catalogue_dto_en_unite_enseignement_dto(unite_enseignement)
            for unite_enseignement in contenu.unites_enseignement_contenues
        ]
        groupement_contenant = cls.convertir_groupement_catalogue_dto_en_groupement_dto(contenu.groupement_contenant)
        return ContenuGroupementDTO(
            groupement_contenant=groupement_contenant,
            unites_enseignement_contenues=unites_enseignement_contenues,
            groupements_contenus=groupement_contenus
        )

    @classmethod
    def convertir_unite_enseignement_catalogue_dto_en_unite_enseignement_dto(
            cls,
            unite_enseignement: 'UniteEnseignementCatalogueDTO',
    ) -> 'UniteEnseignementDTO':
        return UniteEnseignementDTO(
            bloc=unite_enseignement.bloc,
            code=unite_enseignement.code,
            intitule_complet=unite_enseignement.intitule_complet,
            quadrimestre=unite_enseignement.quadrimestre,
            quadrimestre_texte=unite_enseignement.quadrimestre_texte,
            credits_absolus=unite_enseignement.credits_absolus,
            credits_relatifs=unite_enseignement.credits_relatifs,
            obligatoire=unite_enseignement.obligatoire,
            volume_annuel_pp=unite_enseignement.volume_annuel_pp,
            volume_annuel_pm=unite_enseignement.volume_annuel_pm,
            session_derogation=unite_enseignement.session_derogation,
            chemin_acces=unite_enseignement.code
        )

    @classmethod
    def convertir_groupement_catalogue_dto_en_groupement_dto(
            cls,
            groupement: 'GroupementCatalogueDTO'
    ) -> 'GroupementDTO':
        return GroupementDTO(
            intitule=groupement.intitule,
            intitule_complet=groupement.intitule_complet,
            obligatoire=groupement.obligatoire,
            chemin_acces=groupement.code
        )

    @classmethod
    def _ajuster_formulaire_inscription(
            cls,
            formulaire_inscription: 'FormulaireInscriptionCoursDTO',
            groupements_ajustes: List['GroupementAjusteInscriptionCours']
    ) -> FormulaireInscriptionCoursDTO:

        for groupement in groupements_ajustes:
            groupement_concernes = cls._rechercher_groupement(formulaire_inscription.racine, groupement)

            # TODO CHERCHER INFOS UES
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
