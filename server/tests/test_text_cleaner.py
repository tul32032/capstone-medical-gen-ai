from pdf_processing.text_cleaner import (
    clean_document_text,
    dedupe_paragraphs,
    drop_inline_citations,
    find_cutoff,
    find_end_start,
    find_refs_start,
    normalize_text,
    repair_text,
)


def test_normalize_text_standardizes_whitespace_and_blank_lines():
    raw = " First line \r\n\r\n\r\nSecond line\u00a0\r\n"

    assert normalize_text(raw) == "First line\n\nSecond line"


def test_drop_inline_citations_removes_bracket_and_parenthetical_citations():
    assert drop_inline_citations("Evidence [1, 2] supports this (3).") == "Evidence  supports this ."


def test_dedupe_paragraphs_removes_consecutive_duplicates():
    text = "Paragraph one\n\nParagraph one\n\nParagraph two"

    assert dedupe_paragraphs(text) == "Paragraph one\n\nParagraph two\n"


def test_find_reference_and_end_headers():
    text = "Intro\nReferences\n1. Ref\nAcknowledgments\nThanks"

    assert find_refs_start(text) == 1
    assert find_end_start(text) == 3
    assert find_cutoff(text) == 1


def test_repair_text_fixes_common_pdf_line_break_artifacts():
    text = "IgG\n4-related disease re\nturned and post\nobstructive injury"

    assert repair_text(text) == "IgG4-related disease returned and post-obstructive injury"


def test_clean_document_text_removes_top_matter_figures_tables_and_references():
    raw_text = """
Title Of Paper
Jane Doe
Department of Medicine
Correspondence: jane@example.com

Introduction [1]
This is a useful finding.

Figure 1. This caption should go away
short caption line

Real discussion starts here with enough content to stop caption skipping after it.
| col1 | col2 |
| --- | --- |
| a | b |

References
1. A cited paper
"""

    cleaned = clean_document_text(raw_text, remove_tables=True)

    assert "Jane Doe" not in cleaned
    assert "Correspondence" not in cleaned
    assert "Figure 1" not in cleaned
    assert "| col1 | col2 |" not in cleaned
    assert "References" not in cleaned
    assert "Introduction" in cleaned
    assert "Real discussion starts here" in cleaned
