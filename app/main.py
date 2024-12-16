import logging
import time
from typing import Dict, List
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Path, Request, Response
from fastapi.exceptions import RequestValidationError

from app.models import Receipt
from app.receipt_scorer import ReceiptScorer

app = FastAPI(
    title="Receipt Processor",
    description="A simple receipt processor",
    version="1.0.0",
)

# In memory database
points_db: Dict[str, int] = {}

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("fastapi-logger")


# Override default exception handler so that empty body is returned instead of json with detail key
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return Response(status_code=exc.status_code)


# Override default exception handler so that HTTP 400 with empty body is returned instead 422 with detail
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return Response(status_code=400)


@app.post("/receipts/process", summary="Submits a receipt for processing.")
async def process_receipt(receipt: Receipt):
    """Submits a receipt for processing."""
    try:
        receipt_id = str(uuid4())

        score = ReceiptScorer(receipt).calculate_score()

        # Save the score to the DB
        points_db[receipt_id] = score

        logger.info("Saved receipt with id {id}")

        return {"id": receipt_id}

    except Exception as e:
        logger.error("Invalid receipt", exc_info=True)
        raise HTTPException(status_code=400)


@app.get("/receipts/{id}/points", summary="Returns the points awarded for the receipt.")
async def get_receipt_points(
    id: str = Path(..., pattern=r"^\S+$", description="The ID of the receipt.")
):

    logger.info("Query points for receipt with id {id}")

    if id not in points_db:
        logger.info("Receipt with id {id} not found")
        raise HTTPException(status_code=404)

    return {"points": points_db[id]}


# Simple ping endpoint for health checks
@app.get("/ping")
async def ping():
    return {"message": "pong"}
