import pytest
import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.library_service import search_books_in_catalog
from database import init_database, get_db_connection, insert_book

class TestR6Requirements:
    """Test cases for R6: Book Search Functionality"""

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

    def test_has_parameter_q_and_type(self):
        """Test that the function has parameters q and search_type"""
        assert search_books_in_catalog.__code__.co_varnames[0] == 'q'
        assert search_books_in_catalog.__code__.co_varnames[1] == 'search_type'

    def test_partial_matching_for_title_search(self):
        """Test partial matching for title search"""
        # Add books to the database
        insert_book("The Great Gatsby", "F. Scott Fitzgerald", "1234567890123", 3, 3)
        insert_book("Great Expectations", "Charles Dickens", "1234567890124", 2, 2)

        result = search_books_in_catalog("Great", "title")
        titles = [book['title'] for book in result]
        assert "The Great Gatsby" in titles and "Great Expectations" in titles

    def test_exact_matching_for_isbn_search_compete(self):
        """Test exact matching for ISBN search"""
        insert_book("1984", "George Orwell", "1234567890123", 4, 4)
        insert_book("Brave New World", "Aldous Huxley", "1234567890124", 5, 5)

        result = search_books_in_catalog("1234567890123", "isbn")
        titles = [book['title'] for book in result]
        assert "1984" in titles
    
    def test_isbn_exact_matching_search_partial(self):
        """Test that partial matching for ISBN search returns no results"""
        insert_book("1984", "George Orwell", "1234567890123", 4, 4)
        insert_book("Brave New World", "Aldous Huxley", "1234567890124", 5, 5)

        result = search_books_in_catalog("1234567890", "isbn")
        assert result == []

    def test_result_in_same_format_as_catalog_display(self):
        """Test that search results are in the same format as catalog display"""
        insert_book("To Kill a Mockingbird", "Harper Lee", "1234567890123", 3, 3)

        result = search_books_in_catalog("To Kill a Mockingbird", "title")
        assert isinstance(result, list)
        assert 'id' in result[0]
        assert 'title' in result[0]
        assert 'author' in result[0]
        assert 'isbn' in result[0]
        assert 'available_copies' in result[0]
        assert 'total_copies' in result[0]


    