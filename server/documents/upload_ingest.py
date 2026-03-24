


from pathlib import Path
import tempfile

from pdf_processing.ingest_service import run_one


def _parse_chunk_file(raw_text: str) -> dict:
    """Split a generated chunk file into metadata and cleaned body text."""
    lines = raw_text.splitlines()
    metadata: dict[str, str] = {}
    body_start = 0

    for i, line in enumerate(lines):
        stripped = line.strip()

        if stripped == "---":
            body_start = i + 1
            break

        if stripped == "[TAGS]" or not stripped:
            continue

        if ":" in line:
            key, value = line.split(":", 1)
            metadata[key.strip().lower()] = value.strip()

    body = "\n".join(lines[body_start:]).strip()

    return {
        "metadata": metadata,
        "text": body,
    }


def ingest_uploaded_pdf(uploaded_file) -> list[dict]:
    """Save an uploaded PDF, run the PDF pipeline, and return parsed chunks."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_root = Path(tmpdir)
        pdf_dir = tmp_root / "pdfs"
        out_dir = tmp_root / "txt"

        pdf_dir.mkdir(parents=True, exist_ok=True)
        out_dir.mkdir(parents=True, exist_ok=True)

        pdf_path = pdf_dir / uploaded_file.name
        with pdf_path.open("wb") as f:
            for chunk in uploaded_file.chunks():
                f.write(chunk)

        pdf_out_dir, written = run_one(
            pdf_path,
            out_dir,
            remove_tables=False,
            max_chars=4000,
            max_words=600,
        )

        chunk_data: list[dict] = []

        if written <= 0 or not pdf_out_dir.exists():
            return chunk_data

        for txt_file in sorted(pdf_out_dir.glob("*.txt")):
            raw_content = txt_file.read_text(encoding="utf-8", errors="replace")
            parsed = _parse_chunk_file(raw_content)

            chunk_data.append(
                {
                    "filename": txt_file.name,
                    "metadata": parsed["metadata"],
                    "text": parsed["text"],
                    "raw_content": raw_content,
                }
            )

        return chunk_data