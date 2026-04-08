import json
import logging

from app.config import get_settings
from app.services.gemini import get_gemini_client, make_pdf_part
from app.utils.pdf import split_pdf_by_pages
from app.schemas.extraction import ItemizedBillExtraction
from app.workflow.state import PipelineState

logger = logging.getLogger(__name__)

BILL_PROMPT = """You are an expert at extracting itemized billing information from medical documents.

Analyze the provided pages and extract ALL billing information:
- items: List of line items, each with:
  - description: Item or service name
  - quantity: Number of units (null if not specified)
  - unit_price: Price per unit (null if not specified)
  - amount: Total amount for this line item
- subtotal: Subtotal before taxes/discounts (null if not shown)
- tax: Tax amount (null if not shown)
- discount: Discount amount (null if not shown)
- total_amount: Final total amount
- currency: Currency code (default INR)

Extract ALL items from the bill. Calculate total_amount if not explicitly stated.
Be precise with numbers — do not round or estimate."""


def bill_agent_node(state: PipelineState) -> dict[str, ItemizedBillExtraction | None]:
    pages = state["page_classifications"].get("itemized_bill", [])

    if not pages:
        logger.info("No itemized bill pages found, skipping.")
        return {"bill_result": None}

    settings = get_settings()
    client = get_gemini_client()

    page_pdf = split_pdf_by_pages(state["pdf_bytes"], pages)
    pdf_part = make_pdf_part(page_pdf)

    response = client.models.generate_content(
        model=settings.extractor_model,
        contents=[pdf_part, BILL_PROMPT],
        config={
            "response_mime_type": "application/json",
            "response_schema": ItemizedBillExtraction,
        },
    )

    if not response.text:
        logger.warning("Bill agent received empty response from Gemini.")
        return {"bill_result": None}

    result = ItemizedBillExtraction.model_validate(json.loads(response.text))
    logger.info(f"Bill extraction complete: total={result.total_amount}, items={len(result.items)}")

    return {"bill_result": result}
