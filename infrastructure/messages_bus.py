##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2022 Université catholique de Louvain (http://www.uclouvain.be)
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
from typing import Callable, Dict

from ddd.logic.application.commands import (
    ApplyOnVacantCourseCommand,
    DeleteApplicationCommand,
    GetAttributionsAboutToExpireCommand,
    GetChargeSummaryCommand,
    RenewMultipleAttributionsCommand,
    SearchApplicationByApplicantCommand,
    SearchVacantCoursesCommand,
    SendApplicationsSummaryCommand,
    UpdateApplicationCommand,
    SendAttributionEndDateReachedSummaryCommand,
)
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
from ddd.logic.application.use_case.write.send_attribution_end_date_reached_summary import \
    send_emails_to_teachers_with_ending_attributions
from ddd.logic.application.use_case.write.update_application_service import update_application
from ddd.logic.effective_class_repartition.commands import (
    DistributeClassToTutorCommand,
    EditClassVolumeRepartitionToTutorCommand,
    GetTutorRepartitionClassesCommand,
    SearchAttributionCommand,
    SearchAttributionsEnseignantCommand,
    SearchAttributionsToLearningUnitCommand,
    SearchClassesEnseignantCommand,
    SearchTutorsDistributedToClassCommand,
    UnassignTutorClassCommand, SearchClassesParNomEnseignantCommand,
)
from ddd.logic.effective_class_repartition.use_case.read.get_attribution_service import get_attribution
from ddd.logic.effective_class_repartition.use_case.read.get_tutor_repartition_classes_service import \
    get_tutor_repartition_classes
from ddd.logic.effective_class_repartition.use_case.read.search_attributions_enseignant_service import \
    search_attributions_enseignant
from ddd.logic.effective_class_repartition.use_case.read.search_attributions_to_learning_unit_service import \
    search_attributions_to_learning_unit
from ddd.logic.effective_class_repartition.use_case.read.search_classes_enseignant_service import \
    search_classes_enseignant
from ddd.logic.effective_class_repartition.use_case.read.search_classes_par_nom_enseignant_service import \
    search_classes_par_nom_prenom
from ddd.logic.effective_class_repartition.use_case.read.search_effective_classes_distributed_service import \
    search_tutors_distributed_to_class
from ddd.logic.effective_class_repartition.use_case.write.distribute_class_to_tutor_service import \
    distribute_class_to_tutor
from ddd.logic.effective_class_repartition.use_case.write.edit_class_volume_repartition_to_tutor_service import \
    edit_class_volume_repartition_to_tutor
from ddd.logic.effective_class_repartition.use_case.write.unassign_tutor_class_service import unassign_tutor_class
from ddd.logic.encodage_des_notes.encodage.commands import (
    EncoderNotesCommand,
    GetCohortesGestionnaireCommand,
    GetFeuilleDeNotesGestionnaireCommand,
    GetPeriodeEncodageCommand,
    GetProgressionGeneraleGestionnaireCommand,
    RechercherNotesCommand, SearchEnseignantsCommand,
)
from ddd.logic.encodage_des_notes.encodage.use_case.read.get_cohortes_gestionnaire import get_cohortes_gestionnaire
from ddd.logic.encodage_des_notes.encodage.use_case.read.get_feuille_de_notes_service import \
    get_feuille_de_notes_gestionnaire
from ddd.logic.encodage_des_notes.encodage.use_case.read.get_periode_encodage_service import get_periode_encodage
from ddd.logic.encodage_des_notes.encodage.use_case.read.get_progression_generale_encodage_service import \
    get_progression_generale_gestionnaire
from ddd.logic.encodage_des_notes.encodage.use_case.read.rechercher_enseignants import rechercher_enseignants
from ddd.logic.encodage_des_notes.encodage.use_case.read.rechercher_notes_service import rechercher_notes
from ddd.logic.encodage_des_notes.encodage.use_case.write.encoder_notes_service import encoder_notes
from ddd.logic.encodage_des_notes.shared_kernel.commands import GetEncoderNotesRapportCommand
from ddd.logic.encodage_des_notes.shared_kernel.use_case.read.get_encoder_notes_rapport_service import \
    get_encoder_notes_rapport
