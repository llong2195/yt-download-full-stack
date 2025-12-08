"""Channels API router."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from models.database import get_db
from models.schemas import (
    ChannelCreate,
    ChannelResponse,
    ChannelListResponse,
    ErrorResponse,
)
from services import channel_service

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
    """Add a new channel by URL."""
    try:
        channel = channel_service.validate_and_add_channel(db, request.url)
        return ChannelResponse(**channel)

    except channel_service.InvalidChannelURLError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except channel_service.DuplicateChannelError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )

    except channel_service.MetadataFetchError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(e),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add channel: {str(e)}",
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete channel: {str(e)}",
        )
