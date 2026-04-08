import json
import logging

from app.config import get_settings
from app.services.gemini import get_gemini_client, make_pdf_part
from app.utils.pdf import split_pdf_by_pages
from app.schemas.extraction import IdentityExtraction
from app.workflow.state import PipelineState

logger = logging.getLogger(__name__)

IDENTITY_PROMPT = """You are an expert at extracting identity information from medical claim documents.

You are given pages from identity documents AND claim forms. Extract ALL identity-related information 
by combining data from both sources:
- patient_name: Full name of the patient
- date_of_birth: Date of birth (any format found)
- gender: Gender
- id_number: Any government ID number (Aadhaar, PAN, passport, etc.)
- policy_number: Insurance policy number (often found on claim forms)
- insurer_name: Insurance company name (often found on claim forms)
- contact_number: Phone number
- address: Full address

Cross-reference across all pages. Policy and insurer details are typically on claim forms, 
while personal ID details are on identity documents. Extract exactly what is written. Use null for fields not found."""

# Page types that carry identity/policy information
ID_PAGE_TYPES = ["identity_document", "claim_form"]


def id_agent_node(state: PipelineState) -> dict[str, IdentityExtraction | None]:
    pages: list[int] = []
    for doc_type in ID_PAGE_TYPES:
        pages.extend(state["page_classifications"].get(doc_type, []))

    if not pages:
        logger.info("No identity/claim form pages found, skipping.")
        return {"identity_result": None}

    settings = get_settings()
    client = get_gemini_client()

    # Route only relevant pages — not the full PDF
    page_pdf = split_pdf_by_pages(state["pdf_bytes"], pages)
    pdf_part = make_pdf_part(page_pdf)

    response = client.models.generate_content(
        model=settings.extractor_model,
        contents=[pdf_part, IDENTITY_PROMPT],
        config={
            "response_mime_type": "application/json",
            "response_schema": IdentityExtraction,
        },
    )

    if not response.text:
        logger.warning("ID agent received empty response from Gemini.")
        return {"identity_result": None}

    result = IdentityExtraction.model_validate(json.loads(response.text))
    logger.info(f"ID extraction complete: patient={result.patient_name}")

    return {"identity_result": result}
