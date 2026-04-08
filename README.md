# Document Processing Pipeline

**Live API**: https://documentprocessingpipeline-production.up.railway.app

A FastAPI + LangGraph service that processes medical insurance claim PDFs using Gemini's native document understanding. Accepts a PDF and a claim ID, runs a multi-agent extraction pipeline, and returns structured JSON.

## Architecture

```
POST /api/process
        │
        ▼
  Segregator Agent
  (classifies every page into 9 document types)
        │
        ├──────────────────────────────┐──────────────────────────────┐
        ▼                              ▼                              ▼
   ID Agent                   Discharge Agent                  Bill Agent
(identity_document          (discharge_summary               (itemized_bill
  + claim_form pages)             pages)                         pages)
        │                              │                              │
        └──────────────────────────────┴──────────────────────────────┘
                                       │
                                       ▼
                                  Aggregator
                              (merges all results)
                                       │
                                       ▼
                                  Final JSON
```

The 3 extraction agents run in **parallel** (LangGraph fan-out). Each agent receives only its relevant pages — not the full PDF. This is done by splitting the PDF into page-specific byte streams after segregation, so no agent ever sees data it doesn't need.

## Document Types Recognised

`claim_form` · `cheque_or_bank_details` · `identity_document` · `itemized_bill` · `discharge_summary` · `prescription` · `investigation_report` · `cash_receipt` · `other`

## Design Decisions

**Why PyMuPDF only for splitting?**
Gemini processes PDFs natively (vision-based, 258 tokens/page). No OCR pipeline, no pdfplumber, no pytesseract. PyMuPDF is only used to split the PDF bytes by page number before sending to each agent.

**Why `gemini-2.5-flash-lite` for segregation and `gemini-2.5-flash` for extraction?**
Classification is a simpler task — lite is sufficient and cheaper. Extraction requires structured JSON output with cross-referencing across fields, where the full flash model produces more accurate results.

## API

### `POST /api/process`

| Field      | Type            | Description             |
| ---------- | --------------- | ----------------------- |
| `claim_id` | `string` (form) | Unique claim identifier |
| `file`     | `file` (form)   | PDF file to process     |

**Rate limit**: 10 requests/minute per IP.

**Response** (200):

