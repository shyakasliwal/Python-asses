# Autonomous Insurance Claims Processing Agent

A lightweight Python agent that processes **First Notice of Loss (FNOL)** documents: extracts structured fields, flags gaps and inconsistencies, and routes claims to the appropriate workflow with a short explanation.

## Approach

1. **Document ingestion** — Plain text (`.txt`) and PDF (`.pdf`) files are loaded; PDF text is extracted with `pypdf`.
2. **Field extraction** — Label-based regex patterns map FNOL sections to a canonical JSON schema (policy, incident, parties, asset, and mandatory metadata).
3. **Validation** — Mandatory fields are checked; placeholder values (`N/A`, `Unknown`, `TBD`, etc.) count as missing. Numeric damage and initial estimate are parsed for consistency checks.
4. **Routing** — Rules are applied in priority order:
   - **Investigation Flag** — Description contains `fraud`, `inconsistent`, or `staged`
   - **Specialist Queue** — Claim type is injury-related
   - **Manual Review** — Any mandatory field missing or estimates materially inconsistent
   - **Fast-track** — All fields present and estimated damage &lt; £25,000
   - **Standard Processing** — Otherwise (e.g. high-value complete claims)

## Project structure

```
├── main.py                 # CLI
├── requirements.txt
├── samples/                # 5 dummy FNOL documents (4 scenarios + fast-track PDF)
├── scripts/
│   └── generate_pdf_sample.py
├── src/
│   ├── agent.py            # Orchestration
│   ├── document_loader.py
│   ├── extractor.py
│   ├── models.py
│   └── router.py
└── output/                 # JSON results (created when running --samples)
```

## Requirements

- Python 3.10+
- Dependencies in `requirements.txt`

## Setup

```bash
cd d:\Asses
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux
pip install -r requirements.txt
```

Optional: generate the PDF sample from the fast-track TXT file:

```bash
python scripts/generate_pdf_sample.py
```

## Run

**Single document:**

```bash
python main.py samples/fnol_001_fast_track.txt
```

**All samples (writes JSON to `output/`):**

```bash
python main.py --samples
```

**PDF example (after running the generate script):**

```bash
python main.py samples/fnol_001_fast_track.pdf
```

## Output format

```json
{
  "extractedFields": { "...": "..." },
  "missingFields": ["incidentTime"],
  "recommendedRoute": "Manual Review",
  "reasoning": "Mandatory fields missing or incomplete: ..."
}
```

## Sample scenarios

| File | Expected route |
|------|----------------|
| `fnol_001_fast_track.txt` | Fast-track (£12,500 damage, complete) |
| `fnol_002_high_damage.txt` | Standard Processing (£48,000) |
| `fnol_003_incomplete.txt` | Manual Review (missing/placeholder fields) |
| `fnol_004_investigation.txt` | Investigation Flag (`staged`, `inconsistent`) |
| `fnol_005_injury.txt` | Specialist Queue (injury claim type) |

## Extending the agent

- Add new label patterns in `src/extractor.py` (`FIELD_PATTERNS`).
- Adjust thresholds and keywords in `src/models.py` and `src/router.py`.
- For unstructured or scanned FNOLs, plug in an LLM or OCR layer before `extract_fields()`.

## License

Assessment submission — use and modify as needed.
