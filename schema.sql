-- Library Management System schema (CS-4347, Milestone 2)
-- Backwards compatible with the given project schema; adds constraints and indexes.

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS FINES;
DROP TABLE IF EXISTS BOOK_LOANS;
DROP TABLE IF EXISTS BOOK_AUTHORS;
DROP TABLE IF EXISTS AUTHORS;
DROP TABLE IF EXISTS BORROWER;
DROP TABLE IF EXISTS BOOK;

-- ISBN is kept as text so leading zeros and a trailing 'X' are preserved.
CREATE TABLE BOOK (
    Isbn    CHAR(10)  PRIMARY KEY,
    Title   TEXT      NOT NULL
);

CREATE TABLE AUTHORS (
    Author_id  INTEGER  PRIMARY KEY,
    Name       TEXT     NOT NULL
);

-- Many-to-many link between books and authors.
CREATE TABLE BOOK_AUTHORS (
    Author_id  INTEGER   NOT NULL REFERENCES AUTHORS(Author_id),
    Isbn       CHAR(10)  NOT NULL REFERENCES BOOK(Isbn),
    PRIMARY KEY (Author_id, Isbn)
);

-- Name, SSN and address are required. Each SSN may hold only one library card.
CREATE TABLE BORROWER (
    Card_id  CHAR(8)   PRIMARY KEY,          -- format: ID000001
    Ssn      CHAR(11)  NOT NULL UNIQUE,      -- format: 123-45-6789
    Bname    TEXT      NOT NULL,
    Address  TEXT      NOT NULL,
    Phone    TEXT
);

-- Dates are stored as ISO text (YYYY-MM-DD). Date_in is NULL while the book is still out.
CREATE TABLE BOOK_LOANS (
    Loan_id   INTEGER   PRIMARY KEY AUTOINCREMENT,
    Isbn      CHAR(10)  NOT NULL REFERENCES BOOK(Isbn),
    Card_id   CHAR(8)   NOT NULL REFERENCES BORROWER(Card_id),
    Date_out  DATE      NOT NULL,
    Due_date  DATE      NOT NULL,
    Date_in   DATE,
    CHECK (Due_date >= Date_out),
    CHECK (Date_in IS NULL OR Date_in >= Date_out)
);

-- One fine per loan. Fine_amt is a fixed two-decimal dollar amount; Paid is 0/1.
CREATE TABLE FINES (
    Loan_id   INTEGER        PRIMARY KEY REFERENCES BOOK_LOANS(Loan_id),
    Fine_amt  DECIMAL(10,2)  NOT NULL DEFAULT 0.00 CHECK (Fine_amt >= 0),
    Paid      INTEGER        NOT NULL DEFAULT 0 CHECK (Paid IN (0, 1))
);

-- Indexes for search and loan lookups.
CREATE INDEX idx_book_authors_isbn ON BOOK_AUTHORS(Isbn);
CREATE INDEX idx_loans_card        ON BOOK_LOANS(Card_id);
CREATE INDEX idx_loans_isbn        ON BOOK_LOANS(Isbn);

-- A book can have at most one active (not yet returned) loan at a time.
CREATE UNIQUE INDEX idx_one_active_loan_per_book
    ON BOOK_LOANS(Isbn) WHERE Date_in IS NULL;
