import csv
import json
import random
from typing import List, Dict

from service.article_scraper import EntityExtractorFacade, ModelType


class BenchmarkRunner:
    def __init__(self, csv_path: str, model_types: List[ModelType]):
        self.csv_path = csv_path
        self.model_types = model_types

    def load_rows(self) -> List[Dict[str, str]]:
        with open(self.csv_path, newline='', encoding='utf-8') as f:
            reader: csv.DictReader = csv.DictReader(f)
            return [row for row in reader if row.get("summary")]

    def run(self, training_data: List[Dict] = None) -> Dict[str, List[Dict]]:
        rows = self.load_rows()
        selected = random.sample(rows, k=2)
        results = {model.name: [] for model in self.model_types}
        results["BERT"] = []  # Include BERT ground truth

        for row in selected:
            summary = row["summary"]
            bert_entities = [e.strip() for e in row.get("entities", "").split(",") if e.strip()]
            bert_keywords = [k.strip() for k in row.get("keywords", "").split(",") if k.strip()]
            results["BERT"].append({
                "summary": summary,
                "entities": bert_entities,
                "keywords": bert_keywords
            })

            for model in self.model_types:
                output = EntityExtractorFacade.extract_by_model(summary, model, training_data or [])
                results[model.name].append({
                    "summary": summary,
                    "entities": output.get("entities", []),
                    "keywords": output.get("keywords", [])
                })

        return results


def test_benchmark_models():
    def load_training_data(json_path: str) -> List[Dict]:
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)

    runner = BenchmarkRunner("storage/prosport_dump.csv", [ModelType.SPACY, ModelType.GPT, ModelType.CLAUDE])
    results = runner.run(load_training_data("storage/training/example.json"))

    for i in range(len(results["BERT"])):
        print(f"\n=== Summary {i + 1} ===")
        print("Summary:", results["BERT"][i]["summary"])
        print("\n--- BERT (Ground Truth) ---")
        print("Entities:", results["BERT"][i]["entities"])
        print("Keywords:", results["BERT"][i]["keywords"])

        for model in runner.model_types:
            model_name = model.name
            print(f"\n--- {model_name} ---")
            print("Entities:", results[model_name][i]["entities"])
            print("Keywords:", results[model_name][i]["keywords"])
