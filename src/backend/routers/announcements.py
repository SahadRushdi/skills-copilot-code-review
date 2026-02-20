"""Announcement endpoints for the High School Management System API."""

from datetime import date
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query

from ..database import announcements_collection, teachers_collection

router = APIRouter(
    prefix="/announcements",
    tags=["announcements"]
)


def _validate_date_string(date_value: str, field_name: str) -> date:
    """Parse and validate a YYYY-MM-DD date string."""
    try:
        return date.fromisoformat(date_value)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=f"{field_name} must be in YYYY-MM-DD format"
        ) from exc


def _assert_signed_in_user(username: Optional[str]) -> Dict[str, Any]:
    """Validate signed-in user by username."""
    if not username:
        raise HTTPException(status_code=401, detail="Authentication required")

    teacher = teachers_collection.find_one({"_id": username})
    if not teacher:
        raise HTTPException(status_code=401, detail="Invalid user session")

    return teacher


@router.get("", response_model=List[Dict[str, Any]])
@router.get("/", response_model=List[Dict[str, Any]])
def get_active_announcements() -> List[Dict[str, Any]]:
    """Get currently active announcements for public display."""
    today = date.today()
    announcements: List[Dict[str, Any]] = []

    for announcement in announcements_collection.find({}):
        expiration_date = _validate_date_string(
            announcement["expiration_date"], "expiration_date"
        )
        start_date_str = announcement.get("start_date")
        start_date = (
            _validate_date_string(start_date_str, "start_date")
            if start_date_str else None
        )

        if start_date and start_date > today:
            continue

        if expiration_date < today:
            continue

        announcements.append({
            "id": announcement["_id"],
            "title": announcement["title"],
            "message": announcement["message"],
            "start_date": announcement.get("start_date"),
            "expiration_date": announcement["expiration_date"],
            "created_by": announcement.get("created_by")
        })

    announcements.sort(key=lambda item: (item.get("start_date") or "", item["expiration_date"]))
    return announcements


@router.get("/manage", response_model=List[Dict[str, Any]])
def get_all_announcements(username: str) -> List[Dict[str, Any]]:
    """Get all announcements for management UI (requires authenticated user)."""
    _assert_signed_in_user(username)

    announcements = []
    for announcement in announcements_collection.find({}):
        announcements.append({
            "id": announcement["_id"],
            "title": announcement["title"],
            "message": announcement["message"],
            "start_date": announcement.get("start_date"),
            "expiration_date": announcement["expiration_date"],
            "created_by": announcement.get("created_by")
        })

    announcements.sort(key=lambda item: (item.get("start_date") or "", item["expiration_date"]))
    return announcements


@router.post("")
@router.post("/")
def create_announcement(
    username: str,
    title: str,
    message: str,
    expiration_date: str,
    start_date: Optional[str] = None
) -> Dict[str, str]:
    """Create a new announcement (requires authenticated user)."""
    _assert_signed_in_user(username)

    title = title.strip()
    message = message.strip()

    if not title:
        raise HTTPException(status_code=400, detail="Title is required")
    if not message:
        raise HTTPException(status_code=400, detail="Message is required")

    parsed_expiration = _validate_date_string(expiration_date, "expiration_date")
    parsed_start = _validate_date_string(start_date, "start_date") if start_date else None

    if parsed_start and parsed_start > parsed_expiration:
        raise HTTPException(
            status_code=400,
            detail="start_date cannot be after expiration_date"
        )

    announcement_id = title.lower().replace(" ", "-")

    if announcements_collection.find_one({"_id": announcement_id}):
        raise HTTPException(status_code=409, detail="Announcement title already exists")

    announcements_collection.insert_one({
        "_id": announcement_id,
        "title": title,
        "message": message,
        "start_date": start_date,
        "expiration_date": expiration_date,
        "created_by": username
    })

    return {"message": "Announcement created successfully"}


@router.put("/{announcement_id}")
def update_announcement(
    announcement_id: str,
    username: str,
    title: str,
    message: str,
    expiration_date: str,
    start_date: Optional[str] = None
) -> Dict[str, str]:
    """Update an existing announcement (requires authenticated user)."""
    _assert_signed_in_user(username)

    title = title.strip()
    message = message.strip()

    if not title:
        raise HTTPException(status_code=400, detail="Title is required")
    if not message:
        raise HTTPException(status_code=400, detail="Message is required")

    parsed_expiration = _validate_date_string(expiration_date, "expiration_date")
    parsed_start = _validate_date_string(start_date, "start_date") if start_date else None

    if parsed_start and parsed_start > parsed_expiration:
        raise HTTPException(
            status_code=400,
            detail="start_date cannot be after expiration_date"
        )

    result = announcements_collection.update_one(
        {"_id": announcement_id},
        {
            "$set": {
                "title": title,
                "message": message,
                "start_date": start_date,
                "expiration_date": expiration_date,
                "created_by": username
            }
        }
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Announcement not found")

    return {"message": "Announcement updated successfully"}


@router.delete("/{announcement_id}")
def delete_announcement(announcement_id: str, username: str) -> Dict[str, str]:
    """Delete an announcement (requires authenticated user)."""
    _assert_signed_in_user(username)

    result = announcements_collection.delete_one({"_id": announcement_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Announcement not found")

    return {"message": "Announcement deleted successfully"}
