from pathlib import Path

from app.utils.env_vars import LLM_ROOT


def get_project_root() -> Path:
    return Path(__file__).parent.parent.parent


PROJECT_ROOT = get_project_root()
if LLM_ROOT == "local":
    model_root = PROJECT_ROOT
else:
    model_root = LLM_ROOT
BERT_MODEL_PATH = Path(model_root) / "checkpoint-200"
BERT_MODEL_PT_PATH = Path(model_root) / "bert_model.pt"
T5_MODEL_PATH = Path(model_root) / "t5_decorator_model"
