import unittest

from service.util.summary_util import merge_summaries


class TestSummaryUtil(unittest.TestCase):
    def test_merge_summaries_basic(self):
        summaries = [
            """CFR Cluj a scăpat două puncte printre degete în prelungirile partidei cu Csikszereda. 
            Ciucanii au beneficiat de un penalty, care în opinia lui Andrea Mandorlini a fost acordat ușor. 
            Ce a spus despre arbitraj[...]""",
            """Andrea Mandorlini, antrenorul de la CFR Cluj, a tras concluziile, după ce echipa lui a remizat 
            pe terenul celor de la Csikszereda, scor 2-2, într-un meci restant din runda 5 din Superliga."""
        ]
        result = merge_summaries(summaries)
        print()
        print(result)
        self.assertTrue("Andrea Mandorlini" in result)
        self.assertTrue("CFR Cluj" in result)
        self.assertTrue("Csikszereda" in result)
        self.assertLessEqual(len(result.split('.')), 4)

    def test_merge_summaries_with_ellipsis_delimiters(self):
        summaries = [
            "Mandorlini a fost nervos [...]",
            "CFR Cluj a pierdut două puncte....",
            "Ciucanii au egalat în prelungiri"
        ]
        result = merge_summaries(summaries)
        self.assertTrue("Mandorlini" in result)
        self.assertTrue("CFR Cluj" in result)
        self.assertTrue(result.endswith("."))

    def test_merge_summaries_missing_final_punctuation(self):
        summaries = [
            "Mandorlini a fost nervos",
            "CFR Cluj a pierdut două puncte",
            "Ciucanii au egalat în prelungiri"
        ]
        result = merge_summaries(summaries)
        self.assertTrue(result.endswith("."))
        self.assertLessEqual(len(result.split('.')), 4)


if __name__ == "__main__":
    unittest.main()
