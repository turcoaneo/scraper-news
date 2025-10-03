# test_span_utils.py
from service.util.span_utils import SpanUtils


def test_suppress_sub_spans():
    input_spans = ["Screciu", "Vladimir Screciu", "Oțelul Galați", "Galați"]
    expected = ["Oțelul Galați", "Vladimir Screciu"]
    assert SpanUtils.suppress_sub_spans(input_spans) == expected


def test_group_labeled_phrases_basic():
    word_ids = [0, 1, 2, 3, 4, 5]
    labels = ["B-ENT", "B-ENT", "O", "B-KW", "B-KW", "O"]
    words = ["Vladimir", "Screciu", "a", "declarat", "echipa", "."]
    result = SpanUtils.group_labeled_phrases(word_ids, labels, words)
    assert result["entities"] == ["Vladimir Screciu"]
    assert result["keywords"] == ["declarat echipa"]