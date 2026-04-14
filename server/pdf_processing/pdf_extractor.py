from pathlib import Path
from typing import Any, Callable, List

import pymupdf4llm


def make_single_page(text: Any) -> List[dict[str, Any]]:
    return [{"page": 1, "text": str(text), "metadata": {}}]


def normalize_pages(pages: Any) -> List[dict[str, Any]]:
    """Normalize extracted per-page output into page dictionaries."""

    def get_text(page_dict: dict[str, Any]) -> str:
        text = page_dict.get("text") or page_dict.get("content") or page_dict.get("markdown") or page_dict.get("md")
        if isinstance(text, str) and text.strip():
            return text

        blocks = page_dict.get("blocks")
        if isinstance(blocks, list):
            parts: List[str] = []
            for block in blocks:
                if isinstance(block, dict):
                    block_text = (
                        block.get("text")
                        or block.get("content")
                        or block.get("span")
                        or block.get("value")
                    )
                    if isinstance(block_text, str) and block_text.strip():
                        parts.append(block_text)
            if parts:
                return "\n".join(parts)

        for key in ("page_text", "raw_text", "raw", "data"):
            value = page_dict.get(key)
            if isinstance(value, str) and value.strip():
                return value

        return ""

    def get_page_no(page_dict: dict[str, Any], default_no: int) -> int:
        metadata = page_dict.get("metadata", {})

        for source in (page_dict, metadata):
            for key in ("page", "page_num", "page_number", "pageno", "pageIndex"):
                value = source.get(key)
                if isinstance(value, int) and value > 0:
                    return value
                if isinstance(value, str) and value.isdigit():
                    page_no = int(value)
                    if page_no > 0:
                        return page_no

        return default_no

    if isinstance(pages, str):
        return [{"page": 1, "text": pages, "metadata": {}}]

    if isinstance(pages, dict):
        page_list = pages.get("pages") or pages.get("page_chunks")
        if isinstance(page_list, list):
            pages = page_list
        else:
            return make_single_page(pages)

    if not isinstance(pages, list):
        return make_single_page(pages)

    items: List[dict[str, Any]] = []
    for idx, page_item in enumerate(pages, start=1):
        if isinstance(page_item, dict):
            metadata = page_item.get("metadata", {})
            if not isinstance(metadata, dict):
                metadata = {}
            items.append(
                {
                    "page": get_page_no(page_item, idx),
                    "text": get_text(page_item),
                    "metadata": metadata,
                }
            )
        elif isinstance(page_item, str):
            items.append({"page": idx, "text": page_item, "metadata": {}})
        else:
            items.append({"page": idx, "text": str(page_item), "metadata": {}})

    return items


def extract_with_llm(
    pdf_path: Path,
    extractor: Callable[..., Any],
    label: str,
) -> List[dict[str, Any]] | None:
    try:
        raw_pages = extractor(
            str(pdf_path),
            page_chunks=True,
        )
        return normalize_pages(raw_pages)
    except Exception as err:
        print(f"[fallback] {label} extraction failed for {pdf_path.name}: {err}")
        return None



def extract_markdown_pages(pdf_path: Path) -> List[dict[str, Any]]:
    """Extract a PDF page by page with markdown first and raw-text fallbacks."""
    pdf_path = Path(pdf_path)

    markdown_pages = extract_with_llm(
        pdf_path,
        lambda path, page_chunks: pymupdf4llm.to_markdown(
            path,
            page_chunks=page_chunks,
            table_strategy="none",
        ),
        "markdown",
    )
    if markdown_pages is not None:
        return markdown_pages

    raw_pages = extract_with_llm(
        pdf_path,
        pymupdf4llm.to_text,
        "raw",
    )
    if raw_pages is not None:
        return raw_pages

    return []