```json
{
  "claim_id": "CLM-001",
  "segregation": {
    "claim_form": [0],
    "cheque_or_bank_details": [1],
    "identity_document": [2],
    "discharge_summary": [3],
    "prescription": [4],
    "investigation_report": [5, 10, 11],
    "cash_receipt": [6],
    "itemized_bill": [8],
    "other": [7, 9, 12, 13, 14, 15, 16, 17, 18]
  },
  "identity": {
    "patient_name": "John Michael Smith",
    "date_of_birth": "March 15, 1985",
    "gender": "Male",
    "id_number": "ID-987-654-321",
    "policy_number": "POL-987654321",
    "insurer_name": "HealthCare Insurance Company",
    "contact_number": "+1-555-0123",
    "address": "456 Oak Street, Apt 12B Springfield, IL 62701"
  },
  "discharge_summary": {
    "patient_name": "John Michael Smith",
    "admission_date": "January 20, 2025",
    "discharge_date": "January 25, 2025",
    "diagnosis": "Community Acquired Pneumonia (CAP)",
    "secondary_diagnosis": [],
    "procedures": [],
    "treating_physician": "Dr. Sarah Johnson, MD",
    "physician_notes": "Patient admitted with fever, cough, and shortness of breath. Chest X-ray confirmed right lower lobe pneumonia. Started on IV antibiotics (Ceftriaxone 1g daily). Patient showed gradual improvement with resolution of fever by day 3. Oxygen saturation improved to 96% on room air. Repeat chest X-ray showed improvement. Condition at Discharge: Stable, improved. Discharge Medications: Amoxicillin 500mg TID x 7 days, Acetaminophen 500mg PRN for pain. Follow-up: Outpatient clinic in 1 week."
  },
  "itemized_bill": {
    "items": [
      {
        "description": "Room Charges - Semi-Private (5 days)",
        "quantity": 5,
        "unit_price": 200.0,
        "amount": 1000.0
      },
      {
        "description": "Admission Fee",
        "quantity": 1,
        "unit_price": 150.0,
        "amount": 150.0
      },
      {
        "description": "Emergency Room Services",
        "quantity": 1,
        "unit_price": 500.0,
        "amount": 500.0
      },
      {
        "description": "Physician Consultation - Dr. Sarah Johnson",
        "quantity": 5,
        "unit_price": 150.0,
        "amount": 750.0
      },
      {
        "description": "Chest X-Ray",
        "quantity": 2,
        "unit_price": 120.0,
        "amount": 240.0
      },
      {
        "description": "CT Scan - Chest",
        "quantity": 1,
        "unit_price": 800.0,
        "amount": 800.0
      },
      {
        "description": "Complete Blood Count (CBC)",
        "quantity": 3,
        "unit_price": 45.0,
        "amount": 135.0
      },
      {
        "description": "Blood Culture Test",
        "quantity": 2,
        "unit_price": 80.0,
        "amount": 160.0
      },
      {
        "description": "Arterial Blood Gas Analysis",
        "quantity": 1,
        "unit_price": 95.0,
        "amount": 95.0
      },
      {
        "description": "IV Fluids - Normal Saline",
        "quantity": 10,
        "unit_price": 25.0,
        "amount": 250.0
      },
      {
        "description": "Injection - Ceftriaxone 1g",
        "quantity": 5,
        "unit_price": 30.0,
        "amount": 150.0
      },
      {
        "description": "Injection - Paracetamol",
        "quantity": 6,
        "unit_price": 8.0,
        "amount": 48.0
      },
      {
        "description": "Nebulization Treatment",
        "quantity": 4,
        "unit_price": 35.0,
        "amount": 140.0
      },
      {
        "description": "Oxygen Therapy (per hour)",
        "quantity": 48,
        "unit_price": 5.0,
        "amount": 240.0
      },
      {
        "description": "Nursing Care (per day)",
        "quantity": 5,
        "unit_price": 100.0,
        "amount": 500.0
      },
      {
        "description": "ICU Monitoring Equipment",
        "quantity": 2,
        "unit_price": 200.0,
        "amount": 400.0
      },
      {
        "description": "Physiotherapy Session",
        "quantity": 3,
        "unit_price": 60.0,
        "amount": 180.0
      },
      {
        "description": "Medical Supplies & Consumables",
        "quantity": 1,
        "unit_price": 250.0,
        "amount": 250.0
      },
      {
        "description": "Laboratory Processing Fee",
        "quantity": 1,
        "unit_price": 75.0,
        "amount": 75.0
      },
      {
        "description": "Pharmacy Dispensing Fee",
        "quantity": 1,
        "unit_price": 50.0,
        "amount": 50.0
      }
    ],
    "subtotal": 6113.0,
    "tax": 305.65,
    "discount": null,
    "total_amount": 6418.65,
    "currency": "USD"
  }
}
```

**Errors**:

- `400` — Not a PDF, exceeds size/page limit
- `429` — Rate limit exceeded
- `500` — Pipeline processing failure

### `GET /health`

Returns `{"status": "ok"}`.

## Setup

```bash
# Clone and install
git clone <repo-url>
cd document_processing_pipeline
uv sync

# Configure
cp .env.example .env
# Set GEMINI_API_KEY in .env

# Run
uv run uvicorn app.main:app --reload --port 8000
```

API docs available at `http://localhost:8000/docs`.

## Configuration

| Variable           | Default                 | Description                   |
| ------------------ | ----------------------- | ----------------------------- |
| `GEMINI_API_KEY`   | —                       | Required. Gemini API key      |
| `SEGREGATOR_MODEL` | `gemini-2.5-flash-lite` | Model for page classification |
| `EXTRACTOR_MODEL`  | `gemini-2.5-flash`      | Model for data extraction     |
| `MAX_PDF_SIZE_MB`  | `50`                    | Maximum PDF file size         |
| `MAX_PDF_PAGES`    | `1000`                  | Maximum PDF page count        |
| `RATE_LIMIT`       | `3/minute`              | Rate limit per IP             |
| `DEBUG`            | `false`                 | Enable debug logging          |

## Stack

- **FastAPI** — API framework
- **LangGraph** — multi-agent workflow orchestration
- **LLM** — Gemini API client (native PDF vision)
- **PyMuPDF** — PDF page splitting only
- **pydantic-settings** — typed config from environment
- **uv** — package management (Python 3.12)

### Docker

```bash
docker build -t document-processing-pipeline .
docker run -p 8000:8000 -e GEMINI_API_KEY=your_key document-processing-pipeline
```
