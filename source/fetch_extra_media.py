from datetime import datetime, timedelta, timezone
import requests

def _auth_headers(api_token: str) -> dict:
    return {
        "X-Emby-Token": api_token,
        "X-Emby-Authorization": 'MediaBrowser Client="newsletter", Device="newsletter", DeviceId="newsletter", Version="0.1"'
    }

def _is_from_watched_folder(item: dict, watched_folder_names: list[str]) -> bool:
    path = (item.get("Path") or "").rstrip("/\\")
    last = path.split("/")[-1].split("\\")[-1]
    return last in set(watched_folder_names or [])

def _recent_items(base_url: str, api_token: str, include_types: list[str], limit: int = 1000):
    url = f"{base_url.rstrip('/')}/Items"
    params = {
        "Recursive": "true",
        "IncludeItemTypes": ",".join(include_types),
        "SortBy": "DateCreated",
        "SortOrder": "Descending",
        "Limit": str(limit),
        "Fields": "Path,DateCreated,PremiereDate,ProductionYear,Overview,ImageTags,ParentId,Album,Artists,SeriesName,ProviderIds"
    }
    resp = requests.get(url, headers=_auth_headers(api_token), params=params, timeout=30)
    resp.raise_for_status()
    return resp.json().get("Items", [])

def _parse_date(dt_str: str | None):
    if not dt_str:
        return None
    try:
        return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    except Exception:
        return None

def _img_url(base_url: str, item: dict, max_height: int = 600) -> str | None:
    tags = item.get("ImageTags") or {}
    if "Primary" in tags:
        return f"{base_url.rstrip('/')}/Items/{item['Id']}/Images/Primary?maxHeight={max_height}&quality=90&tag={tags['Primary']}"
    return None

def get_recent_music_albums(base_url: str, api_token: str, watched_music_folders: list[str], observed_days: int):
    since = datetime.now(timezone.utc) - timedelta(days=observed_days or 30)
    items = _recent_items(base_url, api_token, include_types=["MusicAlbum"])
    albums = []
    for it in items:
        created = _parse_date(it.get("DateCreated") or it.get("PremiereDate"))
        if not created or created < since:
            continue
        if watched_music_folders and not _is_from_watched_folder(it, watched_music_folders):
            continue
        albums.append({
            "id": it["Id"],
            "name": it.get("Name"),
            "artist": ", ".join(it.get("Artists") or []),
            "year": it.get("ProductionYear"),
            "overview": it.get("Overview"),
            "image": _img_url(base_url, it),
            "link": f"{base_url.rstrip('/')}/web/index.html#!/details?id={it['Id']}",
        })
    return albums

def get_recent_books(base_url: str, api_token: str, watched_book_folders: list[str], observed_days: int):
    since = datetime.now(timezone.utc) - timedelta(days=observed_days or 30)
    items = _recent_items(base_url, api_token, include_types=["Book", "AudioBook"])
    books = []
    for it in items:
        created = _parse_date(it.get("DateCreated") or it.get("PremiereDate"))
        if not created or created < since:
            continue
        if watched_book_folders and not _is_from_watched_folder(it, watched_book_folders):
            continue
        author = ", ".join(it.get("Artists") or []) or None
        books.append({
            "id": it["Id"],
            "title": it.get("Name"),
            "author": author,
            "year": it.get("ProductionYear"),
            "overview": it.get("Overview"),
            "image": _img_url(base_url, it),
            "link": f"{base_url.rstrip('/')}/web/index.html#!/details?id={it['Id']}",
        })
    return books
