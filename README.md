# Personal Library & Reading Tracker

A small command-line program for keeping track of the books you own and how
far you have got with each one. Data is stored in a local JSON file, so
nothing is lost between runs.

## Features

- Add books with title, author, genre, total pages and status
  (`to-read`, `reading`, `finished`)
- View all books, filtered by status and/or genre
- Update the page you are on; reaching the last page finishes the book
- Mark a book as finished (the finish date is recorded automatically)
- Remove a book
- Case-insensitive partial search on title or author
- Statistics: total books, books finished this year, average pages per
  finished book, favourite genre
- Optional star rating (1-5) and a short note for each book
- Export the whole library to a CSV file

## Requirements

Python 3.10 or newer. The app itself uses only the standard library;
`requirements.txt` lists the tools used for testing and linting.

## Setup

```bash
git clone <your-repository-url>
cd <repository-folder>

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

## Running

```bash
python main.py
```

On the first run `data.json` is created next to `main.py`. Library events
are written to `library.log` in the same folder.

## Project layout

```
main.py            entry point
src/models.py      Book, Status and the custom exceptions
src/library.py     Library: add, find, search, filter, statistics
src/storage.py     JSON load/save and CSV export
src/cli.py         menu and user input handling
```

## Notes

- Book titles are unique (case-insensitive), so every command that asks
  for a title refers to exactly one book.
- If `data.json` is damaged, the program prints what is wrong and exits
  without overwriting the file, so you can fix it by hand.
- `data.json`, `library.log` and exported reports are ignored by Git.
