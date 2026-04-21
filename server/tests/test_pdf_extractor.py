from unittest.mock import patch

from pdf_processing.pdf_extractor import extract_markdown_pages, normalize_pages


def test_normalize_pages_handles_strings_dicts_and_blocks():
    raw_pages = [
        {"page_number": "3", "blocks": [{"text": "Block A"}, {"content": "Block B"}]},
        "Plain page text",
        42,
    ]

    normalized = normalize_pages(raw_pages)

    assert normalized == [
        {"page": 3, "text": "Block A\nBlock B", "metadata": {}},
        {"page": 2, "text": "Plain page text", "metadata": {}},
        {"page": 3, "text": "42", "metadata": {}},
    ]


def test_normalize_pages_uses_nested_pages_list():
    normalized = normalize_pages(
        {
            "pages": [
                {"metadata": {"page": 7}, "markdown": "Nested markdown"},
            ]
        }
    )

    assert normalized == [
        {"page": 7, "text": "Nested markdown", "metadata": {"page": 7}},
    ]


@patch("pdf_processing.pdf_extractor.extract_with_llm")
def test_extract_markdown_pages_falls_back_to_raw_text(mock_extract_with_llm, tmp_path):
    pdf_path = tmp_path / "sample.pdf"
    pdf_path.write_bytes(b"%PDF-1.7")
    mock_extract_with_llm.side_effect = [None, [{"page": 1, "text": "Raw page", "metadata": {}}]]

    result = extract_markdown_pages(pdf_path)

    assert result == [{"page": 1, "text": "Raw page", "metadata": {}}]


@patch("pdf_processing.pdf_extractor.extract_with_llm", side_effect=[None, None])
def test_extract_markdown_pages_returns_empty_list_when_all_extractors_fail(mock_extract_with_llm, tmp_path):
    pdf_path = tmp_path / "sample.pdf"
    pdf_path.write_bytes(b"%PDF-1.7")

    assert extract_markdown_pages(pdf_path) == []
