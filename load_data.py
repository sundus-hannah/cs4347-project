"""Create the library database and load the normalized Milestone 1 CSV files.

Usage: python load_data.py [--data data] [--db library.db]

The CSV files have no header rows:
    books.csv         Isbn, Title
    authors.csv       Author_id, Name
    book_authors.csv  Author_id, Isbn
    borrowers.csv     Card_id, Ssn, Bname, Address, Phone
"""
import argparse
import csv
from pathlib import Path

from db import get_connection
from normalize import title_case  # same case rules as Milestone 1

HERE = Path(__file__).parent


def read_csv(path):
    with open(path, encoding='utf-8', newline='') as file:
        return [row for row in csv.reader(file) if row]


def create_schema(conn):
    conn.executescript((HERE / 'schema.sql').read_text(encoding='utf-8'))


def load(conn, data_dir):
    books = [(isbn, title_case(title)) for isbn, title in read_csv(data_dir / 'books.csv')]
    authors = [(int(aid), title_case(name)) for aid, name in read_csv(data_dir / 'authors.csv')]
    book_authors = [(int(aid), isbn) for aid, isbn in read_csv(data_dir / 'book_authors.csv')]
    borrowers = [(card, ssn, title_case(name), address, phone)
                 for card, ssn, name, address, phone in read_csv(data_dir / 'borrowers.csv')]

    with conn:  # one transaction: all rows load or none do
        conn.executemany('INSERT INTO BOOK (Isbn, Title) VALUES (?, ?)', books)
        conn.executemany('INSERT INTO AUTHORS (Author_id, Name) VALUES (?, ?)', authors)
        conn.executemany('INSERT INTO BOOK_AUTHORS (Author_id, Isbn) VALUES (?, ?)', book_authors)
        conn.executemany('INSERT INTO BORROWER (Card_id, Ssn, Bname, Address, Phone) '
                         'VALUES (?, ?, ?, ?, ?)', borrowers)


def main():
    parser = argparse.ArgumentParser(description='Build library.db from the Milestone 1 CSV files.')
    parser.add_argument('--data', default=str(HERE / 'data'), help='folder containing the CSV files')
    parser.add_argument('--db', default=str(HERE / 'library.db'), help='database file to create')
    args = parser.parse_args()

    conn = get_connection(args.db)
    create_schema(conn)
    load(conn, Path(args.data))

    for table in ('BOOK', 'AUTHORS', 'BOOK_AUTHORS', 'BORROWER', 'BOOK_LOANS', 'FINES'):
        count = conn.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]
        print(f'{table:<13} {count:>6} rows')
    conn.close()
    print(f'Database created: {args.db}')


if __name__ == '__main__':
    main()
