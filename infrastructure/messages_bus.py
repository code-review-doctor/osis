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
from typing import Dict, Callable, List

from ddd.logic.application.commands import ApplyOnVacantCourseCommand, UpdateApplicationCommand, \
    DeleteApplicationCommand, SearchApplicationByApplicantCommand, SearchVacantCoursesCommand, \
    RenewMultipleAttributionsCommand, GetAttributionsAboutToExpireCommand, SendApplicationsSummaryCommand, \
    GetChargeSummaryCommand
from ddd.logic.application.use_case.read.get_attributions_about_to_expire_service import \
    get_attributions_about_to_expire
from ddd.logic.application.use_case.read.get_charge_summary_service import get_charge_summary
from ddd.logic.application.use_case.read.search_applications_by_applicant_service import \
    search_applications_by_applicant
from ddd.logic.application.use_case.read.search_vacant_courses_service import search_vacant_courses
from ddd.logic.application.use_case.write.apply_on_vacant_course_service import apply_on_vacant_course
from ddd.logic.application.use_case.write.delete_application_service import delete_application
from ddd.logic.application.use_case.write.renew_multiple_attributions_service import renew_multiple_attributions
from ddd.logic.application.use_case.write.send_applications_summary import send_applications_summary
from ddd.logic.application.use_case.write.update_application_service import update_application
from ddd.logic.effective_class_repartition.commands import SearchAttributionsToLearningUnitCommand, \
    SearchTutorsDistributedToClassCommand, SearchAttributionCommand, DistributeClassToTutorCommand, \
    UnassignTutorClassCommand, EditClassVolumeRepartitionToTutorCommand, SearchClassesEnseignantCommand, \
    SearchAttributionsEnseignantCommand
from ddd.logic.effective_class_repartition.use_case.read.get_attribution_service import get_attribution
from ddd.logic.effective_class_repartition.use_case.read.search_attributions_enseignant_service import \
    search_attributions_enseignant
from ddd.logic.effective_class_repartition.use_case.read.search_attributions_to_learning_unit_service import \
    search_attributions_to_learning_unit
from ddd.logic.effective_class_repartition.use_case.read.search_classes_enseignant_service import \
    search_classes_enseignant
from ddd.logic.effective_class_repartition.use_case.read.search_effective_classes_distributed_service import \
    search_tutors_distributed_to_class
from ddd.logic.effective_class_repartition.use_case.write.distribute_class_to_tutor_service import \
    distribute_class_to_tutor
from ddd.logic.effective_class_repartition.use_case.write.edit_class_volume_repartition_to_tutor_service import \
    edit_class_volume_repartition_to_tutor
from ddd.logic.effective_class_repartition.use_case.write.unassign_tutor_class_service import unassign_tutor_class
from ddd.logic.encodage_des_notes.encodage.commands import GetFeuilleDeNotesGestionnaireCommand, EncoderNotesCommand, \
    GetCohortesGestionnaireCommand, RechercherNotesCommand, GetProgressionGeneraleGestionnaireCommand, \
    GetPeriodeEncodageCommand
from ddd.logic.encodage_des_notes.encodage.use_case.read.get_cohortes_gestionnaire import get_cohortes_gestionnaire
from ddd.logic.encodage_des_notes.encodage.use_case.read.get_feuille_de_notes_service import \
    get_feuille_de_notes_gestionnaire
from ddd.logic.encodage_des_notes.encodage.use_case.read.get_periode_encodage_service import get_periode_encodage
from ddd.logic.encodage_des_notes.encodage.use_case.read.get_progression_generale_encodage_service import \
    get_progression_generale_gestionnaire
