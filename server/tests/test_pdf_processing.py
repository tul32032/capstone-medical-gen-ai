from pathlib import Path
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile

from pdf_processing.file_writer import write_md
from pdf_processing.ingest_service import build_md, run_one
from pdf_processing.upload_ingest import ingest_uploaded_pdf


def test_write_md_sanitizes_name_and_writes_front_matter(tmp_path):
    output_path = write_md(
        tmp_path,
        Path("A sample paper!!.pdf"),
        "  # Heading\n\nBody text  ",
    )

    assert output_path.name == "A_sample_paper_.md"
    contents = output_path.read_text(encoding="utf-8")
    assert contents.startswith("---\nsource: A sample paper!!.pdf\n---\n\n")
    assert contents.endswith("Body text\n")


@patch("pdf_processing.ingest_service.clean_document_text")
def test_build_md_skips_empty_pages(mock_clean_document_text):
    mock_clean_document_text.side_effect = ["Cleaned first page\n", "", "Cleaned third page\n"]

    result = build_md(
        [
            {"page": 1, "text": "First"},
            {"page": 2, "text": "Second"},
            {"page": 3, "text": "Third"},
        ],
        remove_tables=False,
    )

    assert "<!-- page: 1 -->" in result
    assert "<!-- page: 2 -->" not in result
    assert "<!-- page: 3 -->" in result


@patch("pdf_processing.ingest_service.write_md")
@patch("pdf_processing.ingest_service.extract_markdown_pages")
def test_run_one_returns_output_path_on_success(mock_extract_markdown_pages, mock_write_md, tmp_path):
    pdf_path = tmp_path / "paper.pdf"
    pdf_path.write_bytes(b"%PDF-1.7")
    out_dir = tmp_path / "out"
    written_path = out_dir / "paper.md"

    mock_extract_markdown_pages.return_value = [{"page": 1, "text": "Body"}]
    mock_write_md.return_value = written_path

    result = run_one(pdf_path, out_dir, remove_tables=False)

    assert result == written_path


@patch("pdf_processing.ingest_service.extract_markdown_pages", side_effect=RuntimeError("bad pdf"))
def test_run_one_returns_none_when_extraction_fails(mock_extract_markdown_pages, tmp_path):
    pdf_path = tmp_path / "paper.pdf"
    pdf_path.write_bytes(b"%PDF-1.7")

    assert run_one(pdf_path, tmp_path / "out", remove_tables=False) is None


@patch("pdf_processing.ingest_service.extract_markdown_pages", return_value=[{"page": 1, "text": ""}])
def test_run_one_returns_none_when_cleaned_markdown_is_empty(mock_extract_markdown_pages, tmp_path):
    pdf_path = tmp_path / "paper.pdf"
    pdf_path.write_bytes(b"%PDF-1.7")

    assert run_one(pdf_path, tmp_path / "out", remove_tables=False) is None


@patch("pdf_processing.upload_ingest.run_one")
def test_ingest_uploaded_pdf_returns_generated_markdown(mock_run_one, tmp_path):
    output_path = tmp_path / "out.md"
    output_path.write_text("# Title\n", encoding="utf-8")
    mock_run_one.return_value = output_path

    uploaded_file = SimpleUploadedFile("upload.pdf", b"%PDF-1.7 mock content")

    assert ingest_uploaded_pdf(uploaded_file) == "# Title\n"


@patch("pdf_processing.upload_ingest.run_one", return_value=None)
def test_ingest_uploaded_pdf_returns_none_when_pipeline_fails(mock_run_one):
    uploaded_file = SimpleUploadedFile("upload.pdf", b"%PDF-1.7 mock content")

    assert ingest_uploaded_pdf(uploaded_file) is None
