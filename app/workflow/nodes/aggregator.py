import logging

from app.schemas.extraction import ProcessingResult
from app.workflow.state import PipelineState

logger = logging.getLogger(__name__)


def aggregator_node(state: PipelineState) -> dict[str, dict]:
    result = ProcessingResult(
        claim_id=state["claim_id"],
        segregation=state["page_classifications"],
        identity=state.get("identity_result"),
        discharge_summary=state.get("discharge_result"),
        itemized_bill=state.get("bill_result"),
    )

    logger.info(f"Aggregation complete for claim {state['claim_id']}")

    return {"final_output": result.model_dump()}