from ddd.logic.encodage_des_notes.soumission.commands import (
    AssignerResponsableDeNotesCommand,
    SupprimerAdresseFeuilleDeNotesPremiereAnneeDeBachelier,
    EncoderAdresseEntiteCommeAdresseFeuilleDeNotes,
    EncoderAdresseFeuilleDeNotesSpecifique,
    EncoderNotesEtudiantCommand,
    GetAdresseFeuilleDeNotesServiceCommand,
    GetChoixEntitesAdresseFeuilleDeNotesCommand,
    GetFeuilleDeNotesCommand,
    GetProgressionGeneraleCommand,
    GetResponsableDeNotesCommand,
    SearchAdressesFeuilleDeNotesCommand,
    SoumettreNotesCommand, SearchResponsableDeNotesCommand,
)
from ddd.logic.encodage_des_notes.soumission.use_case.read.get_addresse_feuille_de_notes_service import \
    get_adresse_feuille_de_notes
from ddd.logic.encodage_des_notes.soumission.use_case.read.get_choix_entites_adresse_feuille_de_notes_service import \
    get_choix_entites_adresse_feuille_de_notes
from ddd.logic.encodage_des_notes.soumission.use_case.read.get_feuille_de_notes_service import get_feuille_de_notes
from ddd.logic.encodage_des_notes.soumission.use_case.read.get_progression_generale_encodage_service import \
    get_progression_generale
from ddd.logic.encodage_des_notes.soumission.use_case.read.get_responsable_de_notes_service import \
    get_responsable_de_notes
from ddd.logic.encodage_des_notes.soumission.use_case.read.search_donnees_administratives_feuille_de_notes_service \
    import \
    search_donnees_administratives_feuille_de_notes
from ddd.logic.encodage_des_notes.soumission.use_case.read.search_responsable_de_notes_service import \
    search_responsables_de_notes
from ddd.logic.encodage_des_notes.soumission.use_case.write.assigner_responsable_de_notes_service import \
    assigner_responsable_de_notes
from ddd.logic.encodage_des_notes.soumission.use_case.write \
    .encoder_adresse_entite_comme_adresse_feuille_de_notes_service import \
    encoder_adresse_entite_comme_adresse_feuille_de_notes
from ddd.logic.encodage_des_notes.soumission.use_case.write.encoder_adresse_feuille_de_notes_specifique_service import \
    encoder_adresse_feuille_de_notes_specifique
from ddd.logic.encodage_des_notes.soumission.use_case.write.encoder_notes_etudiant_service import encoder_notes_etudiant
from ddd.logic.encodage_des_notes.soumission.use_case.write.soumettre_notes_etudiant_service import \
    soumettre_notes_etudiant
from ddd.logic.encodage_des_notes.soumission.use_case.write \
    .supprimer_adresse_feuille_de_note_premiere_annee_de_bachelier import \
    supprimer_adresse_feuille_de_note_premiere_annee_de_bachelier
from ddd.logic.formation_catalogue.commands import SearchFormationsCommand
from ddd.logic.formation_catalogue.use_case.read.search_formation_service import search_formations
from ddd.logic.learning_unit.commands import (
    CanCreateEffectiveClassCommand,
    CanDeleteEffectiveClassCommand,
    CreateEffectiveClassCommand,
    CreateLearningUnitCommand,
    DeleteEffectiveClassCommand,
    GetClassesEffectivesDepuisUniteDEnseignementCommand,
    GetEffectiveClassCommand,
    GetEffectiveClassWarningsCommand,
    GetLearningUnitCommand,
    LearningUnitSearchCommand,
    SearchDetailClassesEffectivesCommand,
    UpdateEffectiveClassCommand,
)
from ddd.logic.learning_unit.use_case.read.check_can_create_class_service import check_can_create_effective_class
from ddd.logic.learning_unit.use_case.read.check_can_delete_class_service import check_can_delete_effective_class
from ddd.logic.learning_unit.use_case.read.get_effective_class_service import get_effective_class
from ddd.logic.learning_unit.use_case.read.get_effective_class_warnings_service import get_effective_class_warnings
from ddd.logic.learning_unit.use_case.read.get_learning_unit_effective_classes_service import \
    get_learning_unit_effective_classes
from ddd.logic.learning_unit.use_case.read.get_learning_unit_service import get_learning_unit
from ddd.logic.learning_unit.use_case.read.search_detail_classes_effectives import search_detail_classes_effectives
from ddd.logic.learning_unit.use_case.read.search_learning_units_service import search_learning_units
from ddd.logic.learning_unit.use_case.write.create_effective_class_service import create_effective_class
from ddd.logic.learning_unit.use_case.write.create_learning_unit_service import create_learning_unit
from ddd.logic.learning_unit.use_case.write.delete_effective_class_service import delete_effective_class
from ddd.logic.learning_unit.use_case.write.update_effective_class_service import update_effective_class
from ddd.logic.preparation_programme_annuel_etudiant.commands import AjouterUEAuProgrammeCommand
from ddd.logic.preparation_programme_annuel_etudiant.commands import GetFormulaireInscriptionCoursCommand, \
    GetFormationCommand
