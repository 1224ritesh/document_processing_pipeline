import logging

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import get_settings
from app.utils.pdf import validate_pdf
from app.workflow.graph import workflow

logger = logging.getLogger(__name__)
router = APIRouter()

limiter = Limiter(key_func=get_remote_address)


@router.post("/process")
@limiter.limit(get_settings().rate_limit)
async def process_claim(
    request: Request,
    claim_id: str = Form(..., description="Unique claim identifier"),
    file: UploadFile = File(..., description="PDF file to process"),
):
    # Validate file type
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    if file.content_type and file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    # Read and validate PDF
    pdf_bytes = await file.read()
    settings = get_settings()

    try:
        validate_pdf(pdf_bytes, settings.max_pdf_size_mb, settings.max_pdf_pages)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Run the LangGraph pipeline
    logger.info(f"Processing claim {claim_id}, file: {file.filename}")

    try:
        result = await workflow.ainvoke(
            {
                "claim_id": claim_id,
                "pdf_bytes": pdf_bytes,
            }
        )
    except Exception as e:
        logger.exception(f"Pipeline failed for claim {claim_id}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

    return result["final_output"]
