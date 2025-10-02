import json
import unittest

from service.csv2jsonl import CsvToJsonlConverter


class TestCsvToJsonlConverter(unittest.TestCase):
    def test_conversion_creates_valid_jsonl(self):
        # Setup
        input_path = "storage/csv2jsonl_input.csv"
        output_path = "storage/csv2jsonl_output.jsonl"
        with open(input_path, "w", encoding="utf-8") as f:
            f.write('"summary","entities","keywords"\n')
            f.write('"Summary12","Entity1,Entity2","Keyword1,Keyword2"\n')
            f.write('"Summary34","Entity3,Entity4","Keyword3,Keyword4"\n')

        # Run

        converter = CsvToJsonlConverter(input_path, output_path)
        converter.convert()

        # Validate
        with open(output_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            self.assertEqual(len(lines), 2)
            obj = json.loads(lines[0])
            self.assert_obj_fields(obj, "1", "2")
            obj = json.loads(lines[1])
            self.assert_obj_fields(obj, "3", "4")

        # Cleanup
        # os.remove(input_path)
        # os.remove(output_path)

    def test_creates_valid_jsonl_diacritics(self):
        # Setup
        input_path = "storage/csv2jsonl_input.csv"
        output_path = "storage/csv2jsonl_output.jsonl"
        with open(input_path, "w", encoding="utf-8") as f:
            f.write('"summary","entities","keywords"\n')
            f.write('"Școala și viața în România merg împreună pe 15 septembrie","text,1-0,text","1-2,text"\n')

        # Run

        converter = CsvToJsonlConverter(input_path, output_path)
        converter.convert()

        # Validate
        with open(output_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            self.assertEqual(len(lines), 1)
            obj = json.loads(lines[0])
            self.assertEqual(obj["summary"], "Școala și viața în România merg împreună pe 15 septembrie")
            self.assertEqual(obj["entities"], ["text", "1-0", "text"])
            self.assertEqual(obj["keywords"], ["1-2", "text"])

        # Cleanup
        # os.remove(input_path)
        # os.remove(output_path)

    def test_creates_valid_jsonl_NaN(self):
        # Setup
        input_path = "storage/csv2jsonl_input.csv"
        output_path = "storage/csv2jsonl_output.jsonl"
        with open(input_path, "w", encoding="utf-8") as f:
            f.write('"summary","entities","keywords"\n')
            f.write('"Școala și viața","",""\n')

        # Run

        converter = CsvToJsonlConverter(input_path, output_path)
        converter.convert()

        # Validate
        with open(output_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            self.assertEqual(len(lines), 1)
            obj = json.loads(lines[0])
            self.assertEqual(obj["summary"], "Școala și viața")
            self.assertEqual(obj["entities"], [])
            self.assertEqual(obj["keywords"], [])

        # Cleanup
        # os.remove(input_path)
        # os.remove(output_path)

    def assert_obj_fields(self, obj, u: str, v: str):
        self.assertEqual(obj["summary"], "Summary" + u + v)
        self.assertEqual(obj["entities"], ["Entity" + u, "Entity" + v])
        self.assertEqual(obj["keywords"], ["Keyword" + u, "Keyword" + v])


if __name__ == "__main__":
    unittest.main()
