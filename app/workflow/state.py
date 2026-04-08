from typing import TypedDict
from app.schemas.extraction import (
    IdentityExtraction,
    DischargeSummaryExtraction,
    ItemizedBillExtraction,
)


class PipelineState(TypedDict):

    # Input
    claim_id: str
    pdf_bytes: bytes

    # Segregator output
    page_classifications: dict[str, list[int]] 

    # Extraction outputs
    identity_result: IdentityExtraction | None
    discharge_result: DischargeSummaryExtraction | None
    bill_result: ItemizedBillExtraction | None

    # Final
    final_output: dict[str, str]
