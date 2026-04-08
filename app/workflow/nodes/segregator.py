import json
import logging

from app.config import get_settings
from app.services.gemini import get_gemini_client, make_pdf_part
from app.schemas.document_types import DocumentType
from app.schemas.extraction import SegregationResult
from app.workflow.state import PipelineState

logger = logging.getLogger(__name__)

SEGREGATION_PROMPT = """You are a medical document classifier. Analyze this PDF and classify EACH page 
into exactly one of these document types:

- claim_form
- cheque_or_bank_details
- identity_document
- itemized_bill
- discharge_summary
- prescription
- investigation_report
- cash_receipt
- other

For EVERY page in the document, provide:
- page_number (zero-indexed)
- document_type (one of the types above)
- confidence (0.0 to 1.0)

Analyze visual layout, headers, content patterns, and form structures to classify accurately."""


def segregator_node(state: PipelineState) -> dict[str, dict[str, list[int]]]:
    settings = get_settings()
    client = get_gemini_client()

    pdf_part = make_pdf_part(state["pdf_bytes"])

    response = client.models.generate_content(
        model=settings.segregator_model,
        contents=[pdf_part, SEGREGATION_PROMPT],
        config={
            "response_mime_type": "application/json",
            "response_schema": SegregationResult,
        },
    )

    if not response.text:
        logger.warning("Segregator received empty response from Gemini.")
        return {"page_classifications": {}}

    result = SegregationResult.model_validate(json.loads(response.text))

    # Build mapping: document_type -> list of page numbers
    page_map: dict[str, list[int]] = {dt.value: [] for dt in DocumentType}
    for classification in result.classifications:
        doc_type = classification.document_type.value
        page_map[doc_type].append(classification.page_number)

    # Remove empty types for cleaner state
    page_map = {k: v for k, v in page_map.items() if v}

    logger.info("Segregation complete: %s", {k: len(v) for k, v in page_map.items()})

    return {"page_classifications": page_map}