from ddd.logic.preparation_programme_annuel_etudiant.commands import GetProgrammeInscriptionCoursCommand
from ddd.logic.preparation_programme_annuel_etudiant.use_case.read.get_formulaire_inscription_cours_service import \
    get_formulaire_inscription_cours_service
from ddd.logic.preparation_programme_annuel_etudiant.use_case.read.get_programme_inscription_cours_service import \
    get_programme_inscription_cours
from ddd.logic.preparation_programme_annuel_etudiant.use_case.write.ajouter_UE_au_programme_service import \
    ajouter_UE_au_programme
from ddd.logic.shared_kernel.academic_year.commands import SearchAcademicYearCommand
from ddd.logic.shared_kernel.academic_year.use_case.read.search_academic_years_service import search_academic_years
from ddd.logic.shared_kernel.campus.commands import GetCampusCommand, SearchUclouvainCampusesCommand
from ddd.logic.shared_kernel.campus.use_case.read.get_campus_service import get_campus
from ddd.logic.shared_kernel.campus.use_case.read.search_uclouvain_campuses_service import search_uclouvain_campuses
from ddd.logic.shared_kernel.language.commands import GetLanguageCommand, SearchLanguagesCommand
from ddd.logic.shared_kernel.language.use_case.read.get_language_service import get_language
from ddd.logic.shared_kernel.language.use_case.read.search_languages_service import search_languages
from education_group.ddd.repository.training import TrainingRepository
from infrastructure.application.repository.applicant import ApplicantRepository
from infrastructure.application.repository.application import ApplicationRepository
from infrastructure.application.repository.application_calendar import ApplicationCalendarRepository
from infrastructure.application.repository.vacant_course import VacantCourseRepository
from infrastructure.application.services.applications_summary import ApplicationsMailSummary
from infrastructure.application.services.attribution_end_date_reached_summary import AttributionsEndDateReachedSummary
from infrastructure.application.services.learning_unit_service import LearningUnitTranslator
from infrastructure.effective_class_repartition.domain.service.tutor_attribution import \
    TutorAttributionToLearningUnitTranslator
from infrastructure.effective_class_repartition.repository.tutor import TutorRepository
from infrastructure.encodage_de_notes.encodage.domain.service.cohortes_du_gestionnaire import \
    CohortesDuGestionnaireTranslator
from infrastructure.encodage_de_notes.encodage.domain.service.historiser_notes import HistoriserEncodageNotesService
from infrastructure.encodage_de_notes.encodage.domain.service.notifier_encodage_notes import NotifierEncodageNotes
from infrastructure.encodage_de_notes.encodage.repository.note_etudiant import NoteEtudiantRepository as \
    NoteEtudiantGestionnaireRepository
from infrastructure.encodage_de_notes.shared_kernel.repository.encoder_notes_rapport import \
    EncoderNotesRapportRepository
from infrastructure.encodage_de_notes.shared_kernel.service.attribution_enseignant import \
    AttributionEnseignantTranslator
from infrastructure.encodage_de_notes.shared_kernel.service.inscription_examen import InscriptionExamenTranslator
from infrastructure.encodage_de_notes.shared_kernel.service.periode_encodage_notes import \
    PeriodeEncodageNotesTranslator
from infrastructure.encodage_de_notes.shared_kernel.service.signaletique_etudiant import \
    SignaletiqueEtudiantTranslator
from infrastructure.encodage_de_notes.shared_kernel.service.unite_enseignement import UniteEnseignementTranslator
from infrastructure.encodage_de_notes.soumission.domain.service.entites_cohorte import EntitesCohorteTranslator
from infrastructure.encodage_de_notes.soumission.domain.service.historiser_notes import HistoriserNotesService
from infrastructure.encodage_de_notes.soumission.domain.service.notifier_soumission_notes import NotifierSoumissionNotes
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
from infrastructure.preparation_programme_annuel_etudiant.domain.service.catalogue_formations import \
    CatalogueFormationsTranslator
