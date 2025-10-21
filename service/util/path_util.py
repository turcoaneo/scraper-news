from pathlib import Path


def get_project_root() -> Path:
    return Path(__file__).parent.parent.parent


PROJECT_ROOT = get_project_root()
BERT_MODEL_PATH = PROJECT_ROOT / "dumitrescustefan_token_output" / "checkpoint-200"
BERT_MODEL_PT_PATH = PROJECT_ROOT / "bert_model.pt"
