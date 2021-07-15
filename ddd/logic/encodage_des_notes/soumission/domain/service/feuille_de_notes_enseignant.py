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

from ddd.logic.encodage_des_notes.soumission.commands import EncoderFeuilleDeNotesCommand
from ddd.logic.encodage_des_notes.soumission.domain.model.feuille_de_notes import FeuilleDeNotes
from ddd.logic.encodage_des_notes.soumission.domain.model.responsable_de_notes import ResponsableDeNotes
from ddd.logic.encodage_des_notes.soumission.domain.service.i_attribution_enseignant import \
    IAttributionEnseignantTranslator
from ddd.logic.encodage_des_notes.soumission.domain.service.i_inscription_examen import IInscriptionExamenTranslator
from ddd.logic.encodage_des_notes.soumission.domain.service.i_periode_soumission_notes import \
    IPeriodeSoumissionNotesTranslator
from ddd.logic.encodage_des_notes.soumission.domain.service.i_signaletique_etudiant import \
    ISignaletiqueEtudiantTranslator
from ddd.logic.encodage_des_notes.soumission.domain.service.i_unite_enseignement import IUniteEnseignementTranslator
from ddd.logic.encodage_des_notes.soumission.domain.validator.exceptions import \
    EnseignantNonAttribueUniteEnseignementException
from ddd.logic.encodage_des_notes.soumission.dtos import FeuilleDeNotesEnseignantDTO
from osis_common.ddd import interface


class FeuilleDeNotesEnseignant(interface.DomainService):

    @classmethod
    def get(
            cls,
            feuille_de_notes: 'FeuilleDeNotes',
            responsable_de_notes: 'ResponsableDeNotes',
            periode_soumission_note_translator: 'IPeriodeSoumissionNotesTranslator',
            inscription_examen_translator: 'IInscriptionExamenTranslator',
            signaletique_etudiant_translator: 'ISignaletiqueEtudiantTranslator',
            attribution_translator: 'IAttributionEnseignantTranslator',
            unite_enseignement_translator: 'IUniteEnseignementTranslator',
    ) -> 'FeuilleDeNotesEnseignantDTO':
        pass
