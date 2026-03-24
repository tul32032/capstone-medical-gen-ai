from pathlib import Path
from typing import Any, List

import re
import fitz
import pymupdf.layout
import pymupdf4llm

from .text_cleaner import (
    clean_chunk_text,
    find_bibliography_start_line_index,
    find_endmatter_start_line_index,
    normalize_text,
    remove_author_lines_near_top,
    remove_consecutive_duplicate_paragraphs,
)
from .section_chunker import chunk_pages_by_sections


def page_chunks_to_items(chunks: Any) -> List[tuple[int, int, str]]:
    """Normalize pymupdf4llm output into (chunk_no, page_no, text) items."""
    def coerce_text_from_page_dict(d: dict[str, Any]) -> str:
        txt = d.get("text") or d.get("content") or d.get("markdown") or d.get("md")
        if isinstance(txt, str) and txt.strip():
            return txt

        blocks = d.get("blocks")
        if isinstance(blocks, list):
            parts: List[str] = []
            for b in blocks:
                if isinstance(b, dict):
                    bt = b.get("text") or b.get("content") or b.get("span") or b.get("value")
                    if isinstance(bt, str) and bt.strip():
                        parts.append(bt)
            if parts:
                return "\n".join(parts)

        for k in ("page_text", "page", "raw_text", "raw", "data"):
            v = d.get(k)
            if isinstance(v, str) and v.strip():
                return v

        return ""

    def coerce_page_no(d: dict[str, Any], default_no: int) -> int:
        for k in ("page", "page_num", "page_number", "pageno", "pageIndex"):
            v = d.get(k)
            if isinstance(v, int) and v > 0:
                return v
            if isinstance(v, str) and v.isdigit():
                iv = int(v)
                if iv > 0:
                    return iv
        return default_no

    if isinstance(chunks, str):
        return [(1, 1, chunks)]

    if isinstance(chunks, dict):
        pages = chunks.get("pages") or chunks.get("page_chunks")
        if isinstance(pages, list):
            chunks = pages
        else:
            return [(1, 1, str(chunks))]

    if isinstance(chunks, list):
        items: List[tuple[int, int, str]] = []
        for idx, chunk in enumerate(chunks, start=1):
            page_no = idx
            text = ""

            if isinstance(chunk, dict):
                page_no = coerce_page_no(chunk, idx)
                text = coerce_text_from_page_dict(chunk)
            elif isinstance(chunk, str):
                text = chunk
            else:
                text = str(chunk)

            items.append((idx, page_no, text))

        return items

    return [(1, 1, str(chunks))]


def extract_chunks_with_pymupdf4llm(
    pdf_path: Path,
    *,
    remove_tables: bool,
    max_chars: int,
    max_words: int,
) -> List[tuple[int, int, int, str, str]]:
    """Convert PDF to text with pymupdf4llm, clean pages, then section-chunk across pages."""
    if not hasattr(pymupdf4llm, "to_text"):
        raise AttributeError("pymupdf4llm.to_text is not available in your installed version")

    with fitz.open(str(pdf_path)) as doc:
        raw = pymupdf4llm.to_text(doc, page_chunks=True)
    items = page_chunks_to_items(raw)

    try:
        with fitz.open(str(pdf_path)) as doc:
            page_count = doc.page_count
    except Exception:
        page_count = 0

    if page_count >= 2 and len(items) <= 1:
        return []

    cleaned_pages: List[tuple[int, str]] = []
    doc_title: str | None = None

    for i, (_chunk_no, page_no, ch_text) in enumerate(items):
        t = ch_text

        if i == 0:
            t = remove_author_lines_near_top(t)

        t = clean_chunk_text(t, remove_tables=remove_tables)
        t = remove_consecutive_duplicate_paragraphs(t)

        if i == 0 and doc_title is None:
            for ln in t.split("\n"):
                if ln.strip():
                    doc_title = ln.strip()
                    break

        if i > 0 and doc_title:
            dt = doc_title.strip()
            if 3 <= len(dt) <= 120:
                lines = t.split("\n")
                cleaned_lines: List[str] = []
                for ln in lines:
                    if ln.strip() == dt:
                        continue
                    cleaned_lines.append(ln)
                t = "\n".join(cleaned_lines)
                t = re.sub(r"\n{3,}", "\n\n", t).strip() + "\n"

        bib_idx = find_bibliography_start_line_index(t)
        if bib_idx is not None:
            lines = t.split("\n")
            t2 = "\n".join(lines[:bib_idx]).rstrip() + "\n"
            t2 = normalize_text(t2).strip() + "\n"
            if t2.strip():
                cleaned_pages.append((page_no, t2))
            break

        end_idx = find_endmatter_start_line_index(t)
        if end_idx is not None:
            if end_idx == 0:
                break
            lines = t.split("\n")
            t2 = "\n".join(lines[:end_idx]).rstrip() + "\n"
            t2 = normalize_text(t2).strip() + "\n"
            if t2.strip():
                cleaned_pages.append((page_no, t2))
            break

        t = normalize_text(t).strip() + "\n"
        if t.strip():
            cleaned_pages.append((page_no, t))

    return chunk_pages_by_sections(cleaned_pages, max_chars=max_chars, max_words=max_words)


def extract_chunks_with_fitz_fallback(
    pdf_path: Path,
    *,
    max_chars: int,
    max_words: int,
) -> List[tuple[int, int, int, str, str]]:
    """Fallback raw PyMuPDF extraction path."""
    doc = fitz.open(str(pdf_path))
    raw_pages: List[tuple[int, str]] = []

    for i, page in enumerate(doc, start=1):
        txt = page.get_text("text")
        if txt and txt.strip():
            raw_pages.append((i, txt))

    doc.close()

    cleaned_pages: List[tuple[int, str]] = []
    for page_no, txt in raw_pages:
        cleaned = clean_chunk_text(txt, remove_tables=True)
        cleaned = remove_consecutive_duplicate_paragraphs(cleaned)
        cleaned = normalize_text(cleaned).strip() + "\n"
        if cleaned.strip():
            cleaned_pages.append((page_no, cleaned))

    return chunk_pages_by_sections(cleaned_pages, max_chars=max_chars, max_words=max_words)