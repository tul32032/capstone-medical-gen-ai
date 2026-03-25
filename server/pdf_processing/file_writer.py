import re
from pathlib import Path


def write_md(out_dir: Path, pdf: Path, text: str) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)

    safe_name = re.sub(r"[^A-Za-z0-9._-]+", "_", pdf.stem)
    out_path = out_dir / f"{safe_name}.md"

    header = f"---\nsource: {pdf.name}\n---\n\n"
    body = (text or "").strip()

    out_path.write_text(header + body + "\n", encoding="utf-8", errors="replace")
    return out_path