from pathlib import Path

from .file_writer import write_chunks
from .pdf_extractor import (
    extract_chunks_with_fitz_fallback,
    extract_chunks_with_pymupdf4llm,
)


def run_one(
    pdf_path: Path,
    out_dir: Path,
    *,
    remove_tables: bool,
    max_chars: int,
    max_words: int,
) -> tuple[Path, int]:
    chunks = []

    try:
        chunks = extract_chunks_with_pymupdf4llm(
            pdf_path,
            remove_tables=remove_tables,
            max_chars=max_chars,
            max_words=max_words,
        )
        if chunks:
            print(f"[layout] pymupdf4llm succeeded for {pdf_path.name} with {len(chunks)} chunks.")
        else:
            print(f"[warn] pymupdf4llm returned no chunks for {pdf_path.name}")
    except Exception as err:
        print(f"[error] pymupdf4llm failed for {pdf_path.name}: {err}")

    if not chunks:
        print(f"[fallback] Trying raw PyMuPDF text extraction for {pdf_path.name}...")
        try:
            chunks = extract_chunks_with_fitz_fallback(
                pdf_path,
                max_chars=max_chars,
                max_words=max_words,
            )

            if chunks:
                print(f"[fallback] Raw PyMuPDF extraction succeeded for {pdf_path.name}.")
            else:
                print(f"[fallback] Raw PyMuPDF extraction also produced no text for {pdf_path.name}.")
        except Exception as fb_err:
            print(f"[fallback] Raw PyMuPDF fallback failed for {pdf_path.name}: {fb_err}")

    pdf_out_dir, written = write_chunks(out_dir, pdf_path, chunks)
    return pdf_out_dir, written