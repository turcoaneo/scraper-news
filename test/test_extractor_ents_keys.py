import pytest

from service.extractor_ents_keys import EntityKeywordExtractor


@pytest.fixture
def extractor():
    return EntityKeywordExtractor("../dumitrescustefan_token_output/checkpoint-200")


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
