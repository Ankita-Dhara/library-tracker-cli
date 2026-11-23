"""Menu-driven command line interface."""

from datetime import date
from pathlib import Path

from src.library import Library
from src.models import Book, LibraryError, Status
from src.storage import DEFAULT_PATH, export_csv, save_books

MENU = """
Personal Library
  1. Add a book
  2. View books
  3. Update reading progress
  4. Mark a book as finished
  5. Remove a book
  6. Search by title or author
  7. Statistics
  8. Rate / review a book
  9. Export to CSV
  0. Quit
"""


def _fit(text: str, width: int) -> str:
    return text if len(text) <= width else text[: width - 3] + "..."


class LibraryApp:
    """Ties the menu to a Library and saves after every change."""

    def __init__(self, library: Library, data_path: Path = DEFAULT_PATH):
        self.library = library
        self.data_path = data_path
        self.actions = {
            "1": self.add_book,
            "2": self.view_books,
            "3": self.update_progress,
            "4": self.finish_book,
            "5": self.remove_book,
            "6": self.search_books,
            "7": self.show_stats,
            "8": self.review_book,
            "9": self.export_report,
        }

    def run(self) -> None:
        """Show the menu until the user quits."""
        while True:
            print(MENU)
            try:
                choice = input("Choose: ").strip()
                if choice == "0":
                    break
                action = self.actions.get(choice)
                if action is None:
                    print("Please pick a number from the menu.")
                    continue
                action()
            except LibraryError as exc:
                print(f"Error: {exc}")
            except (EOFError, KeyboardInterrupt):
                print()
                break
        print("Bye!")

    def add_book(self) -> None:
        """Ask for the details of a new book and add it."""
        title = input("Title: ")
        author = input("Author: ")
        genre = input("Genre: ")
        pages = self._ask_int("Total pages: ", 1)
        status = Status.parse(
            input("Status (to-read / reading / finished) [to-read]: ")
            or "to-read"
        )
        page, finished_on = 0, None
        if status is Status.READING:
            page = self._ask_int("Current page: ", 0, pages - 1)
        elif status is Status.FINISHED:
            finished_on = self._ask_date("Finish date (YYYY-MM-DD) [today]: ")
        self.library.add(
            Book(title, author, genre, pages, status, page, finished_on)
        )
        self._save()
        print("Book added.")

    def view_books(self) -> None:
        """List books, optionally filtered by status and genre."""
        status_text = input("Filter by status (blank for all): ").strip()
        genre = input("Filter by genre (blank for all): ").strip()
        status = Status.parse(status_text) if status_text else None
        self._print_table(self.library.list_books(status, genre))

    def update_progress(self) -> None:
        """Record the page the reader has reached."""
        book = self.library.get(input("Book title: "))
        page = self._ask_int(
            f"Current page (1-{book.total_pages}): ", 1, book.total_pages
        )
        book.update_progress(page)
        self._save()
        if book.finish_date:
            print(f"That was the last page. Finished on {book.finish_date}.")
        else:
            print(f"Now at page {page} ({book.percent_read}%).")

    def finish_book(self) -> None:
        """Mark a book finished as of today."""
        book = self.library.get(input("Book title: "))
        book.finish()
        self._save()
        print(f"Finished '{book.title}' on {book.finish_date}.")

    def remove_book(self) -> None:
        """Delete a book after confirmation."""
        book = self.library.get(input("Book title: "))
        answer = input(f"Remove '{book.title}'? (y/n): ").strip().lower()
        if answer != "y":
            print("Nothing removed.")
            return
        self.library.remove(book.title)
        self._save()
        print("Book removed.")

    def search_books(self) -> None:
        """Search by part of a title or author."""
        term = input("Search for: ")
        self._print_table(self.library.search(term))

    def show_stats(self) -> None:
        """Print the summary figures."""
        lib = self.library
        favorite = lib.favorite_genre() or "none yet"
        print(f"Total books:               {len(lib.books)}")
        print(f"Finished this year:        "
              f"{lib.finished_in_year(date.today().year)}")
        print(f"Avg pages per finished:    {lib.average_pages_finished():.0f}")
        print(f"Favorite genre:            {favorite}")

    def review_book(self) -> None:
        """Attach a star rating and a note to a book."""
        book = self.library.get(input("Book title: "))
        book.set_rating(self._ask_int("Rating (1-5): ", 1, 5))
        book.notes = input("Notes (optional): ").strip()
        self._save()
        print("Saved your review.")

    def export_report(self) -> None:
        """Write the whole library to a CSV file."""
        name = input("File name [reading_report.csv]: ").strip()
        path = Path(name or "reading_report.csv")
        export_csv(self.library.books, path)
        print(f"Exported {len(self.library.books)} books to {path}.")

    def _save(self) -> None:
        save_books(self.library.books, self.data_path)

    @staticmethod
    def _ask_int(prompt: str, low: int, high: int | None = None) -> int:
        while True:
            raw = input(prompt).strip()
            try:
                value = int(raw)
            except ValueError:
                print("Please enter a whole number.")
                continue
            if value < low or (high is not None and value > high):
                limit = f"{low} or more" if high is None else f"{low}-{high}"
                print(f"The number must be {limit}.")
                continue
            return value

    @staticmethod
    def _ask_date(prompt: str) -> date:
        while True:
            raw = input(prompt).strip()
            if not raw:
                return date.today()
            try:
                return date.fromisoformat(raw)
            except ValueError:
                print("Use the format YYYY-MM-DD, e.g. 2026-03-14.")

    @staticmethod
    def _print_table(books: list[Book]) -> None:
        if not books:
            print("No books found.")
            return
        print(f"{'#':>3}  {'Title':<26} {'Author':<18} {'Genre':<11} "
              f"{'Status':<9} {'Progress':<14} Rating")
        for number, book in enumerate(books, start=1):
            progress = (f"{book.current_page}/{book.total_pages} "
                        f"({book.percent_read}%)")
            stars = f"{book.rating}/5" if book.rating else "-"
            print(f"{number:>3}  {_fit(book.title, 26):<26} "
                  f"{_fit(book.author, 18):<18} {_fit(book.genre, 11):<11} "
                  f"{book.status.value:<9} {progress:<14} {stars}")
