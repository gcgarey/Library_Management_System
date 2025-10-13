# PYTHONPATH=. pytest tests/f2_test.py
import pytest
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_all_books, init_database, insert_book, get_db_connection


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

    # ==================== POSITIVE TEST CASES ====================

    def test_tc1_1_catalog_display_returns_all_books(self):
        """TC1.1: Test that catalog retrieval returns all books in the database."""
        # Add test books
        insert_book("Test Book 1", "Author 1", "1234567890123", 3, 3)
        insert_book("Test Book 2", "Author 2", "1234567890124", 2, 1)

        books = get_all_books()

        assert len(books) == 2
        assert books[0]['title'] == "Test Book 1"
        assert books[1]['title'] == "Test Book 2"

    def test_tc1_2_catalog_display_shows_correct_format(self):
        """TC1.2: Test catalog returns books with all required fields (ID, title, author, ISBN)."""
        insert_book("Test Title", "Test Author", "1234567890123", 5, 3)

        books = get_all_books()
        book = books[0]

        assert 'id' in book
        assert 'title' in book
        assert 'author' in book
        assert 'isbn' in book
        assert book['title'] == "Test Title"
        assert book['author'] == "Test Author"
        assert book['isbn'] == "1234567890123"

    def test_tc1_3_catalog_display_shows_available_total_copies(self):
        """TC1.3: Test catalog shows available copies and total copies for each book."""
        insert_book("Copy Test", "Copy Author", "1234567890123", 5, 3)

        books = get_all_books()
        book = books[0]

        assert 'available_copies' in book
        assert 'total_copies' in book
        assert book['available_copies'] == 3
        assert book['total_copies'] == 5

    def test_tc1_4_catalog_display_multiple_books_correct_order(self):
        """TC1.4: Test that multiple books are displayed in the correct order."""
        insert_book("Book A", "Author A", "1111111111111", 1, 1)
        insert_book("Book B", "Author B", "2222222222222", 2, 2)
        insert_book("Book C", "Author C", "3333333333333", 3, 3)

        books = get_all_books()

        assert len(books) == 3
        assert books[0]['title'] == "Book A"
        assert books[1]['title'] == "Book B"
        assert books[2]['title'] == "Book C"

    def test_tc1_5_catalog_display_single_book(self):
        """TC1.5: Test catalog display with exactly one book."""
        insert_book("Single Book", "Single Author", "9999999999999", 10, 5)

        books = get_all_books()

        assert len(books) == 1
        assert books[0]['title'] == "Single Book"
        assert books[0]['available_copies'] == 5
        assert books[0]['total_copies'] == 10

    # ==================== AVAILABLE COPIES SCENARIOS ====================

    def test_tc2_1_catalog_display_book_with_all_copies_available(self):
        """TC2.1: Test display of book where all copies are available."""
        insert_book("All Available", "Author", "1234567890123", 5, 5)

        books = get_all_books()
        book = books[0]

        assert book['available_copies'] == 5
        assert book['total_copies'] == 5
        assert book['available_copies'] == book['total_copies']

    def test_tc2_2_catalog_display_book_with_some_copies_available(self):
        """TC2.2: Test display of book where some copies are available."""
        insert_book("Partially Available", "Author", "1234567890123", 10, 6)

        books = get_all_books()
        book = books[0]

        assert book['available_copies'] == 6
        assert book['total_copies'] == 10
        assert book['available_copies'] < book['total_copies']
        assert book['available_copies'] > 0

    def test_tc2_3_catalog_display_book_with_no_copies_available(self):
        """TC2.3: Test display of book where no copies are available."""
        insert_book("All Borrowed", "Author", "1234567890123", 5, 0)

        books = get_all_books()
        book = books[0]

        assert book['available_copies'] == 0
        assert book['total_copies'] == 5
        assert book['available_copies'] < book['total_copies']

    def test_tc2_4_catalog_display_book_with_one_copy_available(self):
        """TC2.4: Test display of book with exactly one copy available (boundary case)."""
        insert_book("One Available", "Author", "1234567890123", 3, 1)

        books = get_all_books()
        book = books[0]

        assert book['available_copies'] == 1
        assert book['total_copies'] == 3

    def test_tc2_5_catalog_display_book_with_one_total_copy(self):
        """TC2.5: Test display of book with exactly one total copy."""
        insert_book("Single Copy Book", "Author", "1234567890123", 1, 1)

        books = get_all_books()
        book = books[0]

        assert book['available_copies'] == 1
        assert book['total_copies'] == 1

    # ==================== BORROW ACTION AVAILABILITY ====================

    def test_tc3_1_borrow_action_available_for_books_with_copies(self):
        """TC3.1: Test that books with available copies can show borrow action."""
        insert_book("Borrowable Book", "Author", "1234567890123", 3, 2)

        books = get_all_books()
        book = books[0]

        assert book['available_copies'] > 0
        # Book should be eligible for borrow action

    def test_tc3_2_borrow_action_unavailable_for_books_without_copies(self):
        """TC3.2: Test that books with no available copies cannot show borrow action."""
        insert_book("Non-Borrowable Book", "Author", "1234567890123", 3, 0)

        books = get_all_books()
        book = books[0]

        assert book['available_copies'] == 0
        # Book should not be eligible for borrow action

    def test_tc3_3_borrow_action_multiple_books_mixed_availability(self):
        """TC3.3: Test borrow action for multiple books with mixed availability."""
        insert_book("Available Book 1", "Author 1", "1111111111111", 5, 3)
        insert_book("Unavailable Book", "Author 2", "2222222222222", 2, 0)
        insert_book("Available Book 2", "Author 3", "3333333333333", 4, 1)

        books = get_all_books()

        # Verify we have books with mixed availability
        available_books = [b for b in books if b['available_copies'] > 0]
        unavailable_books = [b for b in books if b['available_copies'] == 0]

        assert len(available_books) == 2  # Two books can be borrowed
        assert len(unavailable_books) == 1  # One book cannot be borrowed

    # ==================== EDGE CASES ====================

    def test_tc4_1_catalog_display_empty_catalog(self):
        """TC4.1: Test catalog display with no books in the database."""
        books = get_all_books()

        assert books == []
        assert len(books) == 0
        assert isinstance(books, list)

    def test_tc4_2_catalog_display_book_with_large_copy_count(self):
        """TC4.2: Test display of book with very large number of copies."""
        insert_book("Many Copies", "Author", "1234567890123", 999999, 500000)

        books = get_all_books()
        book = books[0]

        assert book['available_copies'] == 500000
        assert book['total_copies'] == 999999

    def test_tc4_3_catalog_display_book_with_special_characters_in_title(self):
        """TC4.3: Test display of book with special characters in title."""
        insert_book("Book: A Journey! @2024 #1", "Author", "1234567890123", 5, 5)

        books = get_all_books()
        book = books[0]

        assert book['title'] == "Book: A Journey! @2024 #1"
        assert book['available_copies'] == 5

    def test_tc4_4_catalog_display_book_with_unicode_characters(self):
        """TC4.4: Test display of book with Unicode characters."""
        insert_book("日本語のタイトル", "José García", "1234567890123", 3, 2)

        books = get_all_books()
        book = books[0]

        assert book['title'] == "日本語のタイトル"
        assert book['author'] == "José García"
        assert book['available_copies'] == 2

    def test_tc4_5_catalog_display_books_with_same_title_different_isbn(self):
        """TC4.5: Test display of books with same title but different ISBNs."""
        insert_book("Duplicate Title", "Author 1", "1111111111111", 3, 3)
        insert_book("Duplicate Title", "Author 2", "2222222222222", 2, 1)

        books = get_all_books()

        assert len(books) == 2
        assert books[0]['title'] == "Duplicate Title"
        assert books[1]['title'] == "Duplicate Title"
        assert books[0]['isbn'] != books[1]['isbn']

    def test_tc4_6_catalog_display_very_long_title_and_author(self):
        """TC4.6: Test display of book with maximum length title and author."""
        long_title = "A" * 200
        long_author = "B" * 100
        insert_book(long_title, long_author, "1234567890123", 5, 3)

        books = get_all_books()
        book = books[0]

        assert len(book['title']) == 200
        assert len(book['author']) == 100
        assert book['available_copies'] == 3

    # ==================== DATA INTEGRITY ====================

    def test_tc5_1_catalog_display_verifies_all_required_fields_present(self):
        """TC5.1: Test that all required fields are present in catalog response."""
        insert_book("Complete Book", "Complete Author", "1234567890123", 5, 3)

        books = get_all_books()
        book = books[0]

        required_fields = ['id', 'title', 'author', 'isbn', 'total_copies', 'available_copies']
        for field in required_fields:
            assert field in book, f"Required field '{field}' is missing"

    def test_tc5_2_catalog_display_verifies_data_types(self):
        """TC5.2: Test that catalog returns correct data types for each field."""
        insert_book("Type Test", "Author", "1234567890123", 5, 3)

        books = get_all_books()
        book = books[0]

        assert isinstance(book['id'], int)
        assert isinstance(book['title'], str)
        assert isinstance(book['author'], str)
        assert isinstance(book['isbn'], str)
        assert isinstance(book['total_copies'], int)
        assert isinstance(book['available_copies'], int)

    def test_tc5_3_catalog_display_validates_available_never_exceeds_total(self):
        """TC5.3: Test that available copies never exceeds total copies."""
        insert_book("Book 1", "Author 1", "1111111111111", 10, 5)
        insert_book("Book 2", "Author 2", "2222222222222", 3, 3)
        insert_book("Book 3", "Author 3", "3333333333333", 7, 0)

        books = get_all_books()

        for book in books:
            assert book['available_copies'] <= book['total_copies'], \
                f"Book '{book['title']}' has more available copies than total copies"

    def test_tc5_4_catalog_display_validates_non_negative_copies(self):
        """TC5.4: Test that copy counts are non-negative."""
        insert_book("Book 1", "Author 1", "1111111111111", 5, 2)
        insert_book("Book 2", "Author 2", "2222222222222", 3, 0)

        books = get_all_books()

        for book in books:
            assert book['available_copies'] >= 0, \
                f"Book '{book['title']}' has negative available copies"
            assert book['total_copies'] >= 0, \
                f"Book '{book['title']}' has negative total copies"

    # ==================== LARGE DATASET SCENARIOS ====================

    def test_tc6_1_catalog_display_handles_many_books(self):
        """TC6.1: Test catalog display with a large number of books."""
        # Insert 50 books
        for i in range(50):
            isbn = f"{1000000000000 + i:013d}"
            insert_book(f"Book {i+1}", f"Author {i+1}", isbn, 5, 3)

        books = get_all_books()

        assert len(books) == 50
        # Verify all books are present by checking titles
        titles = [book['title'] for book in books]
        assert "Book 1" in titles
        assert "Book 50" in titles

    def test_tc6_2_catalog_display_books_added_at_different_times(self):
        """TC6.2: Test that catalog displays books added at different times."""
        insert_book("First Book", "Author 1", "1111111111111", 3, 3)
        
        books = get_all_books()
        assert len(books) == 1

        insert_book("Second Book", "Author 2", "2222222222222", 2, 1)
        
        books = get_all_books()
        assert len(books) == 2
        assert books[0]['title'] == "First Book"
        assert books[1]['title'] == "Second Book"

    # ==================== ISBN VARIATIONS ====================

    def test_tc7_1_catalog_display_isbn_with_leading_zeros(self):
        """TC7.1: Test display of book with ISBN containing leading zeros."""
        insert_book("Zero ISBN", "Author", "0000000000123", 5, 3)

        books = get_all_books()
        book = books[0]

        assert book['isbn'] == "0000000000123"
        assert len(book['isbn']) == 13

    def test_tc7_2_catalog_display_isbn_all_same_digits(self):
        """TC7.2: Test display of book with ISBN containing all same digits."""
        insert_book("Same Digit ISBN", "Author", "1111111111111", 5, 3)

        books = get_all_books()
        book = books[0]

        assert book['isbn'] == "1111111111111"

    def test_tc7_3_catalog_display_multiple_books_sequential_isbn(self):
        """TC7.3: Test display of books with sequential ISBNs."""
        insert_book("Book 1", "Author", "1234567890120", 5, 3)
        insert_book("Book 2", "Author", "1234567890121", 5, 3)
        insert_book("Book 3", "Author", "1234567890122", 5, 3)

        books = get_all_books()

        assert len(books) == 3
        assert books[0]['isbn'] == "1234567890120"
        assert books[1]['isbn'] == "1234567890121"
        assert books[2]['isbn'] == "1234567890122"