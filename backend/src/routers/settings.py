"""Settings API router."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.models.database import get_db
from src.models.schemas import GlobalSettingsSchema, GlobalSettingsUpdateSchema
from src.services import settings_service
from src.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("", response_model=GlobalSettingsSchema)
async def get_settings(db: Session = Depends(get_db)):
    """Get global default settings."""
    try:
        settings = settings_service.get_global_settings(db)
        return GlobalSettingsSchema.model_validate(settings)
    except settings_service.SettingsServiceError as e:
        logger.exception(f"Settings error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
    except Exception as e:
        logger.exception(f"Failed to fetch settings: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch settings: {str(e)}",
        )


@router.put("", response_model=GlobalSettingsSchema)
async def update_settings(
    request: GlobalSettingsUpdateSchema,
    db: Session = Depends(get_db),
):
    """Update global default settings."""
    try:
        settings = settings_service.update_global_settings(
            db=db,
            default_download_path=request.default_download_path,
            default_subtitle_language=request.default_subtitle_language,
            default_video_quality=request.default_video_quality,
        )
        return GlobalSettingsSchema.model_validate(settings)
    except settings_service.ValidationError as e:
        logger.exception(f"Validation error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.exception(f"Failed to update settings: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update settings: {str(e)}",
        )
