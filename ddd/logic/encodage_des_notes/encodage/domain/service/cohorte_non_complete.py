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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from collections import defaultdict
from typing import List, Tuple, Iterable, Callable, Dict, Any, Set

from ddd.logic.encodage_des_notes.encodage.domain.model.note_etudiant import NoteEtudiant
from ddd.logic.encodage_des_notes.encodage.repository.note_etudiant import INoteEtudiantRepository
from ddd.logic.encodage_des_notes.shared_kernel.domain.service.i_inscription_examen import IInscriptionExamenTranslator
from ddd.logic.encodage_des_notes.soumission.dtos import DesinscriptionExamenDTO
from osis_common.ddd import interface


CodeUniteEnseignement = str
NomCohorte = str


class CohorteAvecEncodageIncomplet(interface.DomainService):

    @classmethod
    def search(
            cls,
            codes_unite_enseignement: List[CodeUniteEnseignement],
            annee_academique: int,
            numero_session: int,
            note_etudiant_repo: 'INoteEtudiantRepository',
            inscr_exam_translator: 'IInscriptionExamenTranslator',
    ) -> List[Tuple[CodeUniteEnseignement, NomCohorte]]:
        notes = note_etudiant_repo.search(
            codes_unite_enseignement=codes_unite_enseignement,
            numero_session=numero_session,
            annee_academique=annee_academique,
        )
        etds_desinscrits = inscr_exam_translator.search_desinscrits_pour_plusieurs_unites_enseignement(
            set(codes_unite_enseignement),
            numero_session,
            annee_academique,
        )
        notes = cls._filtrer_etudiants_inscrits(notes, etds_desinscrits)
        notes_groupees_par_unite_enseignement_et_cohorte = groupby(
            notes,
            key=lambda note: (note.code_unite_enseignement, note.nom_cohorte)
        )
        result = []
        for key, ensemble_de_notes in notes_groupees_par_unite_enseignement_et_cohorte.items():
            if not cls._ensemble_de_notes_est_complet(ensemble_de_notes):
                result.append(key)
        return result

    @classmethod
    def _ensemble_de_notes_est_complet(cls, notes: List['NoteEtudiant']) -> bool:
        return all(not note.is_manquant for note in notes)

    @classmethod
    def _filtrer_etudiants_inscrits(cls, notes, etds_desinscrits):
        return [
            n for n in notes if cls._est_inscrit(etds_desinscrits, n)
        ]

    @classmethod
    def _est_inscrit(cls, etudiants_desinscrits: Set['DesinscriptionExamenDTO'], note: 'NoteEtudiant') -> bool:
        return not any(
            etd for etd in etudiants_desinscrits
            if etd.noma == note.noma and etd.code_unite_enseignement == note.code_unite_enseignement
        )


def groupby(datas: Iterable[Any], key: Callable) -> Dict:
    result = defaultdict(list)
    for data in datas:
        result[key(data)].append(data)
    return result
