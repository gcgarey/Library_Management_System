# PYTHONPATH=. pytest tests/f1_test.py

import pytest
import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from library_service import add_book_to_catalog
from database import init_database, get_db_connection

class TestF1Requirements:
    """Test cases for F1: Add Book to Catalog"""

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

    def test_add_book_valid_input(self):
        """Test adding a book with valid input."""
        success, message = add_book_to_catalog("Test Book", "Test Author", "1234567890128", 5)

        assert success == True
        assert "successfully added" in message.lower()

    def test_add_book_to_catalog_no_title(self):
        """Test adding a book with no title"""
        success, message = add_book_to_catalog("", "Test Author", 1234567890123, 1)

        assert success == False
        assert "title is required." in message.lower()

    def test_add_book_to_catalog_long_title(self):
        """Test adding a book with a title longer than 200 characters"""
        long_title = "A" * 201
        success, message = add_book_to_catalog(long_title, "Test Author", 1234567890123, 1)

        assert success == False
        assert "title must be less than 200 characters." in message.lower()

    def test_add_book_to_catalog_no_author(self):
        """Test adding a book with no author"""
        success, message = add_book_to_catalog("Test Book", "", 1234567890123, 1)

        assert success == False
        assert "author is required." in message.lower()

    def test_add_book_to_catalog_short_isbn_length(self):
        """Test adding a book with an ISBN that is not 13 digits long"""
        success, message = add_book_to_catalog("Test Book", "Test Author", "123456", 1)

        assert success == False
        assert "isbn must be exactly 13 digits." in message.lower()

