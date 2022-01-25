from unittest import mock

from django.test import SimpleTestCase

from infrastructure.messages_bus import message_bus_instance
from infrastructure.preparation_programme_annuel_etudiant.domain.service.in_memory.catalogue_formations import \
    CatalogueFormationsTranslator


class GetFormulaireInscriptionCoursTest(SimpleTestCase):

    def setUp(self) -> None:
        self.catalogue_formation_translator = CatalogueFormationsTranslator()
        self._mock_message_bus()

    def _mock_message_bus(self):
        message_bus_patcher = mock.patch.multiple(
            'infrastructure.messages_bus',
            CatalogueFormationsTranslator=lambda: self.catalogue_formation_translator,
        )
        message_bus_patcher.start()
        self.addCleanup(message_bus_patcher.stop)
        self.message_bus = message_bus_instance

    def test_should_visualiser_ECGE1BA_version_standard(self):
        # réutiliser le CatalogueFormationsTranslatorInMemory
        pass
