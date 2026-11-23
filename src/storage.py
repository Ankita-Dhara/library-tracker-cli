"""Reading and writing the book collection on disk."""

import csv
import json
import logging
from pathlib import Path

from src.models import Book, InvalidBookError, StorageError

DEFAULT_PATH = Path(__file__).resolve().parent.parent / "data.json"
CSV_COLUMNS = [
    "title", "author", "genre", "total_pages", "status",
    "current_page", "finish_date", "rating", "notes",
]

log = logging.getLogger(__name__)


def load_books(path: Path = DEFAULT_PATH) -> list[Book]:
    """Load books from a JSON file; a missing or blank file means none."""
    if not path.exists():
        return []
    try:
        text = path.read_text(encoding="utf-8")
        raw = json.loads(text) if text.strip() else []
    except (OSError, json.JSONDecodeError) as exc:
        raise StorageError(f"Could not read {path.name}: {exc}") from exc
    if not isinstance(raw, list):
        raise StorageError(f"{path.name} should contain a list of books.")
    try:
        books = [Book.from_dict(item) for item in raw]
    except InvalidBookError as exc:
        raise StorageError(f"{path.name} has a damaged entry: {exc}") from exc
    log.info("loaded %d books from %s", len(books), path.name)
    return books


def save_books(books: list[Book], path: Path = DEFAULT_PATH) -> None:
    """Write books to JSON, replacing the old file only on success."""
    payload = json.dumps([b.to_dict() for b in books], indent=2)
    temp = path.with_suffix(".tmp")
    try:
        temp.write_text(payload, encoding="utf-8")
        temp.replace(path)
    except OSError as exc:
        raise StorageError(f"Could not save {path.name}: {exc}") from exc
    log.info("saved %d books", len(books))


def export_csv(books: list[Book], path: Path) -> None:
    """Write a flat CSV reading report."""
    try:
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS)
            writer.writeheader()
            writer.writerows(b.to_dict() for b in books)
    except OSError as exc:
        raise StorageError(f"Could not write {path.name}: {exc}") from exc
    log.info("exported %d books to %s", len(books), path.name)
