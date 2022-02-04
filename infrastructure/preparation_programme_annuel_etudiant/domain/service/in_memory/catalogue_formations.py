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

from ddd.logic.preparation_programme_annuel_etudiant.commands import GetContenuGroupementCommand
from ddd.logic.preparation_programme_annuel_etudiant.domain.service.i_catalogue_formations import \
    ICatalogueFormationsTranslator
from ddd.logic.preparation_programme_annuel_etudiant.dtos import FormationDTO, ContenuGroupementCatalogueDTO, \
    GroupementDTO, GroupementCatalogueDTO, UniteEnseignementCatalogueDTO
from program_management.ddd.domain.program_tree_version import STANDARD


ANNEE = 2021


def _cas_nominal_formation_version_standard():
    SIGLE = 'ECGE1BA'

    return FormationDTO(
        racine=ContenuGroupementCatalogueDTO(
            groupement_contenant=GroupementCatalogueDTO(
                intitule=SIGLE,
                obligatoire=True,
                remarque='Remarque',
                credits=Decimal(10),
                intitule_complet='Bachelier en sciences économiques et de gestion',
                code='LECGE100B'
            ),
            contenu_ordonne_catalogue=[
                ContenuGroupementCatalogueDTO(
                    groupement_contenant=GroupementCatalogueDTO(
                        intitule='Contenu :',
                        obligatoire=True,
                        remarque='Remarque',
                        credits=Decimal(10),
                        intitule_complet='Contenu :',
                        code='LECGE100T',
                    ),
                    contenu_ordonne_catalogue=[
                        ContenuGroupementCatalogueDTO(
                            groupement_contenant=GroupementCatalogueDTO(
                                intitule='Programme de base',
                                obligatoire=True,
                                remarque='Remarque',
                                credits=Decimal(10),
                                intitule_complet='Programme de base',
                                code='LECGE900R',
                            ),
                            contenu_ordonne_catalogue=[
                                UniteEnseignementCatalogueDTO(
                                    bloc=1,
                                    code='LESPO1113',
                                    intitule_complet='Sociologie et anthropologie des mondes contemporains',
                                    quadrimestre='Q1or2',
                                    quadrimestre_texte='Q1 ou Q2',
                                    credits_absolus=Decimal(5),
                                    credits_relatifs=None,
                                    volume_annuel_pm=40,
                                    volume_annuel_pp=0,
                                    obligatoire=True,
                                    session_derogation='',
                                )
                            ]),
                        ContenuGroupementCatalogueDTO(
                            groupement_contenant=GroupementCatalogueDTO(
                                intitule='Formation pluridisciplinaire en sciences humaines',
                                obligatoire=True,
                                remarque='Remarque',
                                credits=Decimal(10),
                                intitule_complet='Formation pluridisciplinaire en sciences humaines',
                                code='LECGE100R',
                            ),
                            contenu_ordonne_catalogue=[
                                UniteEnseignementCatalogueDTO(
                                    bloc=3,
                                    code='LESPO1321',
                                    intitule_complet='Economic, Political and Social Ethics',
                                    quadrimestre='Q2',
                                    quadrimestre_texte='Q2',
                                    credits_absolus=Decimal(3),
                                    credits_relatifs=None,
                                    volume_annuel_pm=30,
                                    volume_annuel_pp=0,
                                    obligatoire=True,
                                    session_derogation='',
                                )
                            ]),
                        ContenuGroupementCatalogueDTO(
                            groupement_contenant=GroupementCatalogueDTO(
                                intitule='Cours au choix',
                                obligatoire=True,
                                remarque='Remarque',
                                credits=Decimal(10),
                                intitule_complet='Cours au choix',
                                code='LECGE860R',
                            ),
                            contenu_ordonne_catalogue=[
                                UniteEnseignementCatalogueDTO(
                                    bloc=1,
                                    code='LCOPS1124',
                                    intitule_complet='Philosophie',
                                    quadrimestre='Q2',
                                    quadrimestre_texte='Q2',
                                    credits_absolus=Decimal(5),
                                    credits_relatifs=None,
                                    volume_annuel_pm=30,
                                    volume_annuel_pp=0,
                                    obligatoire=True,
                                    session_derogation='',
                                )
                            ]),
                    ])
            ],
        ),
        annee=ANNEE,
        sigle=SIGLE,
        version=STANDARD,
        intitule_formation='Bachelier en sciences économiques et de gestion'
    )


