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
from typing import List, Union

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
    UniteEnseignementDTO, ContenuGroupementCatalogueDTO, UniteEnseignementCatalogueDTO, GroupementDTO
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

        formulaire_inscription = FormulaireInscriptionCoursDTO(
            annee_formation=formation.annee,
            sigle_formation=formation.sigle,
            version_formation=formation.version,
            intitule_formation=formation.intitule_formation,
            racine=cls.__build_contenu_formulaire_inscription_cours_dto([formation.racine])[0]
        )

        groupements_ajustes = repo.search(code_programme=cmd.code_programme)
        unite_enseignements_ajoutes_dto = cls.rechercher_unites_enseignement_ajoutees_catalogue_dto(
            groupements_ajustes,
            catalogue_unites_enseignement_translator
        )

        return cls.__ajuster_formulaire_inscription(
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
    def __build_contenu_formulaire_inscription_cours_dto(
            cls,
            contenu_ordonne_catalogue: List[Union['UniteEnseignementCatalogueDTO', 'ContenuGroupementCatalogueDTO']],
    ) -> List[Union['UniteEnseignementDTO', 'ContenuGroupementDTO']]:
        contenu = []
        for element in contenu_ordonne_catalogue:
            if isinstance(element, UniteEnseignementCatalogueDTO):
                contenu.append(
                    UniteEnseignementDTO(
                        bloc=element.bloc,
                        code=element.code,
                        intitule_complet=element.intitule_complet,
                        quadrimestre=element.quadrimestre,
                        quadrimestre_texte=element.quadrimestre_texte,
                        credits_absolus=element.credits_absolus,
                        credits_relatifs=element.credits_relatifs,
                        obligatoire=element.obligatoire,
                        volume_annuel_pp=element.volume_annuel_pp,
                        volume_annuel_pm=element.volume_annuel_pm,
                        session_derogation=element.session_derogation,
                        chemin_acces=element.code
                    )
                )
            elif isinstance(element, ContenuGroupementCatalogueDTO):
                contenu.append(
                    ContenuGroupementDTO(
                        groupement_contenant=GroupementDTO(
                            intitule=element.groupement_contenant.intitule,
                            intitule_complet=element.groupement_contenant.intitule_complet,
                            obligatoire=element.groupement_contenant.obligatoire,
                            chemin_acces=element.groupement_contenant.code
                        ),
                        contenu=cls.__build_contenu_formulaire_inscription_cours_dto(element.contenu_ordonne_catalogue)
                    )
                )
        return contenu

    @classmethod
    def __ajuster_formulaire_inscription(
            cls,
            formulaire_inscription: 'FormulaireInscriptionCoursDTO',
            groupements_ajustes: List['GroupementAjusteInscriptionCours'],
            unite_enseignement_ajoutes_dto: List['UniteEnseignementCatalogueDTO']
    ) -> FormulaireInscriptionCoursDTO:

        for groupement in groupements_ajustes:
            groupement_concernes = cls.__rechercher_groupement(formulaire_inscription.racine, groupement)

            for g in groupement_concernes:
                g.contenu.extend(
                    [
                        cls.__create_unite_enseignement_dto_for_unite_enseignement_ajoutee(
                            ue_ajoutee,
                            unite_enseignement_ajoutes_dto
                        )
                        for ue_ajoutee in groupement.unites_enseignement_ajoutees
                    ]
                )

        return formulaire_inscription

    @classmethod
    def __rechercher_groupement(
            cls,
            contenu_groupement: 'ContenuGroupementDTO',
            groupement_a_rechercher: 'GroupementAjusteInscriptionCours'
    ) -> List['ContenuGroupementDTO']:
        if groupement_a_rechercher.groupement_id.code in contenu_groupement.groupement_contenant.chemin_acces:
            return [contenu_groupement]

        groupement_trouves = []
        for groupement_contenu in filter(lambda el: isinstance(el, ContenuGroupementDTO), contenu_groupement.contenu):
            groupement_trouve = cls.__rechercher_groupement(groupement_contenu, groupement_a_rechercher)
            if groupement_trouve:
                groupement_trouves.extend(groupement_trouve)
        return groupement_trouves

    @classmethod
    def __create_unite_enseignement_dto_for_unite_enseignement_ajoutee(
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
