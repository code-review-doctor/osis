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

from ddd.logic.preparation_programme_annuel_etudiant.commands import GetProgrammeInscriptionCoursCommand
from ddd.logic.preparation_programme_annuel_etudiant.domain.service.get_programme_inscription_cours import \
    GetProgrammeInscriptionCours
from ddd.logic.preparation_programme_annuel_etudiant.domain.service.i_catalogue_formations import \
    ICatalogueFormationsTranslator
from ddd.logic.preparation_programme_annuel_etudiant.domain.service.i_catalogue_unites_enseignement import \
    ICatalogueUnitesEnseignementTranslator
from ddd.logic.preparation_programme_annuel_etudiant.dtos import ProgrammeInscriptionCoursDTO
from ddd.logic.preparation_programme_annuel_etudiant.repository.i_groupement_ajuste_inscription_cours import \
    IGroupementAjusteInscriptionCoursRepository


def get_programme_inscription_cours(
        cmd: 'GetProgrammeInscriptionCoursCommand',
        repository: 'IGroupementAjusteInscriptionCoursRepository',
        translator: 'ICatalogueFormationsTranslator',
        catalogue_unites_enseignement_translator: 'ICatalogueUnitesEnseignementTranslator'
) -> 'ProgrammeInscriptionCoursDTO':
    return GetProgrammeInscriptionCours.get_programme_inscription_cours(
        cmd=cmd,
        groupement_ajuste_repository=repository,
        catalogue_formations_translator=translator,
        catalogue_unites_enseignement_translator=catalogue_unites_enseignement_translator
    )
