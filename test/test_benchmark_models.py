import csv
import json
import os
import random
from typing import List, Dict

from service.article_scraper import EntityExtractorFacade, ModelType

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# CSV_PATH = os.path.join(BASE_DIR, "storage", "prosport_dump.csv")
CSV_PATH = os.path.join(BASE_DIR, "storage", "bert_lora_dump.csv")
JSON_PATH = os.path.join(BASE_DIR, "storage", "training", "example.json")


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
        results["STATIC_FILE"] = []  # Include test file ground truth

        for row in selected:
            summary = row["summary"]
            bert_entities = [e.strip() for e in row.get("entities", "").split(",") if e.strip()]
            bert_keywords = [k.strip() for k in row.get("keywords", "").split(",") if k.strip()]
            results["STATIC_FILE"].append({
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
    # runner = BenchmarkRunner(CSV_PATH, [ModelType.CLAUDE, ModelType.GPT, ModelType.SPACY])
    runner = BenchmarkRunner(CSV_PATH, [ModelType.SPACY])
    results = runner.run(load_training_data(JSON_PATH))

    for i in range(len(results["STATIC_FILE"])):
        print_initial_model(i, results)

        for model in runner.model_types:
            print_other_model(i, model, results)


def test_benchmark_lora():
    runner = BenchmarkRunner(CSV_PATH, [ModelType.BERT_LORA])
    # runner = BenchmarkRunner(CSV_PATH, [ModelType.CLAUDE, ModelType.BERT_LORA])
    claude_training_data = load_training_data(JSON_PATH)
    results = runner.run(claude_training_data)

    for i in range(len(results["STATIC_FILE"])):
        print_initial_model(i, results)

        for model in runner.model_types:
            print_other_model(i, model, results)


def print_other_model(i, model, results):
    model_name = model.name
    print(f"\n--- {model_name} ---")
    print("Entities:", results[model_name][i]["entities"])
    print("Keywords:", results[model_name][i]["keywords"])


def print_initial_model(i, results):
    print(f"\n=== Summary {i + 1} ===")
    print("Summary:", results["STATIC_FILE"][i]["summary"])
    print("\n--- STATIC_FILE (Ground Truth) ---")
    print("Entities:", results["STATIC_FILE"][i]["entities"])
    print("Keywords:", results["STATIC_FILE"][i]["keywords"])


def load_training_data(json_path: str) -> List[Dict]:
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)
