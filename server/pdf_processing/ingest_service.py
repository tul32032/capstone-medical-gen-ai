from pathlib import Path

from .pdf_extractor import extract_markdown_pages
from .text_cleaner import clean_document_text

from .file_writer import write_md


def build_md(pages: list[dict], *, remove_tables: bool) -> str:
    parts: list[str] = []

    for page in pages:
        page_number = page.get("page", 1)
        text = page.get("text", "")

        if not text or not str(text).strip():
            continue

        cleaned = clean_document_text(str(text), remove_tables=remove_tables)
        if not cleaned.strip():
            continue

        parts.append(f"\n<!-- page: {page_number} -->\n")
        parts.append(cleaned.strip() + "\n")

    return ("".join(parts).strip() + "\n") if parts else ""


def run_one(
    pdf_path: Path,
    out_dir: Path,
    *,
    remove_tables: bool,
) -> Path | None:
    """Convert a single PDF into ONE cleaned markdown file."""

    try:
        pages = extract_markdown_pages(pdf_path)
        print(f"[extract] extracted {len(pages)} pages from {pdf_path.name}")
    except Exception as err:
        print(f"[error] extraction failed for {pdf_path.name}: {err}")
        return None

    md = build_md(pages, remove_tables=remove_tables)
    if not md:
        print(f"[warn] no cleaned markdown generated for {pdf_path.name}")
        return None

    try:
        output_path = write_md(out_dir, pdf_path, md)
        print(f"[write] wrote markdown: {output_path}")
        return output_path
    except Exception as write_err:
        print(f"[error] failed to write markdown for {pdf_path.name}: {write_err}")
        return None


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python3 -m server.pdf_processing.ingest_service <pdf_path> <output_dir>")
        sys.exit(1)

    pdf_path = Path(sys.argv[1])
    out_dir = Path(sys.argv[2])

    out_dir.mkdir(parents=True, exist_ok=True)

    result = run_one(pdf_path, out_dir, remove_tables=False)

    if result:
        print(f"Done: {result}")
    else:
        print("Failed to process PDF")