from ddd.logic.encodage_des_notes.encodage.use_case.read.rechercher_notes_service import rechercher_notes
from ddd.logic.encodage_des_notes.encodage.use_case.write.encoder_notes_service import encoder_notes
from ddd.logic.encodage_des_notes.soumission.commands import EncoderNoteCommand, SoumettreNoteCommand, \
    GetAdresseFeuilleDeNotesServiceCommand, GetChoixEntitesAdresseFeuilleDeNotesCommand, \
    EncoderAdresseFeuilleDeNotesSpecifique, EncoderAdresseEntiteCommeAdresseFeuilleDeNotes, \
    EcraserAdresseFeuilleDeNotesPremiereAnneeDeBachelier
from ddd.logic.encodage_des_notes.soumission.commands import GetFeuilleDeNotesCommand, GetProgressionGeneraleCommand, \
    AssignerResponsableDeNotesCommand, \
    SearchAdressesFeuilleDeNotesCommand
from ddd.logic.encodage_des_notes.soumission.use_case.read.get_addresse_feuille_de_notes_service import \
    get_adresse_feuille_de_notes
from ddd.logic.encodage_des_notes.soumission.use_case.read.get_choix_entites_adresse_feuille_de_notes_service import \
    get_choix_entites_adresse_feuille_de_notes
from ddd.logic.encodage_des_notes.soumission.use_case.read.get_feuille_de_notes_service import get_feuille_de_notes
from ddd.logic.encodage_des_notes.soumission.use_case.read.get_progression_generale_encodage_service import \
    get_progression_generale
from ddd.logic.encodage_des_notes.soumission.use_case.read.search_donnees_administratives_feuille_de_notes_service \
    import \
    search_donnees_administratives_feuille_de_notes
from ddd.logic.encodage_des_notes.soumission.use_case.write.assigner_responsable_de_notes_service import \
    assigner_responsable_de_notes
from ddd.logic.encodage_des_notes.soumission.use_case.write\
    .ecraser_adresse_feuille_de_note_premiere_annee_de_bachelier_par_adresse_du_bachelier_service import \
    ecraser_adresse_feuille_de_note_premiere_annee_de_bachelier_par_adresse_du_bachelier
from ddd.logic.encodage_des_notes.soumission.use_case.write.encode_note_etudiant_service import \
    encoder_note_etudiant
from ddd.logic.encodage_des_notes.soumission.use_case.write \
    .encoder_adresse_entite_comme_adresse_feuille_de_notes_service import \
    encoder_adresse_entite_comme_adresse_feuille_de_notes
from ddd.logic.encodage_des_notes.soumission.use_case.write.encoder_adresse_feuille_de_notes_specifique_service import \
    encoder_adresse_feuille_de_notes_specifique
from ddd.logic.encodage_des_notes.soumission.use_case.write.soumettre_note_etudiant_service import \
    soumettre_note_etudiant
from ddd.logic.learning_unit.commands import CreateLearningUnitCommand, GetLearningUnitCommand, \
    CreateEffectiveClassCommand, CanCreateEffectiveClassCommand, GetEffectiveClassCommand, \
    UpdateEffectiveClassCommand, DeleteEffectiveClassCommand, CanDeleteEffectiveClassCommand, \
    GetEffectiveClassWarningsCommand, LearningUnitSearchCommand, SearchDetailClassesEffectivesCommand
