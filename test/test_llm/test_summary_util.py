import unittest

from service.util.merged_summary_by_keys_util import merge_summaries_with_keywords


class TestSummaryUtilFlatMap(unittest.TestCase):

    def test_merge_summaries_real_keywords(self):
        summaries = [
            "Ioan Neculaie (68 de ani), omul de afaceri care a fost patron la FC Brașov între 1999 și 2015, a fost "
            "condamnat la 10 ani de închisoare cu executare, pentru evaziune fiscală.",
            "Oamenii care au fost în fotbalul românesc continuă să aibă probleme cu legea, iar acum o condamnare de "
            "10 ani a venit pe numele celui care visa să se lupte pentru locurile fruntașe.",
            "Ioan Neculaie, fost patron la FC Brașov în perioada în care echipa activa în Liga 1, a fost condamnat "
            "la 10 ani de închisoare pentru evaziune fiscală. Verdictul nu e definitiv și poate fi atacat.",
            "Fostul patron al lui FC Brașov, Ioan Neculaie (68 de ani), a fost condamnat de Tribunalul Brașov la "
            "10 ani de închisoare. Decizia instanței nu e definitivă.156",
            "Omul de afaceri Ioan Neculaie, fost patron al celor de la FC Brașov, a fost condamnat la 10 ani de "
            "închisoare, potrivit informațiilor publicate pe portalul instanțelor. Hotărârea nu este definitivă.",
        ]
        result = merge_summaries_with_keywords(summaries)
        # Should contain key entities/keywords
        self.assertIn("Ioan Neculaie", result)
        self.assertIn("FC Brașov", result)
        # Should not exceed 3 sentences
        self.assertLessEqual(len(result.split('.')), 4)
        self.assertEqual("Ioan Neculaie (68 de ani), omul de afaceri care a fost patron la FC Brașov între 1999 "
                         "și 2015, a fost condamnat la 10 ani de închisoare cu executare, pentru evaziune fiscală. "
                         "Decizia instanței nu e definitivă.", result)

    def test_merge_summaries_basic_keywords(self):
        summaries = [
            "CFR Cluj a scăpat două puncte în prelungiri. Mandorlini a fost nervos.",
            "Ciucanii au egalat în prelungiri. Andrea Mandorlini a criticat arbitrajul.",
            "CFR Cluj a remizat cu Csikszereda, scor 2-2."
        ]
        result = merge_summaries_with_keywords(summaries)
        # Should contain key entities/keywords
        self.assertIn("CFR Cluj", result)
        self.assertIn("Mandorlini", result)
        self.assertEqual("Andrea Mandorlini a criticat arbitrajul. CFR Cluj a scăpat două puncte în prelungiri. "
                         "Ciucanii au egalat în prelungiri.", result)
        # Should not exceed 3 sentences
        self.assertLessEqual(len(result.split('.')), 4)

    def test_merge_summaries_frequency_ranking(self):
        summaries = [
            "Messi a marcat un gol spectaculos.",
            "Messi a marcat un gol spectaculos.",
            "Ronaldo a reușit o dublă."
        ]
        result = merge_summaries_with_keywords(summaries)
        # The repeated Messi sentence should be ranked first
        self.assertTrue(result.startswith("Messi a marcat"))
        self.assertIn("Ronaldo", result)

    def test_merge_summaries_deduplication(self):
        summaries = [
            "Mbappe a fost omul meciului.",
            "Mbappe a fost omul meciului.",
            "Mbappe a fost omul meciului."
        ]
        result = merge_summaries_with_keywords(summaries)
        # Sentence should appear only once despite repetition
        self.assertEqual(result.count("Mbappe a fost omul meciului"), 1)

    def test_merge_summaries_empty_input(self):
        summaries = []
        result = merge_summaries_with_keywords(summaries)
        self.assertEqual(result, "No summaries")

    def test_merge_summaries_fallback(self):
        # No keywords detected (short words only)
        summaries = [
            "A fost un meci.",
            "O echipă a câștigat.",
            "Un alt meci s-a terminat."
        ]
        result = merge_summaries_with_keywords(summaries)
        # Should fall back to first few sentences
        self.assertEqual('O echipă a câștigat. Un alt meci s-a terminat.', result)
        self.assertLessEqual(len(result.split('.')), 4)


if __name__ == "__main__":
    unittest.main()