def _cas_formation_version_particuliere():
    SIGLE = 'CORP2MS/CS'

    return FormationDTO(
        racine=ContenuGroupementCatalogueDTO(
            groupement_contenant=GroupementCatalogueDTO(
                intitule=SIGLE,
                obligatoire=True,
                remarque='Remarque',
                credits=Decimal(10),
                intitule_complet='Master [120] en communication[ Double diplôme UCLouvain - uSherbrooke ]',
                code='LCORP203S'
            ),
            contenu_ordonne_catalogue=[
                ContenuGroupementCatalogueDTO(
                    groupement_contenant=GroupementCatalogueDTO(
                        intitule='Tronc commun',
                        obligatoire=True,
                        remarque='Remarque',
                        credits=Decimal(10),
                        intitule_complet='Tronc commun',
                        code='LCORP114T'
                    ),
                    contenu_ordonne_catalogue=[
                        UniteEnseignementCatalogueDTO(
                            bloc=2,
                            code='LCOMU2904B',
                            intitule_complet="Séminaire d'accompagnement au mémoire : méthodologie",
                            quadrimestre='Q2',
                            credits_absolus=Decimal(20),
                            volume_annuel_pm=0,
                            volume_annuel_pp=0,
                            obligatoire=False,
                            credits_relatifs=None,
                            session_derogation='',
                            quadrimestre_texte='Q2'
                        )
                    ]
                ),
            ],
        ),
        annee=ANNEE,
        sigle=SIGLE,
        version='DDSHERBROOKE',
        intitule_formation='Master [120] en communication[ Double diplôme UCLouvain - uSherbrooke ]',
    )


def _cas_formation_version_transition():
    SIGLE = 'DATI2MS/G'
    INTITULE = "Master [120] en science des données, orientation technologies de l'information, à finalité " \
               "spécialisée[ Version 2020 ]"
    return FormationDTO(
        racine=ContenuGroupementCatalogueDTO(
            groupement_contenant=GroupementCatalogueDTO(
                intitule=SIGLE,
                obligatoire=True,
                remarque='Remarque',
                credits=Decimal(10),
                intitule_complet=INTITULE,
                code='LDATI200S'
            ),
            contenu_ordonne_catalogue=[
                ContenuGroupementCatalogueDTO(
                    groupement_contenant=GroupementCatalogueDTO(
                        intitule='Contenu:',
                        obligatoire=True,
                        remarque='Remarque',
                        credits=Decimal(10),
                        intitule_complet='Contenu:',
                        code='TDATI101T'
                    ),
                    contenu_ordonne_catalogue=[
                        UniteEnseignementCatalogueDTO(
                            bloc=2,
                            code='LINFO2369',
                            intitule_complet="Artificial intelligence and machine learning seminar",
                            quadrimestre='Q1',
                            credits_absolus=Decimal(3),
                            volume_annuel_pm=30,
                            volume_annuel_pp=0,
                            obligatoire=False,
                            credits_relatifs=None,
                            session_derogation='',
                            quadrimestre_texte='Q1'
                        )
                    ]
                ),
            ],
        ),
        annee=ANNEE,
        sigle=SIGLE,
        version='Version 2020',
        intitule_formation=INTITULE,
    )


def _cas_formation_version_particuliere_transition():
    SIGLE = 'CORP2MS/CS'
    VERSION = 'Version 2020'
    INTITULE = "{}[ {} ]".format(
        "Master [120] en communication , à finalité spécialisée: communication stratégique des organisations",
        VERSION)
    return FormationDTO(
        racine=ContenuGroupementCatalogueDTO(
            groupement_contenant=GroupementCatalogueDTO(
                intitule=SIGLE,
                obligatoire=True,
                remarque='Remarque',
                credits=Decimal(10),
                intitule_complet=INTITULE,
                code='LCORP201S'
            ),
            contenu_ordonne_catalogue=[
                ContenuGroupementCatalogueDTO(
                    groupement_contenant=GroupementCatalogueDTO(
                        intitule='Contenu:',
                        obligatoire=True,
                        remarque='Remarque',
                        credits=Decimal(10),
                        intitule_complet='Contenu:',
                        code='TCORP102T'
                    ),
                    contenu_ordonne_catalogue=[
                        UniteEnseignementCatalogueDTO(
                            bloc=2,
                            code='LCOMU9870',
                            intitule_complet="Séminaire d'intégration en communication stratégique (Sherbrooke)",
                            quadrimestre=None,
                            quadrimestre_texte=None,
                            credits_absolus=Decimal(5),
                            credits_relatifs=None,
                            volume_annuel_pm=0,
                            volume_annuel_pp=0,
                            obligatoire=False,
                            session_derogation='',
                        )
                    ]
                ),
            ],
        ),
        annee=ANNEE,
        sigle=SIGLE,
        version=VERSION,
        intitule_formation=INTITULE,
    )