from ddd.logic.learning_unit.use_case.read.check_can_create_class_service import check_can_create_effective_class
from ddd.logic.learning_unit.use_case.read.check_can_delete_class_service import check_can_delete_effective_class
from ddd.logic.learning_unit.use_case.read.get_effective_class_service import get_effective_class
from ddd.logic.learning_unit.use_case.read.get_effective_class_warnings_service import get_effective_class_warnings
from ddd.logic.learning_unit.use_case.read.get_learning_unit_service import get_learning_unit
from ddd.logic.learning_unit.use_case.read.search_detail_classes_effectives import search_detail_classes_effectives
from ddd.logic.learning_unit.use_case.read.search_learning_units_service import search_learning_units
from ddd.logic.learning_unit.use_case.write.create_effective_class_service import create_effective_class
from ddd.logic.learning_unit.use_case.write.create_learning_unit_service import create_learning_unit
from ddd.logic.learning_unit.use_case.write.delete_effective_class_service import delete_effective_class
from ddd.logic.learning_unit.use_case.write.update_effective_class_service import update_effective_class
from ddd.logic.shared_kernel.academic_year.commands import SearchAcademicYearCommand
from ddd.logic.shared_kernel.academic_year.use_case.read.search_academic_years_service import search_academic_years
from ddd.logic.shared_kernel.campus.commands import SearchUclouvainCampusesCommand, GetCampusCommand
from ddd.logic.shared_kernel.campus.use_case.read.get_campus_service import get_campus
from ddd.logic.shared_kernel.campus.use_case.read.search_uclouvain_campuses_service import search_uclouvain_campuses
from ddd.logic.shared_kernel.language.commands import SearchLanguagesCommand, GetLanguageCommand
from ddd.logic.shared_kernel.language.use_case.read.get_language_service import get_language
from ddd.logic.shared_kernel.language.use_case.read.search_languages_service import search_languages
from infrastructure.application.repository.applicant import ApplicantRepository
from infrastructure.application.repository.application import ApplicationRepository
from infrastructure.application.repository.application_calendar import ApplicationCalendarRepository
from infrastructure.application.repository.vacant_course import VacantCourseRepository
from infrastructure.application.services.applications_summary import ApplicationsMailSummary
from infrastructure.application.services.learning_unit_service import LearningUnitTranslator
from infrastructure.effective_class_repartition.domain.service.tutor_attribution import \
    TutorAttributionToLearningUnitTranslator
from infrastructure.effective_class_repartition.repository.tutor import TutorRepository
from infrastructure.encodage_de_notes.encodage.domain.service.cohortes_du_gestionnaire import \
    CohortesDuGestionnaireTranslator
from infrastructure.encodage_de_notes.encodage.repository.note_etudiant import NoteEtudiantRepository as \
    NoteEtudiantGestionnaireRepository
from infrastructure.encodage_de_notes.shared_kernel.service.attribution_enseignant import \
    AttributionEnseignantTranslator
from infrastructure.encodage_de_notes.shared_kernel.service.inscription_examen import InscriptionExamenTranslator
from infrastructure.encodage_de_notes.shared_kernel.service.periode_encodage_notes import \
    PeriodeEncodageNotesTranslator
from infrastructure.encodage_de_notes.shared_kernel.service.signaletique_etudiant import \
    SignaletiqueEtudiantTranslator
from infrastructure.encodage_de_notes.shared_kernel.service.unite_enseignement import UniteEnseignementTranslator
from infrastructure.encodage_de_notes.soumission.domain.service.deliberation import DeliberationTranslator
from infrastructure.encodage_de_notes.soumission.domain.service.entites_cohorte import EntitesCohorteTranslator
from infrastructure.encodage_de_notes.soumission.domain.service.signaletique_personne import \
    SignaletiquePersonneTranslator
from infrastructure.encodage_de_notes.soumission.repository.adresse_feuille_de_notes import \
    AdresseFeuilleDeNotesRepository
from infrastructure.encodage_de_notes.soumission.repository.note_etudiant import NoteEtudiantRepository
from infrastructure.encodage_de_notes.soumission.repository.responsable_de_notes import ResponsableDeNotesRepository
from infrastructure.learning_unit.domain.service.student_enrollments_to_effective_class import \
    StudentEnrollmentsTranslator
from infrastructure.learning_unit.domain.service.tutor_distributed_to_class import TutorAssignedToClassTranslator
from infrastructure.learning_unit.repository.effective_class import EffectiveClassRepository
from infrastructure.learning_unit.repository.entity import UclEntityRepository
from infrastructure.learning_unit.repository.learning_unit import LearningUnitRepository
from infrastructure.shared_kernel.academic_year.repository.academic_year import AcademicYearRepository
from infrastructure.shared_kernel.campus.repository.uclouvain_campus import UclouvainCampusRepository
from infrastructure.shared_kernel.entite.repository.entiteucl import EntiteUCLRepository
from infrastructure.shared_kernel.language.repository.language import LanguageRepository
from osis_common.ddd.interface import CommandRequest, ApplicationServiceResult
from program_management.ddd.command import BulkUpdateLinkCommand, GetReportCommand
from program_management.ddd.repositories import program_tree as program_tree_repo
from program_management.ddd.repositories.report import ReportRepository
from program_management.ddd.service.read.get_report_service import get_report
from program_management.ddd.service.write.bulk_update_link_service import bulk_update_and_postpone_links


