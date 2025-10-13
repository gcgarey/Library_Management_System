import pytest
import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from library_service import borrow_book_by_patron
from database import init_database, get_db_connection, insert_book, insert_borrow_record, get_book_by_id, get_patron_borrow_count


class TestR3Requirements:
    """Test cases for R3: Book Borrowing by Patrons"""

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

    def test_borrowing_interface_valid_patron_id_and_available_book(self):
        """Test successful borrowing with valid 6-digit patron ID and available book"""
        # Add a book with available copies
        insert_book("Test Book", "Test Author", "1234567890123", 3, 3)

        result, message = borrow_book_by_patron("123456", 1)

        assert result == True
        assert "Successfully borrowed" in message
        assert "Test Book" in message

        # Verify available copies decreased
        book = get_book_by_id(1)
        assert book['available_copies'] == 2

    def test_patron_id_validation_exactly_6_digits(self):
        """Test patron ID must be exactly 6 digits"""
        insert_book("Test Book", "Test Author", "1234567890123", 3, 3)

        # Test valid 6-digit ID
        result, message = borrow_book_by_patron("123456", 1)
        assert result == True

    def test_patron_id_validation_rejects_non_digits(self):
        """Test patron ID rejection for non-digit characters"""
        insert_book("Test Book", "Test Author", "1234567890123", 3, 3)

        result, message = borrow_book_by_patron("12345a", 1)
        assert result == False
        assert "Invalid patron ID" in message

    def test_patron_id_validation_rejects_too_short(self):
        """Test patron ID rejection for less than 6 digits"""
        insert_book("Test Book", "Test Author", "1234567890123", 3, 3)

        result, message = borrow_book_by_patron("12345", 1)
        assert result == False
        assert "Invalid patron ID" in message

    def test_book_availability_check_available_book(self):
        """Test borrowing succeeds when book has available copies"""
        insert_book("Available Book", "Author", "1234567890123", 2, 2)

        result, message = borrow_book_by_patron("123456", 1)
        assert result == True

        # Verify copies decreased
        book = get_book_by_id(1)
        assert book['available_copies'] == 1

    def test_borrowing_record_creation(self):
        """Test that borrowing creates proper borrow record"""
        insert_book("Record Test", "Author", "1234567890123", 3, 3)

        result, message = borrow_book_by_patron("123456", 1)
        assert result == True

        # Verify borrow count increased
        count = get_patron_borrow_count("123456")
        assert count == 1
