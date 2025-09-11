import unittest

from service.util.named_entity import NamedEntity


class TestNamedEntity(unittest.TestCase):

    def setUp(self):
        self.extractor = NamedEntity()

    def test_basic_person_name_false(self):
        text = "Cristi Chivu este dorit la Inter Milano."
        entities = self.extractor.extract_ents(text)
        self.assertNotIn("Cristi Chivu", entities)

    def test_basic_person_name_wrong(self):
        text = "Jucătorul Cristi Chivu este dorit la Inter Milano."
        entities = self.extractor.extract_ents(text)
        self.assertIn("Jucătorul Cristi Chivu", entities)

    def test_basic_person_name(self):
        text = "Jucătorul român Cristi Chivu este dorit la Inter Milano."
        entities = self.extractor.extract_ents(text)
        self.assertIn("Cristi Chivu", entities)

    def test_organization_and_location(self):
        text = "FC Steaua București joacă pe Arena Națională din București."
        entities = self.extractor.extract_ents(text)
        self.assertIn("FC", entities)
        self.assertIn("Steaua București", entities)
        self.assertIn("București", entities)

    def test_multiple_names(self):
        text = "Gică Hagi și Gheorghe Popescu au fost colegi la Galatasaray."
        entities = self.extractor.extract_ents(text)
        self.assertIn("Gică Hagi", entities)
        self.assertIn("Gheorghe Popescu", entities)
        self.assertIn("Galatasaray", entities)

    def test_no_first_word(self):
        text = "Este o zi frumoasă."
        entities = self.extractor.extract_ents(text)
        self.assertEqual(entities, [])

    def test_no_entities(self):
        text = "Este o zi frumoasă. FC Steaua joacă cu RMA Madrid. MANU e în formă."
        entities = self.extractor.extract_ents(text)
        self.assertEqual(entities, ['FC Steaua', 'RMA Madrid', 'MANU'])

    def test_regex_only_detection(self):
        text = "Surprinzător! Jucătorul pe care-l vrea Cristi Chivu la Inter"
        entities = self.extractor.extract_ents(text)
        self.assertIn("Cristi Chivu", entities)
        self.assertIn("Inter", entities)

    def test_duplicate_removal(self):
        text = "Cristi Chivu, Cristi Chivu, Inter Milano"
        entities = self.extractor.extract_ents(text)
        self.assertEqual(entities.count("Cristi Chivu"), 1)

    def test_Daniela(self):
        text = "Sportiva română Daria-Măriuca Silişteanu a cucerit medalia de argint în proba de 100 m spate, miercuri, la Campionatele Mondiale de înot pentru juniori de la Otopeni."
        entities = self.extractor.extract_ents(text)
        self.assertEqual(entities.count("Daria-Măriuca Silişteanu"), 1)
        self.assertEqual(entities.count("Sportiva"), 1)


if __name__ == "__main__":
    unittest.main()