def _cas_formation_version_standard_annee_moins_1():
    SIGLE = 'ECGE1BA'
    INTITULE = 'Bachelier en sciences économiques et de gestion'

    return FormationDTO(
        racine=ContenuGroupementCatalogueDTO(
            groupement_contenant=GroupementCatalogueDTO(
                intitule=SIGLE,
                obligatoire=True,
                remarque='Remarque',
                credits=Decimal(10),
                intitule_complet=INTITULE,
                code='LECGE100B'
            ),
            contenu_ordonne_catalogue=[
                ContenuGroupementCatalogueDTO(
                    groupement_contenant=GroupementCatalogueDTO(
                        intitule='Content:',
                        obligatoire=True,
                        remarque='Remarque',
                        credits=Decimal(10),
                        intitule_complet='Content:',
                        code='LECGE100T',
                    ),
                    contenu_ordonne_catalogue=[
                        UniteEnseignementCatalogueDTO(
                            bloc=1,
                            code='LESPO1113',
                            intitule_complet='Sociologie et anthropologie des mondes contemporains',
                            quadrimestre='Q1or2',
                            quadrimestre_texte='Q1 ou Q2',
                            credits_absolus=Decimal(5),
                            credits_relatifs=None,
                            volume_annuel_pm=40,
                            volume_annuel_pp=0,
                            obligatoire=True,
                            session_derogation='',
                        )
                    ]),
            ],
        ),
        annee=ANNEE-1,
        sigle=SIGLE,
        version=STANDARD,
        intitule_formation=INTITULE
    )


def _cas_mini_formation_version_standard():
    SIGLE = 'MINADROI'
    INTITULE = "Mineure en droit (accès)"

    return FormationDTO(
        racine=ContenuGroupementCatalogueDTO(
            groupement_contenant=GroupementCatalogueDTO(
                intitule=SIGLE,
                obligatoire=True,
                remarque='Remarque',
                credits=Decimal(10),
                intitule_complet=INTITULE,
                code='LADRT100I'
            ),
            contenu_ordonne_catalogue=[
                ContenuGroupementCatalogueDTO(
                    groupement_contenant=GroupementCatalogueDTO(
                        intitule='Contenu:',
                        obligatoire=True,
                        remarque='Remarque',
                        credits=Decimal(10),
                        intitule_complet='Contenu:',
                        code='LADRT100T',
                    ),
                    contenu_ordonne_catalogue=[
                        UniteEnseignementCatalogueDTO(
                            bloc=3,
                            code='LDROI1225',
                            intitule_complet='Droit de la procédure pénale',
                            quadrimestre='Q2',
                            quadrimestre_texte='Q2',
                            credits_absolus=Decimal(4),
                            credits_relatifs=None,
                            volume_annuel_pm=45,
                            volume_annuel_pp=10,
                            obligatoire=True,
                            session_derogation='',
                        )
                    ]),
            ],
        ),
        annee=ANNEE,
        sigle=SIGLE,
        version=STANDARD,
        intitule_formation=INTITULE
    )


