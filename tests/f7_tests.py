import pytest
import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from library_service import get_patron_status_report
from database import init_database, get_db_connection, insert_book, insert_borrow_record

class TestR7Requirements:
    """Test cases for R7: Patron Status Report"""

    def setup_method(self):
        """Setup test database before each test"""
        init_database()
        # Clear existing data and reset auto-increment
        conn = get_db_connection()
        conn.execute('DELETE FROM borrow_records')
        conn.execute('DELETE FROM books')
        conn.execute('DELETE FROM sqlite_sequence WHERE name="books"')
        conn.execute('DELETE FROM sqlite_sequence WHERE name="borrow_records"')
        conn.commit()
        conn.close()

    def test_status_report_with_no_borrowed_books(self):
        """Test status report for patron with no borrowed books"""
        report = get_patron_status_report("123456")
        assert report["currently_borrowed_due_dates"] == ""
        assert report["late_fees"] == 0.0
        assert report["number_of_books_borrowed"] == 0

    def test_status_report_with_currently_borrowed_books(self):
        """Test status report showing currently borrowed books with due dates"""
        # Add books to catalog
        insert_book("1984", "George Orwell", "1234567890123", 2, 2)
        insert_book("Brave New World", "Aldous Huxley", "1234567890124", 1, 1)

        # Create borrow records
        borrow_date = datetime.now()
        due_date = borrow_date + timedelta(days=14)
        insert_borrow_record("123456", 1, borrow_date, due_date)
        insert_borrow_record("123456", 2, borrow_date, due_date)

        report = get_patron_status_report("123456")
        assert report["number_of_books_borrowed"] == 2
        assert "1984" in report["currently_borrowed_due_dates"]
        assert "Brave New World" in report["currently_borrowed_due_dates"]

    def test_status_report_calculates_total_late_fees(self):
        """Test status report calculates total late fees owed across all books"""
        # Add book to catalog
        insert_book("Overdue Book", "Test Author", "1234567890123", 1, 1)

        # Create overdue borrow record (30 days overdue)
        borrow_date = datetime.now() - timedelta(days=44)  # 44 days ago, so 30 days overdue
        due_date = borrow_date + timedelta(days=14)
        insert_borrow_record("123456", 1, borrow_date, due_date)

        borrow_date_2 = datetime.now() - timedelta(days=20)  # 20 days ago, so 6 days overdue
        due_date_2 = borrow_date_2 + timedelta(days=14)
        insert_borrow_record("123456", 1, borrow_date_2, due_date_2)

        report = get_patron_status_report("123456")
        # Should calculate late fees: capped at $15.00 * 2 books
        assert report["late_fees"] == 30.00

    def test_displays_number_of_books_currently_borrowed(self):
        """Test status report displays correct number of books currently borrowed"""
        # Add books to catalog
        insert_book("Book One", "Author A", "1234567890123", 2, 2)
        insert_book("Book Two", "Author B", "1234567890124", 1, 1)
        insert_borrow_record("123456", 1, datetime.now(), datetime.now() + timedelta(days=14))
        insert_borrow_record("123456", 2, datetime.now(), datetime.now() + timedelta(days=14))
        report = get_patron_status_report("123456")
        assert report["number_of_books_borrowed"] == 2
