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
from ddd.logic.encodage_des_notes.soumission.builder.responsable_de_notes_identity_builder import \
    ResponsableDeNotesIdentityBuilder
from ddd.logic.encodage_des_notes.soumission.domain.model.feuille_de_notes import FeuilleDeNotes
from ddd.logic.encodage_des_notes.soumission.domain.service.i_attribution_enseignant import \
    IAttributionEnseignantTranslator
from ddd.logic.encodage_des_notes.soumission.domain.service.i_inscription_examen import IInscriptionExamenTranslator
from ddd.logic.encodage_des_notes.soumission.domain.service.i_periode_soumission_notes import \
    IPeriodeSoumissionNotesTranslator
from ddd.logic.encodage_des_notes.soumission.domain.service.i_signaletique_etudiant import \
    ISignaletiqueEtudiantTranslator
from ddd.logic.encodage_des_notes.soumission.domain.service.i_unite_enseignement import IUniteEnseignementTranslator
from ddd.logic.encodage_des_notes.soumission.dtos import FeuilleDeNotesEnseignantDTO, EnseignantDTO, NoteEtudiantDTO
from ddd.logic.encodage_des_notes.soumission.repository.i_responsable_de_notes import IResponsableDeNotesRepository
from osis_common.ddd import interface


class FeuilleDeNotesEnseignant(interface.DomainService):

    @classmethod
    def get(
            cls,
            feuille_de_notes: 'FeuilleDeNotes',
            matricule_fgs_enseignant: str,
            responsable_notes_repo: 'IResponsableDeNotesRepository',
            periode_soumission_note_translator: 'IPeriodeSoumissionNotesTranslator',
            inscription_examen_translator: 'IInscriptionExamenTranslator',
            signaletique_etudiant_translator: 'ISignaletiqueEtudiantTranslator',
            attribution_translator: 'IAttributionEnseignantTranslator',
            unite_enseignement_translator: 'IUniteEnseignementTranslator',
    ) -> 'FeuilleDeNotesEnseignantDTO':
        # TODO :: decoupe en fonction
        # TODO :: reutiliser attribution_translator pour le nom/prenom du resp notes
        # TODO :: unit tests

        unite_enseignement = unite_enseignement_translator.get(
            feuille_de_notes.code_unite_enseignement,
            feuille_de_notes.annee,
        )
        responsable_notes_entity_id = ResponsableDeNotesIdentityBuilder.build_from_matricule_fgs_enseignant(
            matricule_fgs_enseignant=matricule_fgs_enseignant,
        )
        responsable_notes = responsable_notes_repo.get_detail_enseignant(responsable_notes_entity_id)
        enseignants = attribution_translator.search_attributions_enseignant(
            matricule_fgs_enseignant,
            feuille_de_notes.annee,
        )
        autres_enseignants = [
            EnseignantDTO(nom=enseignant.nom, prenom=enseignant.prenom)
            for enseignant in sorted(enseignants, key=lambda ens: (ens.nom, ens.prenom))
        ]

        nomas_concernes = [note.noma for note in feuille_de_notes.notes]
        inscr_examens = inscription_examen_translator.search_inscrits(
            code_unite_enseignement=feuille_de_notes.code_unite_enseignement,
            annee=feuille_de_notes.annee,
            numero_session=feuille_de_notes.numero_session,
        )
        inscr_examen_par_noma = {insc_exam.noma: insc_exam for insc_exam in inscr_examens}
        desinscriptions_examens = inscription_examen_translator.search_desinscrits(
            code_unite_enseignement=feuille_de_notes.code_unite_enseignement,
            annee=feuille_de_notes.annee,
            numero_session=feuille_de_notes.numero_session,
        )
        desinscr_examen_par_noma = {desinscr.noma: desinscr for desinscr in desinscriptions_examens}

        signaletiques_etds = signaletique_etudiant_translator.search(nomas=nomas_concernes)
        signaletique_par_noma = {signal.noma: signal for signal in signaletiques_etds}

        periode_soumission = periode_soumission_note_translator.get()

        result = []
        for note in feuille_de_notes.notes:
            inscr_exmen = inscr_examen_par_noma.get(note.noma)
            inscrit_tardivement = inscr_exmen and inscr_exmen.date_inscription > periode_soumission.debut_periode_soumission
            desinscription = desinscr_examen_par_noma.get(note.noma)
            signaletique = signaletique_par_noma[note.noma]
            result.append(
                NoteEtudiantDTO(
                    est_soumise=note.est_soumise,
                    date_remise_de_notes=note.date_limite_de_remise,
                    sigle_formation=inscr_exmen.sigle_formation if inscr_exmen else desinscription.sigle_formation,
                    noma=note.noma,
                    nom=signaletique.nom,
                    prenom=signaletique.prenom,
                    peps=signaletique.peps,
                    email=note.email,
                    note=note.note.value,
                    inscrit_tardivement=inscrit_tardivement,
                    desinscrit_tardivement=bool(desinscription),
                )
            )

        return FeuilleDeNotesEnseignantDTO(
            code_unite_enseignement=feuille_de_notes.code_unite_enseignement,
            intitule_complet_unite_enseignement=unite_enseignement,
            responsable_note=EnseignantDTO(
                nom=responsable_notes.nom,
                prenom=responsable_notes.prenom,
            ),
            autres_enseignants=autres_enseignants,
            annee_academique=feuille_de_notes.annee,
            numero_session=feuille_de_notes.numero_session,
            notes_etudiants=None,
        )
