import pytest
import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_all_books, init_database, add_sample_data, insert_book, get_db_connection
from services.library_service import add_book_to_catalog


class TestR2CatalogDisplay:
    """Test cases for R2: Book Catalog Display"""

    def setup_method(self):
        """Setup test database before each test"""
        init_database()
        # Clear existing data
        conn = get_db_connection()
        conn.execute('DELETE FROM borrow_records')
        conn.execute('DELETE FROM books')
        conn.commit()
        conn.close()

    def test_catalog_display_returns_all_books(self):
        """Test that catalog retrieval returns all books"""
        # Add test books
        insert_book("Test Book 1", "Author 1", "1234567890123", 3, 3)
        insert_book("Test Book 2", "Author 2", "1234567890124", 2, 1)

        books = get_all_books()

        assert len(books) == 2
        assert books[0]['title'] == "Test Book 1"
        assert books[1]['title'] == "Test Book 2"

    def test_catalog_display_shows_correct_format(self):
        """Test catalog returns books with correct display format (ID, title, author, ISBN)"""
        insert_book("Test Title", "Test Author", "1234567890123", 5, 3)

        books = get_all_books()
        book = books[0]

        assert 'id' in book
        assert book['title'] == "Test Title"
        assert book['author'] == "Test Author"
        assert book['isbn'] == "1234567890123"

    def test_catalog_display_shows_available_total_copies(self):
        """Test catalog shows available copies / total copies"""
        insert_book("Copy Test", "Copy Author", "1234567890123", 5, 3)

        books = get_all_books()
        book = books[0]

        assert book['available_copies'] == 3
        assert book['total_copies'] == 5

    def test_catalog_display_borrow_action_available_books(self):
        """Test that books with available copies show borrow action availability"""
        insert_book("Available Book", "Author", "1234567890123", 3, 2)

        books = get_all_books()
        book = books[0]

        assert book['available_copies'] > 0
        # Book should be borrowable when available_copies > 0

    def test_catalog_display_borrow_action_unavailable_books(self):
        """Test that books with no available copies don't show borrow action"""
        insert_book("Unavailable Book", "Author", "1234567890123", 3, 0)

        books = get_all_books()
        book = books[0]

        assert book['available_copies'] == 0
        # Book should not be borrowable when available_copies = 0

    def test_catalog_display_empty_catalog(self):
        """Test catalog display with no books"""
        books = get_all_books()

        assert books == []
        assert len(books) == 0

    