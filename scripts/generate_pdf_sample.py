"""Generate a PDF copy of fnol_001 for PDF parsing demos."""

from pathlib import Path

from fpdf import FPDF

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "samples" / "fnol_001_fast_track.txt"
TARGET = ROOT / "samples" / "fnol_001_fast_track.pdf"


def main() -> None:
    text = SOURCE.read_text(encoding="utf-8")
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", size=10)
    for line in text.splitlines():
        safe = line if line.strip() else " "
        pdf.multi_cell(w=190, h=6, text=safe)
    pdf.output(str(TARGET))
    print(f"Wrote {TARGET}")


if __name__ == "__main__":
    main()
