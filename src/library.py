"""The Library class: holds the books and answers questions about them."""

import logging
from collections import Counter

from src.models import (
    Book,
    BookNotFoundError,
    DuplicateBookError,
    Status,
)

log = logging.getLogger(__name__)


class Library:
    """A collection of books with lookup, filtering and statistics."""

    def __init__(self, books: list[Book] | None = None) -> None:
        self._books: list[Book] = list(books or [])

    @property
    def books(self) -> list[Book]:
        """A copy of the book list, in the order books were added."""
        return list(self._books)

    def add(self, book: Book) -> None:
        """Add a book; titles are unique, ignoring case."""
        if any(b.title.casefold() == book.title.casefold()
               for b in self._books):
            raise DuplicateBookError(f"'{book.title}' is already listed.")
        self._books.append(book)
        log.info("added %s", book)

    def get(self, title: str) -> Book:
        """Return the book with this exact title (case-insensitive)."""
        wanted = title.strip().casefold()
        for book in self._books:
            if book.title.casefold() == wanted:
                return book
        raise BookNotFoundError(f"No book titled '{title.strip()}'.")

    def remove(self, title: str) -> Book:
        """Delete a book by title and hand it back."""
        book = self.get(title)
        self._books.remove(book)
        log.info("removed %s", book)
        return book

    def search(self, term: str) -> list[Book]:
        """Books whose title or author contains the term."""
        term = term.strip().casefold()
        return [
            b for b in self._books
            if term in b.title.casefold() or term in b.author.casefold()
        ]

    def list_books(
        self, status: Status | None = None, genre: str | None = None
    ) -> list[Book]:
        """All books, optionally narrowed by status and/or genre."""
        books = self._books
        if status is not None:
            books = [b for b in books if b.status is status]
        if genre:
            books = [b for b in books
                     if b.genre.casefold() == genre.strip().casefold()]
        return list(books)

    def finished_books(self) -> list[Book]:
        """Every book marked as finished."""
        return self.list_books(status=Status.FINISHED)

    def finished_in_year(self, year: int) -> int:
        """How many books were finished in the given calendar year."""
        return sum(
            1 for b in self.finished_books()
            if b.finish_date and b.finish_date.year == year
        )

    def average_pages_finished(self) -> float:
        """Mean page count of finished books, or 0 when there are none."""
        finished = self.finished_books()
        if not finished:
            return 0.0
        return sum(b.total_pages for b in finished) / len(finished)

    def favorite_genre(self) -> str | None:
        """Genre with the most finished books; None if nothing finished."""
        counts = Counter(b.genre for b in self.finished_books())
        if not counts:
            return None
        return counts.most_common(1)[0][0]
