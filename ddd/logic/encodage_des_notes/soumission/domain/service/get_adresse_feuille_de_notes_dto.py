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
from ddd.logic.encodage_des_notes.shared_kernel.domain.service.i_periode_encodage_notes import \
    IPeriodeEncodageNotesTranslator
from ddd.logic.encodage_des_notes.soumission.builder.adresse_feuille_de_notes_identity_builder import \
    AdresseFeuilleDeNotesIdentityBuilder
from ddd.logic.encodage_des_notes.soumission.domain.service.annee_academique_addresse_feuille_de_notes import \
    AnneeAcademiqueAddresseFeuilleDeNotesDomaineService
from ddd.logic.encodage_des_notes.soumission.dtos import AdresseFeuilleDeNotesDTO
from ddd.logic.encodage_des_notes.soumission.repository.i_adresse_feuille_de_notes import \
    IAdresseFeuilleDeNotesRepository
from ddd.logic.shared_kernel.academic_year.repository.i_academic_year import IAcademicYearRepository
from osis_common.ddd import interface


class GetAdresseFeuilleDeNotesDTODomainService(interface.DomainService):

    @classmethod
    def get(
            cls,
            nom_cohorte: str,
            repo: 'IAdresseFeuilleDeNotesRepository',
            periode_soumission_note_translator: 'IPeriodeEncodageNotesTranslator',
            academic_year_repo: 'IAcademicYearRepository'
    ) -> AdresseFeuilleDeNotesDTO:
        annee_academique = AnneeAcademiqueAddresseFeuilleDeNotesDomaineService().get(
            periode_soumission_note_translator,
            academic_year_repo
        )
        identite = AdresseFeuilleDeNotesIdentityBuilder().build_from_nom_cohorte_and_annee_academique(
            nom_cohorte,
            annee_academique
        )
        try:
            return repo.search_dtos([identite])[0]
        except IndexError:
            return AdresseFeuilleDeNotesDTO(nom_cohorte=nom_cohorte, annee_academique=annee_academique)
