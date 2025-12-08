"""Queue API router for monitoring download status."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid
from src.models.database import get_db
from src.models.schemas import (
    QueueStatusResponse,
    DownloadTaskResponse,
    TaskRetryResponse,
)
from src.repository import download_repo
from src.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/status", response_model=QueueStatusResponse)
async def get_queue_status(db: Session = Depends(get_db)):
    """
    Get current queue status with summary stats and active tasks.
    
    Returns:
        - total_pending: Count of tasks with status='pending'
        - total_downloading: Count of tasks with status='downloading'
        - total_completed: Count of completed tasks (today)
        - total_failed: Count of failed tasks (today)
        - active_tasks: List of pending and downloading tasks
    """
    try:
        # Get active tasks (pending + downloading)
        active_tasks = download_repo.get_all_active_tasks(db)
        
        # Count by status
        pending_count = sum(1 for t in active_tasks if t.status == 'pending')
        downloading_count = sum(1 for t in active_tasks if t.status == 'downloading')
        
        # Get completed and failed counts (today)
        from datetime import datetime
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        completed_today = download_repo.get_tasks_by_status(db, 'completed')
        completed_count = sum(
            1 for t in completed_today 
            if t.completed_at and t.completed_at >= today_start
        )
        
        failed_today = download_repo.get_tasks_by_status(db, 'failed')
        failed_count = sum(
            1 for t in failed_today 
            if t.created_at >= today_start
        )
        
        # Convert to response format
        task_responses = [
            DownloadTaskResponse.model_validate(task) 
            for task in active_tasks
        ]
        
        return QueueStatusResponse(
            total_pending=pending_count,
            total_downloading=downloading_count,
            total_completed=completed_count,
            total_failed=failed_count,
            active_tasks=task_responses,
        )
        
    except Exception as e:
        logger.error(f"Failed to get queue status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch queue status: {str(e)}",
        )


@router.get("/tasks/{task_id}", response_model=DownloadTaskResponse)
async def get_task_status(task_id: str, db: Session = Depends(get_db)):
    """
    Get detailed status of a specific task by task_id.
    
    Args:
        task_id: Task UUID string
        
    Returns:
        DownloadTaskResponse with full task details
        
    Raises:
        404: Task not found
    """
    try:
        task = download_repo.get_task_by_task_id(db, task_id)
        
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} not found",
            )
        
        return DownloadTaskResponse.model_validate(task)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get task {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch task status: {str(e)}",
        )


@router.post("/tasks/{task_id}/retry", response_model=TaskRetryResponse)
async def retry_failed_task(task_id: str, db: Session = Depends(get_db)):
    """
    Retry a failed download task.
    
    Args:
        task_id: Task UUID string
        
    Returns:
        TaskRetryResponse with new task_id and success status
        
    Raises:
        404: Task not found
        400: Task cannot be retried (not failed or max retries exceeded)
    """
    try:
        task = download_repo.get_task_by_task_id(db, task_id)
        
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} not found",
            )
        
        # Check if task can be retried
        if task.status != 'failed':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot retry task with status '{task.status}'. Only failed tasks can be retried.",
            )
        
        if task.retry_count >= 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Maximum retry limit (3) exceeded for task {task_id}",
            )
        
        # Reset task to pending status
        new_task_id = str(uuid.uuid4())
        
        # Update existing task
        task.task_id = new_task_id
        task.status = 'pending'
        task.progress_percent = 0
        task.error_message = None
        task.started_at = None
        task.completed_at = None
        task.retry_count += 1
        
        db.commit()
        db.refresh(task)
        
        # Re-enqueue the task
        from src.tasks.download_tasks import download_video
        download_video(task.id)
        
        logger.info(f"Retrying task {task_id} as {new_task_id} (attempt {task.retry_count}/3)")
        
        return TaskRetryResponse(
            success=True,
            new_task_id=new_task_id,
            message=f"Task re-queued successfully. Retry attempt {task.retry_count}/3.",
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retry task {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retry task: {str(e)}",
        )
