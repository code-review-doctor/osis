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
from base.models.enums.peps_type import PepsTypes
from ddd.logic.encodage_des_notes.encodage.domain.service.i_feuille_de_notes_enseignant import \
    IFeuilleDeNotesEnseignantTranslator
from ddd.logic.encodage_des_notes.soumission.dtos import FeuilleDeNotesEnseignantDTO, EnseignantDTO, NoteEtudiantDTO, \
    DateDTO, EtudiantPepsDTO


class FeuilleDeNotesEnseignantTranslatorInMemory(IFeuilleDeNotesEnseignantTranslator):

    @classmethod
    def get(
            cls,
            code_unite_enseignement: str,
            matricule_fgs_enseignant: str,
    ) -> 'FeuilleDeNotesEnseignantDTO':
        return FeuilleDeNotesEnseignantDTO(
            code_unite_enseignement='LDROI1001',
            intitule_complet_unite_enseignement='Intitule complet unite enseignement',
            responsable_note=EnseignantDTO(
                nom='Chileng',
                prenom='Jean-Michel',
            ),
            autres_enseignants=[
                EnseignantDTO(nom="Jolypas", prenom="Michelle"),
                EnseignantDTO(nom="Smith", prenom="Charles"),
                EnseignantDTO(nom="Yolo", prenom="Ana"),
            ],
            annee_academique=2020,
            numero_session=2,
            note_decimale_est_autorisee=False,
            notes_etudiants=[
                NoteEtudiantDTO(
                    est_soumise=False,
                    date_remise_de_notes=DateDTO(jour=5, mois=6, annee=2020),
                    nom_cohorte='DROI1BA',
                    noma='11111111',
                    nom='NomEtudiant1',
                    prenom='PrenomEtudiant1',
                    peps=EtudiantPepsDTO(
                        type_peps=PepsTypes.ARRANGEMENT_JURY.name,
                        tiers_temps=True,
                        copie_adaptee=True,
                        local_specifique=True,
                        autre_amenagement=True,
                        details_autre_amenagement="Details autre aménagement",
                        accompagnateur="Accompagnateur",
                    ),
                    email='nometudiant1_prenometudiant1@email.be',
                    note='',
                    inscrit_tardivement=True,
                    desinscrit_tardivement=False,
                ),
                NoteEtudiantDTO(
                    est_soumise=False,
                    date_remise_de_notes=DateDTO(jour=6, mois=6, annee=2020),
                    nom_cohorte='DROI1BA',
                    noma='11111112',
                    nom='NomEtudiant2',
                    prenom='PrenomEtudiant2',
                    peps=None,
                    email='nometudiant2_prenometudiant2@email.be',
                    note='',
                    inscrit_tardivement=False,
                    desinscrit_tardivement=True,
                ),
            ],
        )
