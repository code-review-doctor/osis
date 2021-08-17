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
from ddd.logic.encodage_des_notes.shared_kernel.service.i_attribution_enseignant import IAttributionEnseignantTranslator
from ddd.logic.encodage_des_notes.soumission.domain.validator.exceptions import \
    EnseignantNonAttribueUniteEnseignementException
from osis_common.ddd import interface


class EnseignantAttribueUniteEnseignement(interface.DomainService):

    @classmethod
    def verifier(
            cls,
            code_unite_enseignement: str,
            annee_unite_enseignement: int,
            matricule_fgs_enseignant: str,
            attribution_translator: 'IAttributionEnseignantTranslator'
    ) -> None:
        attributions = attribution_translator.search_attributions_enseignant(
            code_unite_enseignement=code_unite_enseignement,
            annee=annee_unite_enseignement,
        )
        est_attribue_unite_enseignement = any(
            attribution for attribution in attributions
            if attribution.matricule_fgs_enseignant == matricule_fgs_enseignant
            and attribution.code_unite_enseignement == code_unite_enseignement
            and attribution.annee == annee_unite_enseignement
        )
        if not est_attribue_unite_enseignement:
            raise EnseignantNonAttribueUniteEnseignementException(code_unite_enseignement)
