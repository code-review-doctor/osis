# ##############################################################################
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
# ##############################################################################
from typing import List, Optional

from admission.contrib.models import DoctorateAdmission
from base.models.education_group_year import EducationGroupYear
from base.models.person import Person
from ddd.logic.admission.preparation.projet_doctoral.builder.proposition_identity_builder import \
    PropositionIdentityBuilder
from ddd.logic.admission.preparation.projet_doctoral.domain.model._detail_projet import DetailProjet
from ddd.logic.admission.preparation.projet_doctoral.domain.model._experience_precedente_recherche import (
    ChoixDoctoratDejaRealise,
    ExperiencePrecedenteRecherche,
)
from ddd.logic.admission.preparation.projet_doctoral.domain.model._financement import ChoixTypeFinancement, Financement
from ddd.logic.admission.preparation.projet_doctoral.domain.model.doctorat import DoctoratIdentity
from ddd.logic.admission.preparation.projet_doctoral.domain.model.proposition import (
    Proposition,
    PropositionIdentity,
)
from ddd.logic.admission.preparation.projet_doctoral.domain.model._enums import (
    ChoixStatusProposition,
    ChoixTypeAdmission,
)
from ddd.logic.admission.preparation.projet_doctoral.dtos import PropositionDTO, PropositionSearchDTO
from ddd.logic.admission.preparation.projet_doctoral.repository.i_proposition import IPropositionRepository
from infrastructure.admission.preparation.projet_doctoral.domain.service.doctorat import DoctoratTranslator
from infrastructure.admission.preparation.projet_doctoral.domain.service.secteur_ucl import SecteurUclTranslator
from osis_common.ddd.interface import ApplicationService


def _instantiate_admission(admission: DoctorateAdmission) -> Proposition:
    return Proposition(
        entity_id=PropositionIdentityBuilder().build_from_uuid(admission.uuid),
        type_admission=ChoixTypeAdmission[admission.type],
        doctorat_id=DoctoratIdentity(admission.doctorate.acronym, admission.doctorate.academic_year.year),
        matricule_candidat=admission.candidate.global_id,
        projet=DetailProjet(
            titre=admission.project_title,
            resume=admission.project_abstract,
            documents=admission.project_document,
            langue_redaction_these=admission.thesis_language,
            graphe_gantt=admission.gantt_graph,
            proposition_programme_doctoral=admission.program_proposition,
            projet_formation_complementaire=admission.additional_training_project,
        ),
        justification=admission.comment,
        status=ChoixStatusProposition.IN_PROGRESS,
        financement=Financement(
            type=ChoixTypeFinancement[admission.financing_type] if admission.financing_type else '',
            type_contrat_travail=admission.financing_work_contract,
            eft=admission.financing_eft,
            bourse_recherche=admission.scholarship_grant,
            duree_prevue=admission.planned_duration,
            temps_consacre=admission.dedicated_time,
        ),
        experience_precedente_recherche=ExperiencePrecedenteRecherche(
            doctorat_deja_realise=ChoixDoctoratDejaRealise[admission.phd_already_done],
            institution=admission.phd_already_done_institution,
            date_soutenance=admission.phd_already_done_defense_date,
            raison_non_soutenue=admission.phd_already_done_no_defense_reason,
        ),
    )


def _instantiate_admission_dto(admission: DoctorateAdmission) -> PropositionSearchDTO:
    doctorat = DoctoratTranslator().search(admission.doctorate.acronym, 2020)[0]
    secteur = SecteurUclTranslator().get(doctorat.sigle_entite_gestion)
    return PropositionSearchDTO(
        uuid=admission.uuid,
        type_admission=admission.type,
        sigle_doctorat=doctorat.sigle,
        matricule_candidat=admission.candidate.global_id,
        code_secteur_formation=secteur.sigle,
        bureau_CDE=admission.bureau,
        intitule_doctorat_en=doctorat.intitule_en,
        intitule_doctorat_fr=doctorat.intitule_fr,
        created_at=admission.created,
    )


def load_admissions(matricule) -> List['Proposition']:
    qs = DoctorateAdmission.objects.filter(candidate__global_id=matricule)

    return [_instantiate_admission(a) for a in qs]


def search_admissions(matricule) -> List['PropositionSearchDTO']:
    qs = DoctorateAdmission.objects.filter(candidate__global_id=matricule)

    return [_instantiate_admission_dto(a) for a in qs]


class PropositionRepository(IPropositionRepository):
    @classmethod
    def get_dto(cls, uuid_proposition: str) -> 'PropositionDTO':
        raise NotImplementedError

    @classmethod
    def get(cls, entity_id: 'PropositionIdentity') -> 'Proposition':
        return _instantiate_admission(DoctorateAdmission.objects.get(uuid=entity_id.uuid))

    @classmethod
    def search(cls, entity_ids: Optional[List['PropositionIdentity']] = None, matricule_candidat: str = None,
               **kwargs) -> List['Proposition']:
        if matricule_candidat is not None:
            return load_admissions(matricule_candidat)
        return []

    @classmethod
    def search_dto(cls, matricule_candidat: str = None, **kwargs) -> List['PropositionSearchDTO']:
        if matricule_candidat is not None:
            return search_admissions(matricule_candidat)
        return []

    @classmethod
    def delete(cls, entity_id: 'PropositionIdentity', **kwargs: ApplicationService) -> None:
        raise NotImplementedError

    @classmethod
    def save(cls, entity: 'Proposition') -> None:
        doctorate = EducationGroupYear.objects.get(
            acronym=entity.sigle_formation,
            academic_year__year=entity.annee,
        )
        DoctorateAdmission.objects.update_or_create(
            uuid=entity.entity_id.uuid,
            defaults={
                'type': entity.type_admission.name,
                'comment': entity.justification,
                'candidate': Person.objects.get(global_id=entity.matricule_candidat),
                'bureau': entity.bureau_CDE or '',
                'doctorate': doctorate,
                'financing_type': entity.financement.type.name,
                'financing_work_contract': entity.financement.type_contrat_travail,
                'financing_eft': entity.financement.eft,
                'scholarship_grant': entity.financement.bourse_recherche,
                'planned_duration': entity.financement.duree_prevue,
                'dedicated_time': entity.financement.temps_consacre,
                'project_title': entity.projet.titre,
                'project_abstract': entity.projet.resume,
                'thesis_language': entity.projet.langue_redaction_these,
                'project_document': entity.projet.documents,
                'gantt_graph': entity.projet.graphe_gantt,
                'program_proposition': entity.projet.proposition_programme_doctoral,
                'additional_training_project': entity.projet.projet_formation_complementaire,
                'phd_already_done': entity.experience_precedente_recherche.doctorat_deja_realise.name,
                'phd_already_done_institution': entity.experience_precedente_recherche.institution,
                'phd_already_done_defense_date': entity.experience_precedente_recherche.date_soutenance,
                'phd_already_done_no_defense_reason': entity.experience_precedente_recherche.raison_non_soutenue,
            }
        )
