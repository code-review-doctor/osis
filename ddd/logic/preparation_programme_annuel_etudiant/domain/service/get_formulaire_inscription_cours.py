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
import itertools
from typing import List

from ddd.logic.preparation_programme_annuel_etudiant.commands import GetFormulaireInscriptionCoursCommand
from ddd.logic.preparation_programme_annuel_etudiant.domain.model.groupement_ajuste_inscription_cours import \
    GroupementAjusteInscriptionCours
from ddd.logic.preparation_programme_annuel_etudiant.domain.model.unite_enseignement_ajoutee import \
    UniteEnseignementAjoutee
from ddd.logic.preparation_programme_annuel_etudiant.domain.service.i_catalogue_formations import \
    ICatalogueFormationsTranslator
from ddd.logic.preparation_programme_annuel_etudiant.domain.service.i_catalogue_unites_enseignement import \
    ICatalogueUnitesEnseignementTranslator
from ddd.logic.preparation_programme_annuel_etudiant.dtos import FormulaireInscriptionCoursDTO, ContenuGroupementDTO, \
    UniteEnseignementDTO, FormationDTO, ContenuGroupementCatalogueDTO, UniteEnseignementCatalogueDTO, \
    GroupementCatalogueDTO, GroupementDTO
from ddd.logic.preparation_programme_annuel_etudiant.repository.i_groupement_ajuste_inscription_cours import \
    IGroupementAjusteInscriptionCoursRepository
from education_group.ddd.domain.group import GroupIdentity
from osis_common.ddd import interface


class GetFormulaireInscriptionCours(interface.DomainService):
    @classmethod
    def get_formulaire_inscription_cours(
            cls,
            cmd: 'GetFormulaireInscriptionCoursCommand',
            repo: 'IGroupementAjusteInscriptionCoursRepository',
            catalogue_formations_translator: 'ICatalogueFormationsTranslator',
            catalogue_unites_enseignement_translator: 'ICatalogueUnitesEnseignementTranslator'
    ) -> 'FormulaireInscriptionCoursDTO':
        formation = catalogue_formations_translator.get_formation(
            code_programme=cmd.code_programme,
            annee=cmd.annee,
        )

        formulaire_inscription = cls.convertir_formation_catalogue_en_formulaire_inscription(formation)

        groupements_ajustes = repo.search(
            groupement_id=GroupIdentity(
                year=cmd.annee,
                code=cmd.code_programme,
            )
        )

        unite_enseignements_ajoutes_dto = cls.rechercher_unites_enseignement_ajoutees_catalogue_dto(
            groupements_ajustes,
            catalogue_unites_enseignement_translator
        )

        return cls._ajuster_formulaire_inscription(
            formulaire_inscription,
            groupements_ajustes,
            unite_enseignements_ajoutes_dto
        )

    @classmethod
    def rechercher_unites_enseignement_ajoutees_catalogue_dto(
            cls,
            groupements_ajustes: List['GroupementAjusteInscriptionCours'],
            catalogue_unites_enseignement_translator: 'ICatalogueUnitesEnseignementTranslator'
            ) -> List['UniteEnseignementCatalogueDTO']:
        unites_enseignement_ajoutees = itertools.chain.from_iterable(
            [
                groupement.unites_enseignement_ajoutees
                for groupement in groupements_ajustes
            ]
        )
        entity_id_unites_enseignement = [
            unite_enseignement.unite_enseignement_identity
            for unite_enseignement in unites_enseignement_ajoutees
        ]

        return catalogue_unites_enseignement_translator.search(
            entity_ids=entity_id_unites_enseignement
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
            intitule_formation=formation.intitule_complet,
            intitule_version_programme=formation.intitule_complet,
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
            groupements_ajustes: List['GroupementAjusteInscriptionCours'],
            unite_enseignement_ajoutes_dto: List['UniteEnseignementCatalogueDTO']
    ) -> FormulaireInscriptionCoursDTO:

        for groupement in groupements_ajustes:
            groupement_concernes = cls._rechercher_groupement(formulaire_inscription.racine, groupement)

            for g in groupement_concernes:
                g.unites_enseignement_contenues.extend(
                    [
                        cls._create_unite_enseignement_dto_for_unite_enseignement_ajoutee(
                            ue_ajoutee,
                            unite_enseignement_ajoutes_dto
                        )
                        for ue_ajoutee in groupement.unites_enseignement_ajoutees
                    ]
                )

        return formulaire_inscription

    @classmethod
    def _create_unite_enseignement_dto_for_unite_enseignement_ajoutee(
            cls,
            unite_enseignement_ajoutee: 'UniteEnseignementAjoutee',
            unite_enseignement_ajoutes_dto: List['UniteEnseignementCatalogueDTO'],
    ) -> 'UniteEnseignementDTO':
        dto_correspondant = next(
            dto for dto in unite_enseignement_ajoutes_dto
            if dto.code == unite_enseignement_ajoutee.code
        )
        return UniteEnseignementDTO(
            bloc=1,
            code=unite_enseignement_ajoutee.code,
            intitule_complet=dto_correspondant.intitule_complet,
            quadrimestre=dto_correspondant.quadrimestre,
            quadrimestre_texte=dto_correspondant.quadrimestre_texte,
            credits_absolus=dto_correspondant.credits_absolus,
            credits_relatifs=dto_correspondant.credits_relatifs,
            volume_annuel_pm=dto_correspondant.volume_annuel_pm,
            volume_annuel_pp=dto_correspondant.volume_annuel_pp,
            chemin_acces=unite_enseignement_ajoutee.code,
            obligatoire=dto_correspondant.obligatoire,
            session_derogation=dto_correspondant.session_derogation,
        )

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
