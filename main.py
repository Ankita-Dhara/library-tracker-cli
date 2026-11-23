"""Entry point: python main.py"""

import logging
import sys
from pathlib import Path

from src.cli import LibraryApp
from src.library import Library
from src.models import StorageError
from src.storage import load_books


def main() -> int:
    """Load the saved collection and start the menu."""
    logging.basicConfig(
        filename=Path(__file__).resolve().parent / "library.log",
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    try:
        library = Library(load_books())
    except StorageError as exc:
        print(f"Cannot start: {exc}")
        return 1
    LibraryApp(library).run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
