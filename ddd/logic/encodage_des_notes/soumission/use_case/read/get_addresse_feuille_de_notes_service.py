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
from ddd.logic.encodage_des_notes.soumission.commands import GetAdresseFeuilleDeNotesServiceCommand
from ddd.logic.encodage_des_notes.soumission.domain.service.adresse_feuille_de_notes import \
    AdresseFeuilleDeNotesDomainService
from ddd.logic.encodage_des_notes.soumission.dtos import AdresseFeuilleDeNotesDTO
from ddd.logic.encodage_des_notes.soumission.repository.i_adresse_feuille_de_notes import \
    IAdresseFeuilleDeNotesRepository
from ddd.logic.shared_kernel.entite.repository.entite import IEntiteRepository


def get_adresse_feuille_de_notes(
        cmd: GetAdresseFeuilleDeNotesServiceCommand,
        repo: IAdresseFeuilleDeNotesRepository,
        entite_repo: IEntiteRepository,
) -> 'AdresseFeuilleDeNotesDTO':
    return AdresseFeuilleDeNotesDomainService().get_dto(cmd.nom_cohorte, repo, entite_repo)