from infrastructure.preparation_programme_annuel_etudiant.domain.service.catalogue_unites_enseignement import \
    CatalogueUnitesEnseignementTranslator
from infrastructure.preparation_programme_annuel_etudiant.repository.in_memory.groupement_ajuste_inscription_cours \
    import GroupementAjusteInscriptionCoursInMemoryRepository
from infrastructure.shared_kernel.academic_year.repository.academic_year import AcademicYearRepository
from infrastructure.shared_kernel.campus.repository.uclouvain_campus import UclouvainCampusRepository
from infrastructure.shared_kernel.entite.repository.entiteucl import EntiteUCLRepository
from infrastructure.shared_kernel.language.repository.language import LanguageRepository
from infrastructure.utils import AbstractMessageBusCommands, load_message_bus_instance
from osis_common.ddd.interface import ApplicationServiceResult, CommandRequest
from program_management.ddd.command import BulkUpdateLinkCommand, GetReportCommand, GetProgramTreeVersionCommand
from program_management.ddd.repositories import program_tree as program_tree_repo
from program_management.ddd.repositories.report import ReportRepository
from program_management.ddd.service.read.get_program_tree_version_service import get_program_tree_version, \
    get_programme_formation
from program_management.ddd.service.read.get_report_service import get_report
from program_management.ddd.service.write.bulk_update_link_service import bulk_update_and_postpone_links


