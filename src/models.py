"""Book model, reading status and the custom exceptions for the app."""

from datetime import date
from enum import Enum


class LibraryError(Exception):
    """Base class for every error this application raises on purpose."""


class BookNotFoundError(LibraryError):
    """Raised when no book in the library has the requested title."""


class DuplicateBookError(LibraryError):
    """Raised when a book with the same title is already in the library."""


class InvalidBookError(LibraryError):
    """Raised when book details or a progress update are not valid."""


class StorageError(LibraryError):
    """Raised when the data file cannot be read, parsed or written."""


class Status(Enum):
    """Where a book currently sits in the reading cycle."""

    TO_READ = "to-read"
    READING = "reading"
    FINISHED = "finished"

    @classmethod
    def parse(cls, text: str) -> "Status":
        """Turn user text such as 'Reading' into a Status."""
        try:
            return cls(text.strip().lower())
        except ValueError:
            options = ", ".join(item.value for item in cls)
            raise InvalidBookError(
                f"Status must be one of: {options}."
            ) from None


def _required_text(value: str, label: str) -> str:
    text = value.strip()
    if not text:
        raise InvalidBookError(f"{label} cannot be empty.")
    return text


class Book:
    """A single book and how far the reader has got with it."""

    def __init__(
        self,
        title: str,
        author: str,
        genre: str,
        total_pages: int,
        status: Status = Status.TO_READ,
        current_page: int = 0,
        finish_date: date | None = None,
        rating: int | None = None,
        notes: str = "",
    ) -> None:
        self.title = _required_text(title, "Title")
        self.author = _required_text(author, "Author")
        self.genre = _required_text(genre, "Genre").title()
        if total_pages < 1:
            raise InvalidBookError("Total pages must be at least 1.")
        self.total_pages = total_pages
        self.notes = notes.strip()
        self.rating: int | None = None
        if rating is not None:
            self.set_rating(rating)

        if status is Status.TO_READ:
            current_page = 0
        elif status is Status.FINISHED:
            current_page = total_pages
            finish_date = finish_date or date.today()
        elif not 0 <= current_page < total_pages:
            raise InvalidBookError(
                f"A book in progress needs a page from 0 to "
                f"{total_pages - 1}."
            )
        self._status = status
        self._current_page = current_page
        self.finish_date = finish_date if status is Status.FINISHED else None

    @property
    def status(self) -> Status:
        """Current reading status."""
        return self._status

    @property
    def current_page(self) -> int:
        """Page the reader has reached."""
        return self._current_page

    @property
    def percent_read(self) -> int:
        """Whole-number percentage of the book that has been read."""
        return self._current_page * 100 // self.total_pages

    def update_progress(self, page: int) -> None:
        """Move the bookmark; reaching the last page finishes the book."""
        if self._status is Status.FINISHED:
            raise InvalidBookError(f"'{self.title}' is already finished.")
        if not 1 <= page <= self.total_pages:
            raise InvalidBookError(
                f"Page must be between 1 and {self.total_pages}."
            )
        if page == self.total_pages:
            self.finish()
            return
        self._current_page = page
        self._status = Status.READING

    def finish(self, on: date | None = None) -> None:
        """Mark the book as finished and record the date."""
        self._status = Status.FINISHED
        self._current_page = self.total_pages
        self.finish_date = on or date.today()

    def set_rating(self, rating: int) -> None:
        """Store a 1 to 5 star rating."""
        if not 1 <= rating <= 5:
            raise InvalidBookError("Rating must be between 1 and 5.")
        self.rating = rating

    def to_dict(self) -> dict:
        """Return a JSON-friendly dictionary for this book."""
        return {
            "title": self.title,
            "author": self.author,
            "genre": self.genre,
            "total_pages": self.total_pages,
            "status": self._status.value,
            "current_page": self._current_page,
            "finish_date": (
                self.finish_date.isoformat() if self.finish_date else None
            ),
            "rating": self.rating,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Book":
        """Rebuild a book from the dictionary written by to_dict."""
        try:
            raw_date = data.get("finish_date")
            return cls(
                title=data["title"],
                author=data["author"],
                genre=data["genre"],
                total_pages=data["total_pages"],
                status=Status.parse(data["status"]),
                current_page=data.get("current_page", 0),
                finish_date=date.fromisoformat(raw_date) if raw_date else None,
                rating=data.get("rating"),
                notes=data.get("notes", ""),
            )
        except (KeyError, TypeError, ValueError, AttributeError) as exc:
            raise InvalidBookError(f"Bad book record: {exc!r}") from exc

    def __str__(self) -> str:
        return f"{self.title} by {self.author}"
