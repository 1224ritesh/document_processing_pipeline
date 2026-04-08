import json
import logging

from app.config import get_settings
from app.services.gemini import get_gemini_client, make_pdf_part
from app.utils.pdf import split_pdf_by_pages
from app.schemas.extraction import DischargeSummaryExtraction
from app.workflow.state import PipelineState

logger = logging.getLogger(__name__)

DISCHARGE_PROMPT = """You are an expert at extracting discharge summary information from medical documents.

Analyze the provided pages and extract ALL discharge-related information:
- patient_name: Patient name
- admission_date: Date of admission
- discharge_date: Date of discharge
- diagnosis: Primary diagnosis
- secondary_diagnosis: List of secondary diagnoses
- procedures: List of procedures performed
- treating_physician: Name of treating physician
- physician_notes: Any physician notes or clinical summary

Extract exactly what is written. Use null for fields not found. Use empty lists for list fields with no data."""


def discharge_agent_node(state: PipelineState) -> dict[str, DischargeSummaryExtraction | None]:
    pages = state["page_classifications"].get("discharge_summary", [])

    if not pages:
        logger.info("No discharge summary pages found, skipping.")
        return {"discharge_result": None}

    settings = get_settings()
    client = get_gemini_client()

    page_pdf = split_pdf_by_pages(state["pdf_bytes"], pages)
    pdf_part = make_pdf_part(page_pdf)

    response = client.models.generate_content(
        model=settings.extractor_model,
        contents=[pdf_part, DISCHARGE_PROMPT],
        config={
            "response_mime_type": "application/json",
            "response_schema": DischargeSummaryExtraction,
        },
    )

    if not response.text:
        logger.warning("Discharge agent received empty response from Gemini.")
        return {"discharge_result": None}

    result = DischargeSummaryExtraction.model_validate(json.loads(response.text))
    logger.info(f"Discharge extraction complete: diagnosis={result.diagnosis}")

    return {"discharge_result": result}