def _cas_mini_formation_version_particuliere():
    SIGLE = 'MINADROI'
    VERSION = "Pour les bacheliers en sciences économiques et de gestion"
    INTITULE = "{}[{}]".format("Mineure en droit (accès)", VERSION)

    return FormationDTO(
        racine=ContenuGroupementCatalogueDTO(
            groupement_contenant=GroupementCatalogueDTO(
                intitule=SIGLE,
                obligatoire=True,
                remarque='Remarque',
                credits=Decimal(10),
                intitule_complet=INTITULE,
                code='LADRT100S'
            ),
            contenu_ordonne_catalogue=[
                ContenuGroupementCatalogueDTO(
                    groupement_contenant=GroupementCatalogueDTO(
                        intitule='Contenu:',
                        obligatoire=True,
                        remarque='Remarque',
                        credits=Decimal(10),
                        intitule_complet='Contenu:',
                        code='LADRT101T',
                    ),
                    contenu_ordonne_catalogue=[
                        UniteEnseignementCatalogueDTO(
                            bloc=2,
                            code='LDROI1222',
                            intitule_complet="Droit constitutionnel",
                            quadrimestre='Q1and2',
                            quadrimestre_texte='Q1 et Q2',
                            credits_absolus=Decimal(8),
                            credits_relatifs=None,
                            volume_annuel_pm=90,
                            volume_annuel_pp=14,
                            obligatoire=True,
                            session_derogation='',
                        )
                    ]),
            ],
        ),
        annee=ANNEE,
        sigle=SIGLE,
        version=VERSION,
        intitule_formation=INTITULE
    )


def _cas_mini_formation_version_transition():
    SIGLE = 'MINADROI'
    VERSION = "Version 2020 "
    INTITULE = "{}[{}]".format("Mineure en droit (accès)", VERSION)

    return FormationDTO(
        racine=ContenuGroupementCatalogueDTO(
            groupement_contenant=GroupementCatalogueDTO(
                intitule=SIGLE,
                obligatoire=True,
                remarque='Remarque',
                credits=Decimal(10),
                intitule_complet=INTITULE,
                code='LADRT111S'
            ),
            contenu_ordonne_catalogue=[
                ContenuGroupementCatalogueDTO(
                    groupement_contenant=GroupementCatalogueDTO(
                        intitule='Contenu:',
                        obligatoire=True,
                        remarque='Remarque',
                        credits=Decimal(10),
                        intitule_complet='Contenu:',
                        code='TADRT100T',
                    ),
                    contenu_ordonne_catalogue=[
                        UniteEnseignementCatalogueDTO(
                            bloc=2,
                            code='LDROI1223',
                            intitule_complet="Droit des obligations",
                            quadrimestre='Q3',
                            quadrimestre_texte='Q3',
                            credits_absolus=Decimal(11.5),
                            credits_relatifs=None,
                            volume_annuel_pm=0,
                            volume_annuel_pp=50,
                            obligatoire=True,
                            session_derogation='',
                        )
                    ]),
            ],
        ),
        annee=ANNEE,
        sigle=SIGLE,
        version=VERSION,
        intitule_formation=INTITULE
    )


def _cas_mini_formation_version_particuliere_transition():
    SIGLE = 'MINADROI'
    VERSION = "Version 2020 "
    INTITULE = "{}[{}]".format("Mineure en droit (accès)", VERSION)

    return FormationDTO(
        racine=ContenuGroupementCatalogueDTO(
            groupement_contenant=GroupementCatalogueDTO(
                intitule=SIGLE,
                obligatoire=True,
                remarque='Remarque',
                credits=Decimal(10),
                intitule_complet=INTITULE,
                code='LADRT101S'
            ),
            contenu_ordonne_catalogue=[
                ContenuGroupementCatalogueDTO(
                    groupement_contenant=GroupementCatalogueDTO(
                        intitule='Contenu:',
                        obligatoire=True,
                        remarque='Remarque',
                        credits=Decimal(10),
                        intitule_complet='Contenu:',
                        code='TADRT101T',
                    ),
                    contenu_ordonne_catalogue=[
                        UniteEnseignementCatalogueDTO(
                            bloc=2,
                            code='LDROI1225',
                            intitule_complet="Droit de la procédure pénale",
                            quadrimestre='Q2',
                            quadrimestre_texte='Q2',
                            credits_absolus=Decimal(4),
                            credits_relatifs=None,
                            volume_annuel_pm=45,
                            volume_annuel_pp=10,
                            obligatoire=True,
                            session_derogation='',
                        )
                    ]),
            ],
        ),
        annee=ANNEE,
        sigle=SIGLE,
        version=VERSION,
        intitule_formation=INTITULE
    )


