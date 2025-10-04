import logging
from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from starlette.concurrency import run_in_threadpool

from pathlib import Path

from api.v1.models.db import WhaleTransactionRepository

logger = logging.getLogger("API")
app = FastAPI()
repo = WhaleTransactionRepository()

@app.get("/transactions/recent")
async def get_recent_transactions(hours: int = Query(1, ge=1)):
    """ FOR EXAMPLE: GET /transactions/recent?hours=3 """
    return await run_in_threadpool(repo.get_transactions_since, hours)

@app.get("/transactions/last")
async def get_last_transactions(n: int = Query(50, ge=1, le=500)):
    """EXAMPLE USAGE: GET /transactions/last?n=100"""
    return await run_in_threadpool(repo.get_last_n_transactions, n)

@app.get("/report")
async def get_ai_report():
    root_dir = Path(__file__).resolve().parents[2]
    report_path = root_dir / "report.html"
    if not report_path.exists():
        logger.error(f"File {report_path} not found")
        return {"error": f"File {report_path} not found"}
    return FileResponse(report_path)