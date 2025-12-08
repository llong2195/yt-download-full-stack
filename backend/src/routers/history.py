"""History router for download history endpoints."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from src.models import get_db
from src.models.schemas import (
    DownloadHistoryResponse,
    ErrorResponse,
    HistoryListResponse,
    HistoryStatsResponse,
)
from src.repository import download_repo
from src.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get(
    "",
    response_model=HistoryListResponse,
    responses={500: {"model": ErrorResponse}},
)
async def get_history(
    search: Optional[str] = Query(None, description="Search in video titles"),
    date_from: Optional[str] = Query(
        None, description="Filter by download date >= this date (ISO format)"
    ),
    date_to: Optional[str] = Query(
        None, description="Filter by download date <= this date (ISO format)"
    ),
    success: Optional[bool] = Query(None, description="Filter by success status"),
    limit: int = Query(100, ge=1, le=500, description="Maximum records to return"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    db: Session = Depends(get_db),
):
    """Get download history with search and filters.

    Args:
        search: Search in video titles (case-insensitive)
        date_from: Filter by download_date >= date_from (ISO format: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)
        date_to: Filter by download_date <= date_to (ISO format)
        success: Filter by success status (true/false)
        limit: Maximum number of records to return (1-500)
        offset: Number of records to skip for pagination
        db: Database session

    Returns:
        HistoryListResponse with history records and pagination metadata
    """
    try:
        # Parse date strings if provided
        parsed_date_from = None
        parsed_date_to = None

        if date_from:
            try:
                parsed_date_from = datetime.fromisoformat(date_from)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid date_from format: {date_from}. Use ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)",
                )

        if date_to:
            try:
                parsed_date_to = datetime.fromisoformat(date_to)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid date_to format: {date_to}. Use ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)",
                )

        # Get history with filters
        history_records, total_count = download_repo.get_history_with_filters(
            db=db,
            search=search,
            date_from=parsed_date_from,
            date_to=parsed_date_to,
            success=success,
            limit=limit,
            offset=offset,
        )

        # Convert to response models
        history_responses = [
            DownloadHistoryResponse.model_validate(record) for record in history_records
        ]

        # Build filters_applied dict
        filters_applied = {}
        if search:
            filters_applied["search"] = search
        if date_from:
            filters_applied["date_from"] = date_from
        if date_to:
            filters_applied["date_to"] = date_to
        if success is not None:
            filters_applied["success"] = success

        return HistoryListResponse(
            history=history_responses,
            total=total_count,
            limit=limit,
            offset=offset,
            filters_applied=filters_applied,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to get download history: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/stats",
    response_model=HistoryStatsResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def get_history_stats(
    period: str = Query(
        "all", description="Time period for stats (7d, 30d, 90d, all)"
    ),
    db: Session = Depends(get_db),
):
    """Get download history statistics.

    Args:
        period: Time period for stats (7d, 30d, 90d, all)
        db: Database session

    Returns:
        HistoryStatsResponse with aggregated statistics
    """
    # Validate period
    valid_periods = ["7d", "30d", "90d", "all"]
    if period not in valid_periods:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid period: {period}. Must be one of {valid_periods}",
        )

    try:
        stats = download_repo.get_history_stats(db=db, period=period)
        return HistoryStatsResponse(**stats )

    except Exception as e:
        logger.exception(f"Failed to get download history stats: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
