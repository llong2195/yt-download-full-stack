"""Channels API router."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.models.database import get_db
from src.models.schemas import (
    ChannelCreate,
    ChannelUpdate,
    ChannelListResponse,
    ChannelResponse,
)
from src.services import channel_service
from src.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("", response_model=ChannelListResponse)
async def get_channels(db: Session = Depends(get_db)):
    """Get all tracked channels with video counts."""
    try:
        channels = channel_service.get_all_channels_with_stats(db)
        return ChannelListResponse(
            channels=channels,
            total=len(channels),
        )
    except Exception as e:
        logger.exception(f"Error fetching channels: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch channels: {str(e)}",
        )


@router.post(
    "",
    response_model=ChannelResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_channel(
    request: ChannelCreate,
    db: Session = Depends(get_db),
):
    """Add a new channel by URL with custom name and settings."""
    try:
        channel = channel_service.validate_and_add_channel(
            db=db,
            url=request.url,
            custom_name=request.name,
            download_path=request.download_path,
            subtitle_language=request.subtitle_language,
            video_quality=request.video_quality,
        )
        return ChannelResponse(**channel)

    except channel_service.InvalidChannelURLError as e:
        logger.exception(f"Invalid channel URL: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except channel_service.DuplicateChannelError as e:
        logger.exception(f"Duplicate channel error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )

    except channel_service.DuplicateNameError as e:
        logger.exception(f"Duplicate channel name: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )

    except channel_service.ValidationError as e:
        logger.exception(f"Validation error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except channel_service.MetadataFetchError as e:
        logger.exception(f"Metadata fetch error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(e),
        )

    except Exception as e:
        logger.exception(f"Failed to add channel: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add channel: {str(e)}",
        )


@router.put("/{channel_id}", response_model=ChannelResponse)
async def update_channel(
    channel_id: int,
    request: ChannelUpdate,
    db: Session = Depends(get_db),
):
    """Update channel settings."""
    try:
        channel = channel_service.update_channel(
            db=db,
            channel_id=channel_id,
            name=request.name,
            download_path=request.download_path,
            subtitle_language=request.subtitle_language,
            video_quality=request.video_quality,
        )

        if not channel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Channel with ID {channel_id} not found",
            )

        return ChannelResponse(**channel)

    except channel_service.DuplicateNameError as e:
        logger.exception(f"Duplicate channel name: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )

    except channel_service.ValidationError as e:
        logger.exception(f"Validation error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.exception(f"Failed to update channel: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update channel: {str(e)}",
        )


@router.delete("/{channel_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_channel(
    channel_id: int,
    db: Session = Depends(get_db),
):
    """Delete a channel and all its related data."""
    try:
        success = channel_service.delete_channel_with_files(db, channel_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Channel with ID {channel_id} not found",
            )

        return None

    except HTTPException:
        raise

    except Exception as e:
        logger.exception(f"Failed to delete channel: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete channel: {str(e)}",
        )