def _cas_mini_formation_version_standard_annee_moins_1():
    SIGLE = 'MINADROI'
    VERSION = STANDARD
    INTITULE = "Mineure en droit (accès)"

    return FormationDTO(
        racine=ContenuGroupementCatalogueDTO(
            groupement_contenant=GroupementCatalogueDTO(
                intitule=SIGLE,
                obligatoire=True,
                remarque='Remarque',
                credits=Decimal(10),
                intitule_complet=INTITULE,
                code='LADRT121S'
            ),
            contenu_ordonne_catalogue=[
                ContenuGroupementCatalogueDTO(
                    groupement_contenant=GroupementCatalogueDTO(
                        intitule='Contenu:',
                        obligatoire=True,
                        remarque='Remarque',
                        credits=Decimal(10),
                        intitule_complet='Contenu:',
                        code='LADRT100T',
                    ),
                    contenu_ordonne_catalogue=[
                        UniteEnseignementCatalogueDTO(
                            bloc=3,
                            code='LDROI1225',
                            intitule_complet="Droit de la procédure pénale",
                            quadrimestre='Q2',
                            quadrimestre_texte='Q2',
                            credits_absolus=Decimal(4),
                            credits_relatifs=None,
                            volume_annuel_pm=45,
                            volume_annuel_pp=10,
                            obligatoire=True,
                            session_derogation='',
                        )
                    ]),
            ],
        ),
        annee=ANNEE-1,
        sigle=SIGLE,
        version=VERSION,
        intitule_formation=INTITULE
    )


CAS_NOMINAL_FORMATION_STANDARD = _cas_nominal_formation_version_standard()
CAS_FORMATION_VERSION_PARTICULIERE = _cas_formation_version_particuliere()
CAS_FORMATION_VERSION_TRANSITION = _cas_formation_version_transition()
CAS_FORMATION_VERSION_PARTICULIERE_TRANSITION = _cas_formation_version_particuliere_transition()
CAS_FORMATION_STANDARD_ANNEE_MOINS_1 = _cas_formation_version_standard_annee_moins_1()
CAS_MINI_FORMATION_VERSION_STANDARD = _cas_mini_formation_version_standard()
CAS_MINI_FORMATION_VERSION_PARTICULIERE = _cas_mini_formation_version_particuliere()
CAS_MINI_FORMATION_VERSION_TRANSITION = _cas_mini_formation_version_transition()
CAS_MINI_FORMATION_VERSION_PARTICULIERE_TRANSITION = _cas_mini_formation_version_particuliere_transition()
CAS_MINI_FORMATION_VERSION_STANDARD_ANNEE_MOINS_1 = _cas_mini_formation_version_standard_annee_moins_1()


class CatalogueFormationsTranslatorInMemory(ICatalogueFormationsTranslator):

    dtos = [
        CAS_NOMINAL_FORMATION_STANDARD,
        CAS_FORMATION_VERSION_PARTICULIERE,
        CAS_FORMATION_VERSION_TRANSITION,
        CAS_FORMATION_VERSION_PARTICULIERE_TRANSITION,
        CAS_FORMATION_STANDARD_ANNEE_MOINS_1,
        CAS_MINI_FORMATION_VERSION_STANDARD,
        CAS_MINI_FORMATION_VERSION_PARTICULIERE,
        CAS_MINI_FORMATION_VERSION_TRANSITION,
        CAS_MINI_FORMATION_VERSION_PARTICULIERE_TRANSITION,
        CAS_MINI_FORMATION_VERSION_STANDARD_ANNEE_MOINS_1,
    ]

    @classmethod
    def get_formation(cls, code_programme: str, annee: int) -> 'FormationDTO':
        return next(
            dto for dto in cls.dtos
            if dto.racine.groupement_contenant.code == code_programme and dto.annee == annee
        )

    @classmethod
    def get_groupement(
            cls,
            sigle_formation: str,
            annee: int,
            version_formation: str,
            code_groupement: str
    ) -> 'GroupementDTO':
        raise NotImplementedError()

    @classmethod
    def get_contenu_groupement(cls, cmd: GetContenuGroupementCommand) -> 'GroupementContenantDTO':
        raise NotImplementedError()
