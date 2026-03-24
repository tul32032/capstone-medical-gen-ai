import re
from pathlib import Path
from typing import List


def write_chunks(
    out_root: Path,
    pdf_path: Path,
    chunks: List[tuple[int, int, int, str, str]],
) -> tuple[Path, int]:
    out_root.mkdir(parents=True, exist_ok=True)

    safe_stem = re.sub(r"[^A-Za-z0-9._-]+", "_", pdf_path.stem)
    pdf_out_dir = out_root / safe_stem
    pdf_out_dir.mkdir(parents=True, exist_ok=True)

    pdf_name = pdf_path.name

    prepared_chunks: List[tuple[int, int, str, str]] = []

    for chunk_no, page_start, _page_end, text, section in chunks:
        is_small = len(text.strip()) < 250 or len(re.findall(r"\S+", text)) < 50

        if is_small and prepared_chunks:
            prev_chunk_no, prev_page_start, prev_text, prev_section = prepared_chunks[-1]
            merged_text = (prev_text.rstrip() + "\n\n" + text.strip()).rstrip() + "\n"
            prepared_chunks[-1] = (prev_chunk_no, prev_page_start, merged_text, prev_section)
        else:
            prepared_chunks.append((chunk_no, page_start, text, section))

    written = 0
    for chunk_no, page_start, text, section in prepared_chunks:
        tag_lines: List[str] = [
            "[TAGS]",
            f"Source: {pdf_name}",
            f"Page: {page_start}",
            f"Section: {section}",
        ]
        tag_lines += ["---", ""]

        safe_section = re.sub(r"[^A-Za-z0-9._-]+", "_", section)[:40] or "Unknown"
        chunk_path = pdf_out_dir / f"{safe_stem}_{chunk_no}_{safe_section}.txt"
        chunk_path.write_text(
            "\n".join(tag_lines) + text,
            encoding="utf-8",
            errors="replace",
        )
        written += 1

    return pdf_out_dir, written