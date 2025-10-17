import os

import pytest

from service.extractor_ents_keys import EntityKeywordExtractor
from service.util.path_util import PROJECT_ROOT, BERT_MODEL_PATH, BERT_MODEL_PT_PATH


@pytest.fixture(params=["classic", "torchscript"])
def extractor(request):
    base_dir = BERT_MODEL_PATH
    model_pt_path = BERT_MODEL_PT_PATH

    if request.param == "classic":
        return EntityKeywordExtractor(base_dir)
    else:
        return EntityKeywordExtractor(
            model_pt_path,
            use_torchscript=True,
            tokenizer_path=base_dir
        )


def test_extraction_basic(extractor):
    text = "Vladimir Screciu a declarat că echipa sa trebuie să câștige în etapa următoare după înfrângerea cu Oțelul Galați."
    result = extractor.extract_with_roberta(text)
    assert isinstance(result, dict)
    assert "entities" in result and "keywords" in result
    assert all(isinstance(e, str) for e in result["entities"])
    assert all(isinstance(k, str) for k in result["keywords"])
    print(result["entities"])
    print(result["keywords"])


def test_empty_input(extractor):
    result = extractor.extract_with_roberta("")
    assert result == {"entities": [], "keywords": []}
