import csv
import json
import random
from typing import List, Dict

from service.article_scraper import EntityExtractorFacade, ModelType


class BenchmarkRunner:
    def __init__(self, csv_path: str, model_types: List[ModelType]):
        self.csv_path = csv_path
        self.model_types = model_types

    from typing import List, Dict

    def load_summaries(self) -> List[str]:
        with open(self.csv_path, newline='', encoding='utf-8') as f:
            reader: csv.DictReader = csv.DictReader(f)
            return [row["summary"] for row in reader if row["summary"]]

    def run(self, training_data: List[Dict] = None) -> Dict[str, List[Dict]]:
        summaries = self.load_summaries()
        selected = random.sample(summaries, k=2)  # 👈 pick 2 random summaries
        results = {model.name: [] for model in self.model_types}

        for summary in selected:
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
    # results = runner.run()

    # Optional: print or save results
    for model, outputs in results.items():
        print(f"\n--- {model} ---")
        for item in outputs[:3]:  # show first 3
            print("Summary:", item["summary"])
            print("Entities:", item["entities"])
            print("Keywords:", item["keywords"])
