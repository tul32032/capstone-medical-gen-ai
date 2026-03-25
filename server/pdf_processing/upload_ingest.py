from pathlib import Path
import tempfile

from pdf_processing.ingest_service import run_one


def ingest_uploaded_pdf(uploaded_file) -> str | None:
    """
    Save an uploaded PDF, run the markdown pipeline,
    and return the generated markdown text.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_root = Path(tmpdir)
        pdf_dir = tmp_root / "pdfs"
        out_dir = tmp_root / "md"

        pdf_dir.mkdir(parents=True, exist_ok=True)
        out_dir.mkdir(parents=True, exist_ok=True)

        pdf_path = pdf_dir / uploaded_file.name
        with pdf_path.open("wb") as f:
            for chunk in uploaded_file.chunks():
                f.write(chunk)

        output_path = run_one(
            pdf_path,
            out_dir,
            remove_tables=False,
        )

        if not output_path or not output_path.exists():
            return None

        return output_path.read_text(encoding="utf-8", errors="replace")