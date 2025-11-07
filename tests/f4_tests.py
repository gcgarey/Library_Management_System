import pytest 
import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.library_service import return_book_by_patron
from database import init_database, get_db_connection, insert_book, insert_borrow_record, get_book_by_id, get_patron_borrow_count

class TestR4Requirements:
    """Test cases for R4: Book Return Processing"""

    def setup_method(self):
        """Setpu test database before each test"""
        init_database()
        # Clear existing data and reset auto-increment
        conn = get_db_connection()
        conn.execute('DELETE FROM borrow_records')
        conn.execute('DELETE FROM books')
        conn.execute('DELETE FROM sqlite_sequence WHERE name="books"')
        conn.execute('DELETE FROM sqlite_sequence WHERE name="borrow_records"')
        conn.commit()
        conn.close()

    def test_with_incorrect_parameters_for_return_book_functionality(self):
        """Test return book function with incorrect parameters (patron ID, book ID, date returned)"""
        # Add a book and a borrow record
        insert_book("Test Book", "Test Author", "1234567890123", 3, 2)
        insert_borrow_record("123456", 1, datetime.now() - timedelta(days=5), datetime.now() + timedelta(days=9))


        result, message = return_book_by_patron("12345", 1)
        assert result == False

         
    def test_patron_returns_book_after_borrowing(self):
        """Test that patron borrowed the book before returning it --> should succeed"""
        # Add a book and a borrow record"""
        insert_book("Test Book", "Test Author", "1234567890123", 3, 2)
        insert_borrow_record("123456", 1, datetime.now() - timedelta(days=5), datetime.now() + timedelta(days=9))

        # return the book
        result, message = return_book_by_patron("123456", 1)
        assert result == True
        assert "returned successfully" in message.lower()

    def test_patron_returns_book_not_borrowed(self):
        """Test that patron tries to return a book they did not borrow --> should fail"""
        # Add a book but no borrow record
        insert_book("Test Book", "Test Author", "1234567890123", 3, 3)

        # Return the book
        result, message = return_book_by_patron("123456", 1)
        assert result == False

    def test_copies_updated_after_return(self):
        """Test that available copies are updated correctly after a return"""
        # Add a book and a borrow record
        insert_book("Test Book", "Test Author", "1234567890123", 3, 2)
        insert_borrow_record("123456", 1, datetime.now() - timedelta(days=5), datetime.now() + timedelta(days=9))

        # Return the book
        result, message = return_book_by_patron("123456", 1)

        # Verify available copies increased
        book = get_book_by_id(1)
        assert book['available_copies'] == 3

    def test_late_fees_calculated(self):
        """Test that late fees are calculated for overdue returns"""
        # Add a book and a borrow record with past due date
        insert_book("Test Book", "Test Author", "1234567890123", 3, 2)
        insert_borrow_record("123456", 1, datetime.now() - timedelta(days=20), datetime.now() - timedelta(days=6))

        # Return the book
        result, message = return_book_by_patron("123456", 1)

        assert result == True
        assert "late fee" in message.lower()
        assert "$3.00" in message  # $0.50 per day for 6 days late
    
