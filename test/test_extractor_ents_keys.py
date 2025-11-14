import pytest

from service.extractor_ents_keys import EntityKeywordExtractor
from service.util.path_util import BERT_MODEL_PATH, BERT_MODEL_PT_PATH


@pytest.fixture(params=["classic", "torchscript"])
def extractor(request):
    base_dir = BERT_MODEL_PATH
    model_pt_path = BERT_MODEL_PT_PATH

    if request.param == "classic":
        return EntityKeywordExtractor(base_dir)
    else:
        return EntityKeywordExtractor(
            model_pt_path,
            use_torch_script=True,
            tokenizer_path=base_dir
        )


def test_extraction_basic(extractor):
    text = "Vladimir Screciu a declarat că echipa sa trebuie să câștige în etapa următoare după înfrângerea cu Oțelul."
    extract_and_assert(extractor, text)


def test_extraction_diacritics(extractor):
    text = "Vasile Șiman a promis că Sportul Studențesc va reveni în primul eșalon in câțiva ani."
    extract_and_assert(extractor, text)


def test_extraction_diacritics_new(extractor):
    text = "Dan Șucu aduce întăriri la Rapid București."
    extract_and_assert(extractor, text)


def test_extraction_diacritics_extra(extractor):
    text = "Ion Țiriac a promis că Sportul Studențesc va reveni în primul eșalon in câțiva ani."
    extract_and_assert(extractor, text)


def test_extraction_diacritics_alt(extractor):
    text = "Andrei Țăranu aduce întăriri la Rapid București."
    extract_and_assert(extractor, text)


def test_empty_input(extractor):
    result = extractor.extract_with_roberta("")
    assert result == {"entities": [], "keywords": []}


def extract_and_assert(extractor, text):
    result = extractor.extract_with_roberta(text)
    assert isinstance(result, dict)
    assert "entities" in result and "keywords" in result
    assert all(isinstance(e, str) for e in result["entities"])
    assert all(isinstance(k, str) for k in result["keywords"])
    print(result["entities"])
    print(result["keywords"])
