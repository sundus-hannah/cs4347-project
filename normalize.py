"""Normalize library CSV data for CS 4347 Milestone 1.
Usage: python normalize.py --books books-1.csv --borrowers borrowers.csv [--out folder

"""
import csv
import re
import unicodedata
from pathlib import Path
import argparse


def clean(text):
    # Normalize Unicode without removing accented characters.
    text = unicodedata.normalize('NFC', text or '')
    return ' '.join(text.split())


def title_word(word):
    # Capitalize the first letter of each part, so o'brien -> O'Brien and smith-jones -> Smith-Jones.
    parts = re.split(r"(-|')", word.lower())
    for i, part in enumerate(parts):
        after_apostrophe = i >= 2 and parts[i - 1] == "'"
        if part and (not after_apostrophe or len(parts[i - 2]) == 1):
            # Skip leading punctuation such as '(' before the first letter.
            parts[i] = re.sub(r'[^\W\d_]', lambda m: m.group().upper(), part, count=1)
    return ''.join(parts)


def title_case(text):
    # The data mostly uses Every Word Capitalized, so apply that to text written
    # entirely in upper or lower case. Mixed-case names (McDonald, DeLillo) are left alone.
    letters = [c for c in text if c.isupper() or c.islower()]
    if letters and (all(c.isupper() for c in letters) or all(c.islower() for c in letters)):
        return ' '.join(title_word(word) for word in text.split(' '))
    return text


def load_csv(filename):
    with open(filename, encoding='utf-8-sig', newline='') as file:
        first_line = file.readline()
        file.seek(0)
        delimiter = '\t' if '\t' in first_line else ','
        return list(csv.DictReader(file, delimiter=delimiter))


def save_csv(filename, rows):
    with open(filename, 'w', encoding='utf-8', newline='') as file:
        csv.writer(file).writerows(rows)


def process_books(filename):
    books = []
    authors = []
    book_authors = []
    author_ids = {}
    used_isbns = set()

    for line, row in enumerate(load_csv(filename), 2):
        isbn = clean(row['ISBN10']).upper()
        title = title_case(clean(row['Title']))

        # Keep ISBNs as strings to preserve leading zeros and a possible final X.
        if not re.fullmatch(r'[0-9]{9}[0-9X]', isbn):
            raise ValueError(f'Invalid ISBN on line {line}: {isbn}')
        if isbn in used_isbns:
            raise ValueError(f'Duplicate ISBN on line {line}: {isbn}')

        used_isbns.add(isbn)
        books.append([isbn, title])

        author_text = clean(row['Author'])
        if not author_text:
            continue

        names = list(dict.fromkeys(
            title_case(clean(name)) for name in re.split(r'[,;]', author_text) # majority of authors are separated by commas, but some use semicolons
            if clean(name) and clean(name).casefold() != '(none)'  # remove repeated names within a book and the '(None)' placeholder
        ))

        for name in names:
            # Match capitalization variants without altering stored names or punctuation.
            key = name.casefold()
            if key not in author_ids:
                author_ids[key] = len(author_ids) + 1
                authors.append([author_ids[key], name])
            book_authors.append([author_ids[key], isbn])

    return books, authors, book_authors


def process_borrowers(filename):
    borrowers = []
    used_cards = set()

    for line, row in enumerate(load_csv(filename), 2):
        card_id = clean(row['ID0000id'])
        if card_id in used_cards:
            raise ValueError(f'Duplicate card ID on line {line}: {card_id}')
        used_cards.add(card_id)

        name = clean(title_case(clean(row['first_name'])) + ' ' + title_case(clean(row['last_name'])))
        address_parts = [clean(row[col]) for col in ('address', 'city', 'state')]
        address = ', '.join(part for part in address_parts if part)
        borrowers.append([card_id, clean(row['ssn']), name, address, clean(row['phone'])])

    return borrowers


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--books', required=True)
    parser.add_argument('--borrowers', required=True)
    parser.add_argument('--out', default=str(Path(__file__).parent))
    args = parser.parse_args()

    output = Path(args.out)
    output.mkdir(parents=True, exist_ok=True)

    books, authors, book_authors = process_books(args.books)
    borrowers = process_borrowers(args.borrowers)

    save_csv(output / 'books.csv', books)
    save_csv(output / 'authors.csv', authors)
    save_csv(output / 'book_authors.csv', book_authors)
    save_csv(output / 'borrowers.csv', borrowers)

    print(f'Books: {len(books)}')
    print(f'Authors: {len(authors)}')
    print(f'Book-author links: {len(book_authors)}')
    print(f'Borrowers: {len(borrowers)}')


if __name__ == '__main__':
    main()