class MessageBus:
    command_handlers = {
        CreateLearningUnitCommand: lambda cmd: create_learning_unit(
            cmd, LearningUnitRepository(), UclEntityRepository()
        ),
        SearchLanguagesCommand: lambda cmd: search_languages(cmd, LanguageRepository()),
        SearchAcademicYearCommand: lambda cmd: search_academic_years(cmd, AcademicYearRepository()),
        GetReportCommand: lambda cmd: get_report(cmd),
        BulkUpdateLinkCommand: lambda cmd: bulk_update_and_postpone_links(
            cmd, program_tree_repo.ProgramTreeRepository(), ReportRepository()
        ),
        GetLearningUnitCommand: lambda cmd: get_learning_unit(cmd, LearningUnitRepository()),
        LearningUnitSearchCommand: lambda cmd: search_learning_units(cmd, LearningUnitRepository()),
        CreateEffectiveClassCommand: lambda cmd: create_effective_class(
            cmd, LearningUnitRepository(), EffectiveClassRepository(), StudentEnrollmentsTranslator()
        ),
        CanCreateEffectiveClassCommand: lambda cmd: check_can_create_effective_class(
            cmd, LearningUnitRepository(), StudentEnrollmentsTranslator()
        ),
        SearchUclouvainCampusesCommand: lambda cmd: search_uclouvain_campuses(cmd, UclouvainCampusRepository()),
        GetEffectiveClassCommand: lambda cmd: get_effective_class(cmd, EffectiveClassRepository()),
        SearchAttributionsToLearningUnitCommand: lambda cmd: search_attributions_to_learning_unit(
            cmd,
            TutorAttributionToLearningUnitTranslator(),
        ),
        SearchAttributionsEnseignantCommand: lambda cmd: search_attributions_enseignant(
            cmd,
            TutorAttributionToLearningUnitTranslator(),
        ),
        UpdateEffectiveClassCommand: lambda cmd: update_effective_class(
            cmd,
            LearningUnitRepository(),
            EffectiveClassRepository()
        ),
        GetLanguageCommand: lambda cmd: get_language(cmd, LanguageRepository()),
        GetCampusCommand: lambda cmd: get_campus(cmd, UclouvainCampusRepository()),
        DeleteEffectiveClassCommand: lambda cmd: delete_effective_class(
            cmd,
            EffectiveClassRepository(),
            TutorAssignedToClassTranslator(),
            StudentEnrollmentsTranslator(),
        ),
        CanDeleteEffectiveClassCommand: lambda cmd: check_can_delete_effective_class(
            cmd,
            EffectiveClassRepository(),
            TutorAssignedToClassTranslator(),
            StudentEnrollmentsTranslator(),
        ),
        GetEffectiveClassWarningsCommand: lambda cmd: get_effective_class_warnings(
            cmd, EffectiveClassRepository(), LearningUnitRepository()
        ),
        SearchTutorsDistributedToClassCommand: lambda cmd: search_tutors_distributed_to_class(
            cmd,
            TutorAttributionToLearningUnitTranslator(),
            TutorRepository(),
        ),
        SearchClassesEnseignantCommand: lambda cmd: search_classes_enseignant(
            cmd,
            TutorAttributionToLearningUnitTranslator(),
            TutorRepository(),
        ),
        ApplyOnVacantCourseCommand: lambda cmd: apply_on_vacant_course(
            cmd, ApplicationRepository(), ApplicationCalendarRepository(),
            ApplicantRepository(), VacantCourseRepository()
        ),
        UpdateApplicationCommand: lambda cmd: update_application(
            cmd, ApplicationRepository(), VacantCourseRepository()
        ),
        RenewMultipleAttributionsCommand: lambda cmd: renew_multiple_attributions(
            cmd, ApplicationRepository(), ApplicationCalendarRepository(),
            ApplicantRepository(), VacantCourseRepository()
        ),
        DeleteApplicationCommand: lambda cmd: delete_application(cmd, ApplicationRepository()),
        SearchApplicationByApplicantCommand: lambda cmd: search_applications_by_applicant(
            cmd, ApplicationRepository(), ApplicationCalendarRepository()
        ),
        SearchVacantCoursesCommand: lambda cmd: search_vacant_courses(
            cmd, ApplicationCalendarRepository(), VacantCourseRepository(), LearningUnitTranslator()
        ),
        GetChargeSummaryCommand: lambda cmd: get_charge_summary(
            cmd, ApplicationCalendarRepository(), ApplicantRepository(), VacantCourseRepository(),
            LearningUnitTranslator()
        ),
        GetAttributionsAboutToExpireCommand: lambda cmd: get_attributions_about_to_expire(
            cmd, ApplicationRepository(), ApplicationCalendarRepository(),
            ApplicantRepository(), VacantCourseRepository(), LearningUnitTranslator()
        ),
        SendApplicationsSummaryCommand: lambda cmd: send_applications_summary(
            cmd, ApplicationRepository(), ApplicationCalendarRepository(), ApplicantRepository(),
            ApplicationsMailSummary()
        ),
        SearchAttributionCommand: lambda cmd: get_attribution(cmd, TutorAttributionToLearningUnitTranslator()),
        DistributeClassToTutorCommand: lambda cmd: distribute_class_to_tutor(
            cmd,
            TutorRepository(),
            EffectiveClassRepository(),
        ),
        SearchDetailClassesEffectivesCommand: lambda cmd: search_detail_classes_effectives(
            cmd,
            EffectiveClassRepository(),
        ),
        UnassignTutorClassCommand: lambda cmd: unassign_tutor_class(cmd, TutorRepository()),
        EditClassVolumeRepartitionToTutorCommand: lambda cmd: edit_class_volume_repartition_to_tutor(
            cmd,
            TutorRepository(),
            EffectiveClassRepository()
        ),
        GetFeuilleDeNotesCommand: lambda cmd: get_feuille_de_notes(
            cmd,
            NoteEtudiantRepository(),
            ResponsableDeNotesRepository(),
            SignaletiquePersonneTranslator(),
            PeriodeEncodageNotesTranslator(),
            InscriptionExamenTranslator(),
            SignaletiqueEtudiantTranslator(),
            AttributionEnseignantTranslator(),
            UniteEnseignementTranslator(),
        ),
        EncoderNoteCommand: lambda cmd: encoder_note_etudiant(
            cmd,
            NoteEtudiantRepository(),
            PeriodeEncodageNotesTranslator(),
            AttributionEnseignantTranslator(),
        ),
        SoumettreNoteCommand: lambda cmd: soumettre_note_etudiant(
            cmd,
            NoteEtudiantRepository(),
            ResponsableDeNotesRepository(),
            PeriodeEncodageNotesTranslator(),
        ),
        GetProgressionGeneraleCommand: lambda cmd: get_progression_generale(
            cmd,
            NoteEtudiantRepository(),
            ResponsableDeNotesRepository(),
            PeriodeEncodageNotesTranslator(),
            SignaletiqueEtudiantTranslator(),
            AttributionEnseignantTranslator(),
            UniteEnseignementTranslator(),
        ),
        AssignerResponsableDeNotesCommand: lambda cmd: assigner_responsable_de_notes(
            cmd,
            ResponsableDeNotesRepository(),
            AttributionEnseignantTranslator()
        ),
        GetFeuilleDeNotesGestionnaireCommand: lambda cmd: get_feuille_de_notes_gestionnaire(
            cmd,
            NoteEtudiantRepository(),
            ResponsableDeNotesRepository(),
            SignaletiquePersonneTranslator(),  # TODO :: merger avec signaletique etudiant ?
            PeriodeEncodageNotesTranslator(),
            InscriptionExamenTranslator(),
            SignaletiqueEtudiantTranslator(),
            AttributionEnseignantTranslator(),
            UniteEnseignementTranslator(),
            CohortesDuGestionnaireTranslator(),
        ),
        SearchAdressesFeuilleDeNotesCommand: lambda cmd: search_donnees_administratives_feuille_de_notes(
            cmd,
            PeriodeEncodageNotesTranslator(),
            InscriptionExamenTranslator(),
            DeliberationTranslator(),
            AdresseFeuilleDeNotesRepository(),
        ),
        EncoderNotesCommand: lambda cmd: encoder_notes(
            cmd,
            NoteEtudiantGestionnaireRepository(),
            PeriodeEncodageNotesTranslator(),
            CohortesDuGestionnaireTranslator(),
        ),
        GetCohortesGestionnaireCommand: lambda cmd: get_cohortes_gestionnaire(
            cmd,
            CohortesDuGestionnaireTranslator()
        ),
        RechercherNotesCommand: lambda cmd: rechercher_notes(
            cmd,
            NoteEtudiantGestionnaireRepository(),
            PeriodeEncodageNotesTranslator(),
            CohortesDuGestionnaireTranslator(),
            SignaletiqueEtudiantTranslator(),
        ),
        GetProgressionGeneraleGestionnaireCommand: lambda cmd: get_progression_generale_gestionnaire(
            cmd,
            NoteEtudiantGestionnaireRepository(),
            NoteEtudiantRepository(),
            ResponsableDeNotesRepository(),
            PeriodeEncodageNotesTranslator(),
            SignaletiqueEtudiantTranslator(),
            UniteEnseignementTranslator(),
            CohortesDuGestionnaireTranslator(),
        ),
        GetPeriodeEncodageCommand: lambda cmd: get_periode_encodage(
            cmd,
            PeriodeEncodageNotesTranslator(),
        ),
        EncoderAdresseEntiteCommeAdresseFeuilleDeNotes: lambda cmd:
            encoder_adresse_entite_comme_adresse_feuille_de_notes(
                cmd,
                AdresseFeuilleDeNotesRepository(),
                EntiteUCLRepository(),
                EntitesCohorteTranslator()
        ),
        EncoderAdresseFeuilleDeNotesSpecifique: lambda cmd: encoder_adresse_feuille_de_notes_specifique(
            cmd,
            AdresseFeuilleDeNotesRepository(),
        ),
        EcraserAdresseFeuilleDeNotesPremiereAnneeDeBachelier: lambda cmd:
            ecraser_adresse_feuille_de_note_premiere_annee_de_bachelier_par_adresse_du_bachelier(
                cmd,
                AdresseFeuilleDeNotesRepository(),
        ),
        GetAdresseFeuilleDeNotesServiceCommand: lambda cmd: get_adresse_feuille_de_notes(
            cmd,
            AdresseFeuilleDeNotesRepository(),
        ),
        GetChoixEntitesAdresseFeuilleDeNotesCommand: lambda cmd: get_choix_entites_adresse_feuille_de_notes(
            cmd,
            EntiteUCLRepository(),
            EntitesCohorteTranslator()
        )
    }  # type: Dict[CommandRequest, Callable[[CommandRequest], ApplicationServiceResult]]

    def invoke(self, command: CommandRequest) -> ApplicationServiceResult:
        return self.command_handlers[command.__class__](command)

    def invoke_multiple(self, commands: List['CommandRequest']) -> List[ApplicationServiceResult]:
        return [self.invoke(command) for command in commands]


message_bus_instance = MessageBus()