class MessageBusCommands(AbstractMessageBusCommands):
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
            EffectiveClassRepository()
        ),
        SearchClassesEnseignantCommand: lambda cmd: search_classes_enseignant(
            cmd,
            TutorAttributionToLearningUnitTranslator(),
            TutorRepository(),
            EffectiveClassRepository()
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
            ApplicantRepository(), VacantCourseRepository(), LearningUnitTranslator()
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
            LearningUnitTranslator(),
        ),
        SearchDetailClassesEffectivesCommand: lambda cmd: search_detail_classes_effectives(
            cmd,
            EffectiveClassRepository(),
        ),
        UnassignTutorClassCommand: lambda cmd: unassign_tutor_class(cmd, TutorRepository()),
        EditClassVolumeRepartitionToTutorCommand: lambda cmd: edit_class_volume_repartition_to_tutor(
            cmd,
            TutorRepository(),
            EffectiveClassRepository(),
            LearningUnitTranslator(),
        ),
        GetTutorRepartitionClassesCommand: lambda cmd: get_tutor_repartition_classes(cmd, TutorRepository()),
        GetClassesEffectivesDepuisUniteDEnseignementCommand: lambda cmd: get_learning_unit_effective_classes(
            cmd, EffectiveClassRepository()
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
        EncoderNotesEtudiantCommand: lambda cmd: encoder_notes_etudiant(
            cmd,
            NoteEtudiantRepository(),
            PeriodeEncodageNotesTranslator(),
            AttributionEnseignantTranslator(),
            HistoriserNotesService(),
            InscriptionExamenTranslator(),
            EncoderNotesRapportRepository()
        ),
        SoumettreNotesCommand: lambda cmd: soumettre_notes_etudiant(
            cmd,
            NoteEtudiantRepository(),
            ResponsableDeNotesRepository(),
            PeriodeEncodageNotesTranslator(),
            NotifierSoumissionNotes(),
            AttributionEnseignantTranslator(),
            SignaletiquePersonneTranslator(),
            SignaletiqueEtudiantTranslator(),
            HistoriserNotesService(),
            InscriptionExamenTranslator(),
        ),
        GetProgressionGeneraleCommand: lambda cmd: get_progression_generale(
            cmd,
            NoteEtudiantRepository(),
            ResponsableDeNotesRepository(),
            PeriodeEncodageNotesTranslator(),
            SignaletiqueEtudiantTranslator(),
            AttributionEnseignantTranslator(),
            UniteEnseignementTranslator(),
            InscriptionExamenTranslator(),
        ),
        AssignerResponsableDeNotesCommand: lambda cmd: assigner_responsable_de_notes(
            cmd,
            ResponsableDeNotesRepository(),
            AttributionEnseignantTranslator()
        ),
        GetFeuilleDeNotesGestionnaireCommand: lambda cmd: get_feuille_de_notes_gestionnaire(
            cmd,
            NoteEtudiantGestionnaireRepository(),
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
            AdresseFeuilleDeNotesRepository(),
            EntiteUCLRepository(),
            EntitesCohorteTranslator(),
        ),
        EncoderNotesCommand: lambda cmd: encoder_notes(
            cmd,
            NoteEtudiantGestionnaireRepository(),
            PeriodeEncodageNotesTranslator(),
            CohortesDuGestionnaireTranslator(),
            NotifierEncodageNotes(),
            AttributionEnseignantTranslator(),
            SignaletiquePersonneTranslator(),
            SignaletiqueEtudiantTranslator(),
            AdresseFeuilleDeNotesRepository(),
            HistoriserEncodageNotesService(),
            InscriptionExamenTranslator(),
            EncoderNotesRapportRepository()
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
            UniteEnseignementTranslator(),
            InscriptionExamenTranslator(),
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
            InscriptionExamenTranslator(),
            AttributionEnseignantTranslator(),
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
                EntitesCohorteTranslator(),
                PeriodeEncodageNotesTranslator(),
        ),
        EncoderAdresseFeuilleDeNotesSpecifique: lambda cmd: encoder_adresse_feuille_de_notes_specifique(
            cmd,
            AdresseFeuilleDeNotesRepository(),
            PeriodeEncodageNotesTranslator(),
        ),
        SupprimerAdresseFeuilleDeNotesPremiereAnneeDeBachelier: lambda cmd: \
            supprimer_adresse_feuille_de_note_premiere_annee_de_bachelier(
                cmd,
                AdresseFeuilleDeNotesRepository(),
                PeriodeEncodageNotesTranslator(),
        ),
        GetAdresseFeuilleDeNotesServiceCommand: lambda cmd: get_adresse_feuille_de_notes(
            cmd,
            AdresseFeuilleDeNotesRepository(),
            PeriodeEncodageNotesTranslator(),
            EntiteUCLRepository(),
            EntitesCohorteTranslator(),
        ),
        GetChoixEntitesAdresseFeuilleDeNotesCommand: lambda cmd: get_choix_entites_adresse_feuille_de_notes(
            cmd,
            EntiteUCLRepository(),
            EntitesCohorteTranslator(),
            PeriodeEncodageNotesTranslator(),
        ),
        GetResponsableDeNotesCommand: lambda cmd: get_responsable_de_notes(
            cmd,
            ResponsableDeNotesRepository(),
        ),
        SearchFormationsCommand: lambda cmd: search_formations(
            cmd,
            TrainingRepository(),
        ),
        GetEncoderNotesRapportCommand: lambda cmd: get_encoder_notes_rapport(
            cmd,
            EncoderNotesRapportRepository()
        ),
        SearchResponsableDeNotesCommand: lambda cmd: search_responsables_de_notes(
            cmd,
            ResponsableDeNotesRepository()
        ),
        SearchEnseignantsCommand: lambda cmd: rechercher_enseignants(
            cmd,
            AttributionEnseignantTranslator(),
            PeriodeEncodageNotesTranslator(),
        ),
        SearchClassesParNomEnseignantCommand: lambda cmd: search_classes_par_nom_prenom(
            cmd,
            TutorAttributionToLearningUnitTranslator(),
            TutorRepository(),
        ),
        SendAttributionEndDateReachedSummaryCommand: lambda cmd: send_emails_to_teachers_with_ending_attributions(
            ApplicationCalendarRepository(),
            ApplicantRepository(),
            AttributionsEndDateReachedSummary()
        ),
        AjouterUEAuProgrammeCommand: lambda cmd: ajouter_UE_au_programme(
            cmd,
            GroupementAjusteInscriptionCoursInMemoryRepository(),
        ),
        GetProgramTreeVersionCommand: lambda cmd: get_program_tree_version(cmd),
        GetFormulaireInscriptionCoursCommand: lambda cmd: get_formulaire_inscription_cours_service(
            cmd,
            GroupementAjusteInscriptionCoursInMemoryRepository(),
            CatalogueFormationsTranslator(),
            CatalogueUnitesEnseignementTranslator(),
        ),
        GetFormationCommand: lambda cmd: get_programme_formation(cmd),
        GetProgrammeInscriptionCoursCommand: lambda cmd: get_programme_inscription_cours(
            cmd,
            GroupementAjusteInscriptionCoursInMemoryRepository(),
            CatalogueFormationsTranslator(),
            CatalogueUnitesEnseignementTranslator(),
        ),
    }  # type: Dict[CommandRequest, Callable[[CommandRequest], ApplicationServiceResult]]


message_bus_instance = load_message_bus_instance('message_bus')
