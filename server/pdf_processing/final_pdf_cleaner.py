from pathlib import Path

from .ingest_service import run_one


def main() -> int:
    remove_tables = False
    max_chars = 4000
    max_words = 600

    gdrive_root = Path.home() / "Google Drive" / "My Drive" / "GEN AI TEST"
    pdf_dir = gdrive_root / "pdfs"
    out_dir = gdrive_root / "txt"
    done_dir = gdrive_root / "done"
    failed_dir = gdrive_root / "failed"

    if not gdrive_root.exists() or not gdrive_root.is_dir():
        print(f"ERROR: Google Drive folder is not valid: {gdrive_root}")
        return 2

    if not pdf_dir.exists() or not pdf_dir.is_dir():
        print(f"ERROR: PDF directory is not valid: {pdf_dir}")
        print("Create a 'pdfs' folder inside your GEN AI TEST Google Drive folder and place PDFs there.")
        return 2

    done_dir.mkdir(parents=True, exist_ok=True)
    failed_dir.mkdir(parents=True, exist_ok=True)

    pdfs = sorted(p for p in pdf_dir.iterdir() if p.suffix.lower() == ".pdf")
    if not pdfs:
        print(f"ERROR: No .pdf files found in: {pdf_dir}")
        return 2

    print(f"PDF source: {pdf_dir}")
    print(f"Output directory: {out_dir}")

    for pdf_path in pdfs:
        print(f"\n=== {pdf_path.name} ===")
        try:
            pdf_out_dir, written = run_one(
                pdf_path,
                out_dir,
                remove_tables=remove_tables,
                max_chars=max_chars,
                max_words=max_words,
            )

            if written > 0:
                target_path = done_dir / pdf_path.name
                pdf_path.replace(target_path)
                print(f"Saved {written} chunks to: {pdf_out_dir}")
                print(f"Moved to done: {target_path}")
            else:
                target_path = failed_dir / pdf_path.name
                pdf_path.replace(target_path)
                print(f"No chunks were saved for {pdf_path.name}")
                print(f"Moved to failed: {target_path}")
        except Exception as e:
            target_path = failed_dir / pdf_path.name
            try:
                if pdf_path.exists():
                    pdf_path.replace(target_path)
            except Exception as move_err:
                print(f"ERROR moving failed file {pdf_path.name}: {move_err}")
            print(f"ERROR extracting {pdf_path.name}: {e}")
            print(f"Moved to failed: {target_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())