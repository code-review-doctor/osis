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
import itertools
from typing import List, Set

from ddd.logic.encodage_des_notes.shared_kernel.domain.service.i_inscription_examen import IInscriptionExamenTranslator
from ddd.logic.encodage_des_notes.shared_kernel.domain.service.i_periode_encodage_notes import \
    IPeriodeEncodageNotesTranslator
from ddd.logic.encodage_des_notes.soumission.builder.adresse_feuille_de_notes_identity_builder import \
    AdresseFeuilleDeNotesIdentityBuilder
from ddd.logic.encodage_des_notes.soumission.domain.service.get_adresse_feuille_de_notes_dto import \
    GetAdresseFeuilleDeNotesDTODomainService
from ddd.logic.encodage_des_notes.soumission.domain.service.i_entites_cohorte import IEntitesCohorteTranslator
from ddd.logic.encodage_des_notes.soumission.dtos import DonneesAdministrativesFeuilleDeNotesDTO, \
    AdresseFeuilleDeNotesDTO
from ddd.logic.encodage_des_notes.soumission.repository.i_adresse_feuille_de_notes import \
    IAdresseFeuilleDeNotesRepository
from ddd.logic.shared_kernel.academic_year.repository.i_academic_year import IAcademicYearRepository
from ddd.logic.shared_kernel.entite.repository.entiteucl import IEntiteUCLRepository
from osis_common.ddd import interface


class DonneesAdministratives(interface.DomainService):

    @classmethod
    def search(
            cls,
            codes_unites_enseignement: List['str'],
            periode_soumission_note_translator: 'IPeriodeEncodageNotesTranslator',
            inscr_exam_translator: 'IInscriptionExamenTranslator',
            adresse_feuille_de_notes_repository: 'IAdresseFeuilleDeNotesRepository',
            entite_repository: 'IEntiteUCLRepository',
            entites_cohorte_translator: 'IEntitesCohorteTranslator',
    ) -> List['DonneesAdministrativesFeuilleDeNotesDTO']:
        periode_soumission_ouverte = periode_soumission_note_translator.get()
        annee_academique = periode_soumission_ouverte.annee_concernee

        cohortes_par_unite_enseignement = _get_cohortes_par_unite_enseignement(
            codes_unites_enseignement,
            inscr_exam_translator,
            periode_soumission_ouverte,
        )
        noms_cohortes = set(itertools.chain.from_iterable(cohortes_par_unite_enseignement.values()))

        adresse_par_cohorte = _get_adresse_par_cohorte(
            adresse_feuille_de_notes_repository=adresse_feuille_de_notes_repository,
            noms_cohortes=noms_cohortes,
            periode_soumission_note_translator=periode_soumission_note_translator,
            entite_repository=entite_repository,
            entites_cohorte_translator=entites_cohorte_translator,
        )

        result = []
        for code in codes_unites_enseignement:
            for nom_cohorte in cohortes_par_unite_enseignement.get(code, []):
                dto = DonneesAdministrativesFeuilleDeNotesDTO(
                    sigle_formation=nom_cohorte,
                    code_unite_enseignement=code,
                    contact_feuille_de_notes=adresse_par_cohorte.get(
                        nom_cohorte,
                        AdresseFeuilleDeNotesDTO(nom_cohorte=nom_cohorte, annee_academique=annee_academique)
                    ),
                )
                result.append(dto)
        return result


def _get_responsable_de_notes(code, periode_soumission_ouverte, responsables_de_notes):
    matric_fgs_responsable = next(
        (
            resp.matricule_fgs_enseignant for resp in responsables_de_notes
            if resp.is_responsable_unite_enseignement(code, periode_soumission_ouverte.annee_concernee)
        ),
        None
    )
    return matric_fgs_responsable


def _get_adresse_par_cohorte(
        adresse_feuille_de_notes_repository: 'IAdresseFeuilleDeNotesRepository',
        noms_cohortes: Set['str'],
        periode_soumission_note_translator: 'IPeriodeEncodageNotesTranslator',
        entite_repository: 'IEntiteUCLRepository',
        entites_cohorte_translator: 'IEntitesCohorteTranslator',
):
    adresse_par_cohorte = dict()
    for nom_cohorte in noms_cohortes:
        adresse = GetAdresseFeuilleDeNotesDTODomainService().get(
            nom_cohorte=nom_cohorte,
            repo=adresse_feuille_de_notes_repository,
            periode_soumission_note_translator=periode_soumission_note_translator,
            entite_repository=entite_repository,
            entites_cohorte_translator=entites_cohorte_translator,
        )
        adresse_par_cohorte[adresse.nom_cohorte] = adresse
    return adresse_par_cohorte


def _get_deliberation_par_cohorte(deliberation_translator, noms_cohortes, periode_soumission_ouverte):
    deliberations = deliberation_translator.search(
        periode_soumission_ouverte.annee_concernee,
        periode_soumission_ouverte.session_concernee,
        noms_cohortes,
    )
    return {delib.nom_cohorte: delib for delib in deliberations}


def _get_cohortes_par_unite_enseignement(codes_unites_enseignement, inscr_exam_translator, periode_soumission_ouverte):
    cohortes_par_unite_enseignement = dict()
    inscr_examens = inscr_exam_translator.search_inscrits_pour_plusieurs_unites_enseignement(
        codes_unites_enseignement=set(codes_unites_enseignement),
        annee=periode_soumission_ouverte.annee_concernee,
        numero_session=periode_soumission_ouverte.session_concernee,
    )
    desincr_examens = inscr_exam_translator.search_desinscrits_pour_plusieurs_unites_enseignement(
        codes_unites_enseignement=set(codes_unites_enseignement),
        annee=periode_soumission_ouverte.annee_concernee,
        numero_session=periode_soumission_ouverte.session_concernee,
    )

    for row in inscr_examens | desincr_examens:
        cohortes_par_unite_enseignement.setdefault(row.code_unite_enseignement, set()).add(row.nom_cohorte)
    return cohortes_par_unite_enseignement


def _get_signaletique_par_matricule(responsables_de_notes, signaletique_personne_translator):
    signaletiques = signaletique_personne_translator.search(
        matricules_fgs={r.matricule_fgs_enseignant for r in responsables_de_notes}
    )
    return {signal.matricule_fgs: signal for signal in signaletiques}
