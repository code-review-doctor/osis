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
from ddd.logic.admission.preparation.projet_doctoral.builder.proposition_identity_builder import \
    PropositionIdentityBuilder
from ddd.logic.admission.preparation.projet_doctoral.domain.service.i_doctorat import IDoctoratTranslator
from ddd.logic.admission.preparation.projet_doctoral.domain.service.i_secteur_ucl import ISecteurUclTranslator
from ddd.logic.admission.preparation.projet_doctoral.dtos import PropositionDTO
from ddd.logic.admission.preparation.projet_doctoral.repository.i_proposition import IPropositionRepository
from osis_common.ddd import interface


class PropositionDto(interface.DomainService):
    @classmethod
    def get(
            cls,
            uuid_proposition: str,
            repository: 'IPropositionRepository',
            doctorat_translator: 'IDoctoratTranslator',
            secteur_ucl_translator: 'ISecteurUclTranslator',
    ) -> 'PropositionDTO':
        proposition = repository.get(PropositionIdentityBuilder.build_from_uuid(uuid_proposition))
        doctorat = doctorat_translator.get_dto(proposition.doctorat_id.sigle, proposition.doctorat_id.annee)
        return PropositionDTO(
            type_admission=proposition.type_admission.name,
            sigle_doctorat=proposition.doctorat_id.sigle,
            annee_doctorat=proposition.doctorat_id.annee,
            intitule_doctorat_fr=doctorat.intitule_fr,
            intitule_doctorat_en=doctorat.intitule_en,
            matricule_candidat=proposition.matricule_candidat,
            justification=proposition.justification,
            code_secteur_formation=secteur_ucl_translator.get(doctorat.sigle_entite_gestion).sigle,
            bureau_CDE=proposition.bureau_CDE and proposition.bureau_CDE.name,
            type_financement=proposition.financement.type and proposition.financement.type.name,
            type_contrat_travail=proposition.financement.type_contrat_travail,
            eft=proposition.financement.eft,
            bourse_recherche=proposition.financement.bourse_recherche,
            duree_prevue=proposition.financement.duree_prevue,
            temps_consacre=proposition.financement.temps_consacre,
            titre_projet=proposition.projet.titre,
            resume_projet=proposition.projet.resume,
            documents_projet=proposition.projet.documents,
            graphe_gantt=proposition.projet.graphe_gantt,
            proposition_programme_doctoral=proposition.projet.proposition_programme_doctoral,
            projet_formation_complementaire=proposition.projet.projet_formation_complementaire,
            langue_redaction_these=proposition.projet.langue_redaction_these,
            doctorat_deja_realise=proposition.experience_precedente_recherche.doctorat_deja_realise.name,
            institution=proposition.experience_precedente_recherche.institution,
            date_soutenance=proposition.experience_precedente_recherche.date_soutenance,
            raison_non_soutenue=proposition.experience_precedente_recherche.raison_non_soutenue,
        )
