# PYTHONPATH=. pytest tests/f6_test.py
import pytest
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from library_service import search_books_in_catalog
from database import init_database, get_db_connection, insert_book


class TestR6BookSearch:
    """Test cases for R6: Book Search Functionality"""

    def setup_method(self):
        """Setup test database before each test"""
        init_database()
        # Clear existing data
        conn = get_db_connection()
        conn.execute('DELETE FROM borrow_records')
        conn.execute('DELETE FROM books')
        conn.commit()
        conn.close()

    # ==================== POSITIVE TEST CASES - TITLE SEARCH ====================

    def test_tc1_1_search_title_exact_match(self):
        """TC1.1: Verify exact title match returns correct book."""
        with patch('library_service.search_books', return_value=[
            {'id': 1, 'title': 'The Great Gatsby', 'author': 'F. Scott Fitzgerald', 
             'isbn': '9780743273565', 'total_copies': 5, 'available_copies': 3}
        ]):
            results = search_books_in_catalog("The Great Gatsby", "title")
            
            assert len(results) == 1
            assert results[0]['title'] == 'The Great Gatsby'

    def test_tc1_2_search_title_partial_match(self):
        """TC1.2: Verify partial title match returns matching books."""
        with patch('library_service.search_books', return_value=[
            {'id': 1, 'title': 'The Great Gatsby', 'author': 'F. Scott Fitzgerald', 
             'isbn': '9780743273565', 'total_copies': 5, 'available_copies': 3},
            {'id': 2, 'title': 'The Great Expectations', 'author': 'Charles Dickens',
             'isbn': '9780141439563', 'total_copies': 3, 'available_copies': 2}
        ]):
            results = search_books_in_catalog("Great", "title")
            
            assert len(results) == 2
            assert all('Great' in book['title'] for book in results)

    def test_tc1_3_search_title_case_insensitive(self):
        """TC1.3: Verify title search is case-insensitive."""
        with patch('library_service.search_books', return_value=[
            {'id': 1, 'title': 'The Great Gatsby', 'author': 'F. Scott Fitzgerald', 
             'isbn': '9780743273565', 'total_copies': 5, 'available_copies': 3}
        ]):
            # Search with lowercase
            results = search_books_in_catalog("gatsby", "title")
            
            assert len(results) == 1
            assert 'Gatsby' in results[0]['title']

    def test_tc1_4_search_title_single_word(self):
        """TC1.4: Verify single word title search."""
        with patch('library_service.search_books', return_value=[
            {'id': 1, 'title': 'Dune', 'author': 'Frank Herbert', 
             'isbn': '9780441172719', 'total_copies': 4, 'available_copies': 2}
        ]):
            results = search_books_in_catalog("Dune", "title")
            
            assert len(results) == 1
            assert results[0]['title'] == 'Dune'

    def test_tc1_5_search_title_multiple_matches(self):
        """TC1.5: Verify multiple books match title search query."""
        with patch('library_service.search_books', return_value=[
            {'id': 1, 'title': 'Harry Potter and the Sorcerer\'s Stone', 'author': 'J.K. Rowling', 
             'isbn': '9780590353427', 'total_copies': 5, 'available_copies': 3},
            {'id': 2, 'title': 'Harry Potter and the Chamber of Secrets', 'author': 'J.K. Rowling',
             'isbn': '9780439064873', 'total_copies': 4, 'available_copies': 2},
            {'id': 3, 'title': 'Harry Potter and the Prisoner of Azkaban', 'author': 'J.K. Rowling',
             'isbn': '9780439136365', 'total_copies': 4, 'available_copies': 1}
        ]):
            results = search_books_in_catalog("Harry Potter", "title")
            
            assert len(results) == 3
            assert all('Harry Potter' in book['title'] for book in results)

    def test_tc1_6_search_title_with_special_characters(self):
        """TC1.6: Verify title search with special characters."""
        with patch('library_service.search_books', return_value=[
            {'id': 1, 'title': 'Book: A Journey!', 'author': 'Author Name', 
             'isbn': '9781234567890', 'total_copies': 3, 'available_copies': 2}
        ]):
            results = search_books_in_catalog("Book: A Journey!", "title")
            
            assert len(results) == 1
            assert results[0]['title'] == 'Book: A Journey!'

    def test_tc1_7_search_title_with_numbers(self):
        """TC1.7: Verify title search containing numbers."""
        with patch('library_service.search_books', return_value=[
            {'id': 1, 'title': '1984', 'author': 'George Orwell', 
             'isbn': '9780451524935', 'total_copies': 5, 'available_copies': 3}
        ]):
            results = search_books_in_catalog("1984", "title")
            
            assert len(results) == 1
            assert results[0]['title'] == '1984'

    def test_tc1_8_search_title_beginning_of_string(self):
        """TC1.8: Verify partial match at beginning of title."""
        with patch('library_service.search_books', return_value=[
            {'id': 1, 'title': 'The Catcher in the Rye', 'author': 'J.D. Salinger', 
             'isbn': '9780316769488', 'total_copies': 4, 'available_copies': 2}
        ]):
            results = search_books_in_catalog("The Catcher", "title")
            
            assert len(results) == 1

    def test_tc1_9_search_title_middle_of_string(self):
        """TC1.9: Verify partial match in middle of title."""
        with patch('library_service.search_books', return_value=[
            {'id': 1, 'title': 'To Kill a Mockingbird', 'author': 'Harper Lee', 
             'isbn': '9780061120084', 'total_copies': 5, 'available_copies': 4}
        ]):
            results = search_books_in_catalog("Kill", "title")
            
            assert len(results) == 1

    def test_tc1_10_search_title_end_of_string(self):
        """TC1.10: Verify partial match at end of title."""
        with patch('library_service.search_books', return_value=[
            {'id': 1, 'title': 'Lord of the Rings', 'author': 'J.R.R. Tolkien', 
             'isbn': '9780544003415', 'total_copies': 6, 'available_copies': 3}
        ]):
            results = search_books_in_catalog("Rings", "title")
            
            assert len(results) == 1

    # ==================== POSITIVE TEST CASES - AUTHOR SEARCH ====================

    def test_tc2_1_search_author_exact_match(self):
        """TC2.1: Verify exact author name match."""
        with patch('library_service.search_books', return_value=[
            {'id': 1, 'title': 'The Great Gatsby', 'author': 'F. Scott Fitzgerald', 
             'isbn': '9780743273565', 'total_copies': 5, 'available_copies': 3}
        ]):
            results = search_books_in_catalog("F. Scott Fitzgerald", "author")
            
            assert len(results) == 1
            assert results[0]['author'] == 'F. Scott Fitzgerald'

    def test_tc2_2_search_author_partial_match_last_name(self):
        """TC2.2: Verify partial author match by last name."""
        with patch('library_service.search_books', return_value=[
            {'id': 1, 'title': 'The Great Gatsby', 'author': 'F. Scott Fitzgerald', 
             'isbn': '9780743273565', 'total_copies': 5, 'available_copies': 3}
        ]):
            results = search_books_in_catalog("Fitzgerald", "author")
            
            assert len(results) == 1
            assert 'Fitzgerald' in results[0]['author']

    def test_tc2_3_search_author_partial_match_first_name(self):
        """TC2.3: Verify partial author match by first name."""
        with patch('library_service.search_books', return_value=[
            {'id': 1, 'title': 'Pride and Prejudice', 'author': 'Jane Austen', 
             'isbn': '9780141439518', 'total_copies': 4, 'available_copies': 2}
        ]):
            results = search_books_in_catalog("Jane", "author")
            
            assert len(results) == 1
            assert 'Jane' in results[0]['author']

    def test_tc2_4_search_author_case_insensitive(self):
        """TC2.4: Verify author search is case-insensitive."""
        with patch('library_service.search_books', return_value=[
            {'id': 1, 'title': '1984', 'author': 'George Orwell', 
             'isbn': '9780451524935', 'total_copies': 5, 'available_copies': 3}
        ]):
            results = search_books_in_catalog("george orwell", "author")
            
            assert len(results) == 1
            assert results[0]['author'] == 'George Orwell'

    def test_tc2_5_search_author_multiple_books(self):
        """TC2.5: Verify finding multiple books by same author."""
        with patch('library_service.search_books', return_value=[
            {'id': 1, 'title': 'Harry Potter and the Sorcerer\'s Stone', 'author': 'J.K. Rowling', 
             'isbn': '9780590353427', 'total_copies': 5, 'available_copies': 3},
            {'id': 2, 'title': 'Harry Potter and the Chamber of Secrets', 'author': 'J.K. Rowling',
             'isbn': '9780439064873', 'total_copies': 4, 'available_copies': 2}
        ]):
            results = search_books_in_catalog("J.K. Rowling", "author")
            
            assert len(results) == 2
            assert all(book['author'] == 'J.K. Rowling' for book in results)

    def test_tc2_6_search_author_with_special_characters(self):
        """TC2.6: Verify author search with special characters (Jr., III, etc.)."""
        with patch('library_service.search_books', return_value=[
            {'id': 1, 'title': 'Test Book', 'author': 'John Doe, Jr.', 
             'isbn': '9781234567890', 'total_copies': 3, 'available_copies': 2}
        ]):
            results = search_books_in_catalog("John Doe, Jr.", "author")
            
            assert len(results) == 1
            assert results[0]['author'] == 'John Doe, Jr.'

    def test_tc2_7_search_author_single_name(self):
        """TC2.7: Verify author search with single name (mononym)."""
        with patch('library_service.search_books', return_value=[
            {'id': 1, 'title': 'Test Book', 'author': 'Homer', 
             'isbn': '9781234567890', 'total_copies': 3, 'available_copies': 2}
        ]):
            results = search_books_in_catalog("Homer", "author")
            
            assert len(results) == 1
            assert results[0]['author'] == 'Homer'

    def test_tc2_8_search_author_with_unicode(self):
        """TC2.8: Verify author search with Unicode characters."""
        with patch('library_service.search_books', return_value=[
            {'id': 1, 'title': 'Test Book', 'author': 'José García', 
             'isbn': '9781234567890', 'total_copies': 3, 'available_copies': 2}
        ]):
            results = search_books_in_catalog("José García", "author")
            
            assert len(results) == 1
            assert results[0]['author'] == 'José García'

    # ==================== POSITIVE TEST CASES - ISBN SEARCH ====================

    def test_tc3_1_search_isbn_exact_match(self):
        """TC3.1: Verify exact ISBN match returns correct book."""
        with patch('library_service.search_books', return_value=[
            {'id': 1, 'title': 'The Great Gatsby', 'author': 'F. Scott Fitzgerald', 
             'isbn': '9780743273565', 'total_copies': 5, 'available_copies': 3}
        ]):
            results = search_books_in_catalog("9780743273565", "isbn")
            
            assert len(results) == 1
            assert results[0]['isbn'] == '9780743273565'

    def test_tc3_2_search_isbn_with_leading_zeros(self):
        """TC3.2: Verify ISBN search with leading zeros."""
        with patch('library_service.search_books', return_value=[
            {'id': 1, 'title': 'Test Book', 'author': 'Test Author', 
             'isbn': '0000000001234', 'total_copies': 3, 'available_copies': 2}
        ]):
            results = search_books_in_catalog("0000000001234", "isbn")
            
            assert len(results) == 1
            assert results[0]['isbn'] == '0000000001234'

    def test_tc3_3_search_isbn_all_zeros(self):
        """TC3.3: Verify ISBN search with all zeros."""
        with patch('library_service.search_books', return_value=[
            {'id': 1, 'title': 'Test Book', 'author': 'Test Author', 
             'isbn': '0000000000000', 'total_copies': 3, 'available_copies': 2}
        ]):
            results = search_books_in_catalog("0000000000000", "isbn")
            
            assert len(results) == 1
            assert results[0]['isbn'] == '0000000000000'

    def test_tc3_4_search_isbn_all_nines(self):
        """TC3.4: Verify ISBN search with all nines."""
        with patch('library_service.search_books', return_value=[
            {'id': 1, 'title': 'Test Book', 'author': 'Test Author', 
             'isbn': '9999999999999', 'total_copies': 3, 'available_copies': 2}
        ]):
            results = search_books_in_catalog("9999999999999", "isbn")
            
            assert len(results) == 1
            assert results[0]['isbn'] == '9999999999999'

    # ==================== NEGATIVE TEST CASES - EMPTY/INVALID SEARCH ====================

    def test_tc4_1_search_empty_query(self):
        """TC4.1: Verify empty search query returns no results."""
        results = search_books_in_catalog("", "title")
        
        assert results == []
        assert len(results) == 0

    def test_tc4_2_search_whitespace_only_query(self):
        """TC4.2: Verify whitespace-only query returns no results."""
        results = search_books_in_catalog("   ", "title")
        
        assert results == []
        assert len(results) == 0

    def test_tc4_3_search_none_query(self):
        """TC4.3: Verify None query returns no results."""
        results = search_books_in_catalog(None, "title")
        
        assert results == []

    def test_tc4_4_search_no_matches_title(self):
        """TC4.4: Verify no matches returns empty list for title search."""
        with patch('library_service.search_books', return_value=[]):
            results = search_books_in_catalog("NonexistentBookTitle12345", "title")
            
            assert results == []
            assert len(results) == 0

    def test_tc4_5_search_no_matches_author(self):
        """TC4.5: Verify no matches returns empty list for author search."""
        with patch('library_service.search_books', return_value=[]):
            results = search_books_in_catalog("NonexistentAuthor12345", "author")
            
            assert results == []

    def test_tc4_6_search_no_matches_isbn(self):
        """TC4.6: Verify no matches returns empty list for valid but non-existent ISBN."""
        with patch('library_service.search_books', return_value=[]):
            results = search_books_in_catalog("1111111111111", "isbn")
            
            assert results == []

    # ==================== NEGATIVE TEST CASES - INVALID ISBN FORMAT ====================

    def test_tc5_1_isbn_less_than_13_digits(self):
        """TC5.1: Verify ISBN with fewer than 13 digits returns no results."""
        results = search_books_in_catalog("123456789012", "isbn")
        
        assert results == []

    def test_tc5_2_isbn_more_than_13_digits(self):
        """TC5.2: Verify ISBN with more than 13 digits returns no results."""
        results = search_books_in_catalog("12345678901234", "isbn")
        
        assert results == []

    def test_tc5_3_isbn_with_letters(self):
        """TC5.3: Verify ISBN containing letters returns no results."""
        results = search_books_in_catalog("123456789012A", "isbn")
        
        assert results == []

    def test_tc5_4_isbn_with_special_characters(self):
        """TC5.4: Verify ISBN with hyphens/special characters returns no results."""
        results = search_books_in_catalog("978-0-7432-7356", "isbn")
        
        assert results == []

    def test_tc5_5_isbn_with_spaces(self):
        """TC5.5: Verify ISBN with spaces returns no results."""
        results = search_books_in_catalog("9780743 273565", "isbn")
        
        assert results == []

    def test_tc5_6_isbn_empty_string(self):
        """TC5.6: Verify empty string for ISBN search returns no results."""
        results = search_books_in_catalog("", "isbn")
        
        assert results == []

    def test_tc5_7_isbn_with_decimal_point(self):
        """TC5.7: Verify ISBN with decimal point returns no results."""
        results = search_books_in_catalog("9780743273.65", "isbn")
        
        assert results == []

    # ==================== SEARCH TYPE VALIDATION ====================

    def test_tc6_1_invalid_search_type_defaults_to_title(self):
        """TC6.1: Verify invalid search type defaults to title search."""
        with patch('library_service.search_books', return_value=[
            {'id': 1, 'title': 'Test Book', 'author': 'Test Author', 
             'isbn': '9781234567890', 'total_copies': 3, 'available_copies': 2}
        ]) as mock_search:
            results = search_books_in_catalog("Test", "invalid_type")
            
            # Verify search_books was called with 'title' as default
            mock_search.assert_called_once_with("Test", "title")

    def test_tc6_2_empty_search_type_defaults_to_title(self):
        """TC6.2: Verify empty search type defaults to title search."""
        with patch('library_service.search_books', return_value=[
            {'id': 1, 'title': 'Test Book', 'author': 'Test Author', 
             'isbn': '9781234567890', 'total_copies': 3, 'available_copies': 2}
        ]) as mock_search:
            results = search_books_in_catalog("Test", "")
            
            mock_search.assert_called_once_with("Test", "title")

    def test_tc6_3_none_search_type_defaults_to_title(self):
        """TC6.3: Verify None search type defaults to title search."""
        with patch('library_service.search_books', return_value=[
            {'id': 1, 'title': 'Test Book', 'author': 'Test Author', 
             'isbn': '9781234567890', 'total_copies': 3, 'available_copies': 2}
        ]) as mock_search:
            results = search_books_in_catalog("Test", None)
            
            mock_search.assert_called_once_with("Test", "title")

    def test_tc6_4_case_sensitive_search_type(self):
        """TC6.4: Verify search type is case-sensitive (TITLE should default to title)."""
        with patch('library_service.search_books', return_value=[
            {'id': 1, 'title': 'Test Book', 'author': 'Test Author', 
             'isbn': '9781234567890', 'total_copies': 3, 'available_copies': 2}
        ]) as mock_search:
            results = search_books_in_catalog("Test", "TITLE")
            
            # Should default to 'title' since 'TITLE' is not in valid_types
            mock_search.assert_called_once_with("Test", "title")

    def test_tc6_5_valid_title_search_type(self):
        """TC6.5: Verify 'title' search type is accepted."""
        with patch('library_service.search_books', return_value=[]) as mock_search:
            results = search_books_in_catalog("Test", "title")
            
            mock_search.assert_called_once_with("Test", "title")

    def test_tc6_6_valid_author_search_type(self):
        """TC6.6: Verify 'author' search type is accepted."""
        with patch('library_service.search_books', return_value=[]) as mock_search:
            results = search_books_in_catalog("Test", "author")
            
            mock_search.assert_called_once_with("Test", "author")

    def test_tc6_7_valid_isbn_search_type(self):
        """TC6.7: Verify 'isbn' search type is accepted."""
        with patch('library_service.search_books', return_value=[]) as mock_search:
            results = search_books_in_catalog("1234567890123", "isbn")
            
            mock_search.assert_called_once_with("1234567890123", "isbn")

    # ==================== WHITESPACE HANDLING ====================

    def test_tc7_1_search_query_with_leading_spaces(self):
        """TC7.1: Verify leading spaces are trimmed from search query."""
        with patch('library_service.search_books', return_value=[
            {'id': 1, 'title': 'Test Book', 'author': 'Test Author', 
             'isbn': '9781234567890', 'total_copies': 3, 'available_copies': 2}
        ]) as mock_search:
            results = search_books_in_catalog("   Test", "title")
            
            # Verify trimmed query was passed
            mock_search.assert_called_once_with("Test", "title")

    def test_tc7_2_search_query_with_trailing_spaces(self):
        """TC7.2: Verify trailing spaces are trimmed from search query."""
        with patch('library_service.search_books', return_value=[
            {'id': 1, 'title': 'Test Book', 'author': 'Test Author', 
             'isbn': '9781234567890', 'total_copies': 3, 'available_copies': 2}
        ]) as mock_search:
            results = search_books_in_catalog("Test   ", "title")
            
            mock_search.assert_called_once_with("Test", "title")

    def test_tc7_3_search_query_with_both_leading_and_trailing_spaces(self):
        """TC7.3: Verify both leading and trailing spaces are trimmed."""
        with patch('library_service.search_books', return_value=[
            {'id': 1, 'title': 'Test Book', 'author': 'Test Author', 
             'isbn': '9781234567890', 'total_copies': 3, 'available_copies': 2}
        ]) as mock_search:
            results = search_books_in_catalog("   Test Query   ", "title")
            
            mock_search.assert_called_once_with("Test Query", "title")

    def test_tc7_4_search_query_internal_spaces_preserved(self):
        """TC7.4: Verify internal spaces in query are preserved."""
        with patch('library_service.search_books', return_value=[
            {'id': 1, 'title': 'The Great Gatsby', 'author': 'F. Scott Fitzgerald', 
             'isbn': '9780743273565', 'total_copies': 5, 'available_copies': 3}
        ]) as mock_search:
            results = search_books_in_catalog("The Great Gatsby", "title")
            
            mock_search.assert_called_once_with("The Great Gatsby", "title")

    # ==================== RESPONSE FORMAT VALIDATION ====================

    def test_tc8_1_response_is_list(self):
        """TC8.1: Verify function returns a list."""
        with patch('library_service.search_books', return_value=[]):
            results = search_books_in_catalog("Test", "title")
            
            assert isinstance(results, list)

    def test_tc8_2_response_contains_required_fields(self):
        """TC8.2: Verify each result contains all required fields."""
        with patch('library_service.search_books', return_value=[
            {'id': 1, 'title': 'Test Book', 'author': 'Test Author', 
             'isbn': '9781234567890', 'total_copies': 3, 'available_copies': 2}
        ]):
            results = search_books_in_catalog("Test", "title")
            
            assert len(results) == 1
            book = results[0]
            assert 'id' in book
            assert 'title' in book
            assert 'author' in book
            assert 'isbn' in book
            assert 'total_copies' in book
            assert 'available_copies' in book

    def test_tc8_3_empty_results_return_empty_list(self):
        """TC8.3: Verify empty results return empty list (not None)."""
        with patch('library_service.search_books', return_value=[]):
            results = search_books_in_catalog("Nonexistent", "title")
            
            assert results == []
            assert isinstance(results, list)
            assert len(results) == 0

    def test_tc8_4_multiple_results_format(self):
        """TC8.4: Verify multiple results maintain consistent format."""
        with patch('library_service.search_books', return_value=[
            {'id': 1, 'title': 'Book 1', 'author': 'Author 1', 
             'isbn': '9781234567890', 'total_copies': 3, 'available_copies': 2},
            {'id': 2, 'title': 'Book 2', 'author': 'Author 2',
             'isbn': '9780987654321', 'total_copies': 5, 'available_copies': 4}
        ]):
            results = search_books_in_catalog("Book", "title")
            
            assert len(results) == 2
            for book in results:
                assert 'id' in book
                assert 'title' in book
                assert 'author' in book
                assert 'isbn' in book

    # ==================== EDGE CASES ====================

    def test_tc9_1_search_very_long_query(self):
        """TC9.1: Verify handling of very long search query (200 characters)."""
        long_query = "A" * 200
        with patch('library_service.search_books', return_value=[]) as mock_search:
            results = search_books_in_catalog(long_query, "title")
            
            mock_search.assert_called_once_with(long_query, "title")

    def test_tc9_2_search_single_character(self):
        """TC9.2: Verify single character search works."""
        with patch('library_service.search_books', return_value=[
            {'id': 1, 'title': 'A Tale of Two Cities', 'author': 'Charles Dickens', 
             'isbn': '9780141439600', 'total_copies': 4, 'available_copies': 3}
        ]):
            results = search_books_in_catalog("A", "title")
            
            assert len(results) == 1

    def test_tc9_3_search_numeric_query_for_title(self):
        """TC9.3: Verify numeric search query for title search."""
        with patch('library_service.search_books', return_value=[
            {'id': 1, 'title': '1984', 'author': 'George Orwell', 
             'isbn': '9780451524935', 'total_copies': 5, 'available_copies': 3}
        ]):
            results = search_books_in_catalog("1984", "title")
            
            assert len(results) == 1

    def test_tc9_4_search_with_only_special_characters(self):
        """TC9.4: Verify search with only special characters."""
        with patch('library_service.search_books', return_value=[]):
            results = search_books_in_catalog("@#$%", "title")
            
            # Should process normally, may return no results
            assert isinstance(results, list)

    def test_tc9_5_search_unicode_query(self):
        """TC9.5: Verify search with Unicode characters."""
        with patch('library_service.search_books', return_value=[
            {'id': 1, 'title': '日本語のタイトル', 'author': 'Test Author', 
             'isbn': '9781234567890', 'total_copies': 3, 'available_copies': 2}
        ]):
            results = search_books_in_catalog("日本語", "title")
            
            assert len(results) == 1

    def test_tc9_6_search_mixed_case_query(self):
        """TC9.6: Verify search with mixed case."""
        with patch('library_service.search_books', return_value=[
            {'id': 1, 'title': 'The Great Gatsby', 'author': 'F. Scott Fitzgerald', 
             'isbn': '9780743273565', 'total_copies': 5, 'available_copies': 3}
        ]):
            results = search_books_in_catalog("tHe GrEaT gAtSbY", "title")
            
            assert len(results) == 1

    # ==================== COMPREHENSIVE SEARCH TYPE TESTS ====================

    def test_tc10_1_title_search_type_explicit(self):
        """TC10.1: Verify explicit title search type works correctly."""
        with patch('library_service.search_books', return_value=[
            {'id': 1, 'title': 'Test Book', 'author': 'Test Author', 
             'isbn': '9781234567890', 'total_copies': 3, 'available_copies': 2}
        ]) as mock_search:
            results = search_books_in_catalog("Test", "title")
            
            mock_search.assert_called_once()
            call_args = mock_search.call_args[0]
            assert call_args[1] == "title"

    def test_tc10_2_author_search_type_explicit(self):
        """TC10.2: Verify explicit author search type works correctly."""
        with patch('library_service.search_books', return_value=[
            {'id': 1, 'title': 'Test Book', 'author': 'Test Author', 
             'isbn': '9781234567890', 'total_copies': 3, 'available_copies': 2}
        ]) as mock_search:
            results = search_books_in_catalog("Author", "author")
            
            mock_search.assert_called_once()
            call_args = mock_search.call_args[0]
            assert call_args[1] == "author"

    def test_tc10_3_isbn_search_type_explicit(self):
        """TC10.3: Verify explicit ISBN search type works correctly."""
        with patch('library_service.search_books', return_value=[
            {'id': 1, 'title': 'Test Book', 'author': 'Test Author', 
             'isbn': '9781234567890', 'total_copies': 3, 'available_copies': 2}
        ]) as mock_search:
            results = search_books_in_catalog("9781234567890", "isbn")
            
            mock_search.assert_called_once()
            call_args = mock_search.call_args[0]
            assert call_args[1] == "isbn"

    # ==================== ISBN VALIDATION EDGE CASES ====================

    def test_tc11_1_isbn_exactly_13_digits_valid(self):
        """TC11.1: Verify exactly 13 digits is valid for ISBN search."""
        with patch('library_service.search_books', return_value=[
            {'id': 1, 'title': 'Test Book', 'author': 'Test Author', 
             'isbn': '1234567890123', 'total_copies': 3, 'available_copies': 2}
        ]):
            results = search_books_in_catalog("1234567890123", "isbn")
            
            assert len(results) == 1

    def test_tc11_2_isbn_12_digits_invalid(self):
        """TC11.2: Verify 12 digits returns no results for ISBN search."""
        results = search_books_in_catalog("123456789012", "isbn")
        
        assert results == []

    def test_tc11_3_isbn_14_digits_invalid(self):
        """TC11.3: Verify 14 digits returns no results for ISBN search."""
        results = search_books_in_catalog("12345678901234", "isbn")
        
        assert results == []

    def test_tc11_4_isbn_with_mixed_alphanumeric(self):
        """TC11.4: Verify mixed alphanumeric ISBN returns no results."""
        results = search_books_in_catalog("12345ABC67890", "isbn")
        
        assert results == []

    def test_tc11_5_isbn_negative_number_format(self):
        """TC11.5: Verify ISBN with negative sign returns no results."""
        results = search_books_in_catalog("-123456789012", "isbn")
        
        assert results == []

    def test_tc11_6_isbn_with_plus_sign(self):
        """TC11.6: Verify ISBN with plus sign returns no results."""
        results = search_books_in_catalog("+1234567890123", "isbn")
        
        assert results == []

    # ==================== RESULT ORDERING AND CONSISTENCY ====================

    def test_tc12_1_results_maintain_order(self):
        """TC12.1: Verify results maintain order returned from database."""
        with patch('library_service.search_books', return_value=[
            {'id': 1, 'title': 'Book A', 'author': 'Author A', 
             'isbn': '9781234567890', 'total_copies': 3, 'available_copies': 2},
            {'id': 2, 'title': 'Book B', 'author': 'Author B',
             'isbn': '9780987654321', 'total_copies': 5, 'available_copies': 4},
            {'id': 3, 'title': 'Book C', 'author': 'Author C',
             'isbn': '9785555555555', 'total_copies': 2, 'available_copies': 1}
        ]):
            results = search_books_in_catalog("Book", "title")
            
            assert len(results) == 3
            assert results[0]['id'] == 1
            assert results[1]['id'] == 2
            assert results[2]['id'] == 3

    def test_tc12_2_duplicate_search_returns_consistent_results(self):
        """TC12.2: Verify repeated searches return consistent results."""
        with patch('library_service.search_books', return_value=[
            {'id': 1, 'title': 'Test Book', 'author': 'Test Author', 
             'isbn': '9781234567890', 'total_copies': 3, 'available_copies': 2}
        ]):
            results1 = search_books_in_catalog("Test", "title")
            results2 = search_books_in_catalog("Test", "title")
            
            assert results1 == results2

    # ==================== SEARCH WITH VARIOUS BOOK STATES ====================

    def test_tc13_1_search_returns_books_with_zero_available_copies(self):
        """TC13.1: Verify search includes books with no available copies."""
        with patch('library_service.search_books', return_value=[
            {'id': 1, 'title': 'Fully Borrowed Book', 'author': 'Test Author', 
             'isbn': '9781234567890', 'total_copies': 3, 'available_copies': 0}
        ]):
            results = search_books_in_catalog("Borrowed", "title")
            
            assert len(results) == 1
            assert results[0]['available_copies'] == 0

    def test_tc13_2_search_returns_books_with_all_copies_available(self):
        """TC13.2: Verify search includes books with all copies available."""
        with patch('library_service.search_books', return_value=[
            {'id': 1, 'title': 'Available Book', 'author': 'Test Author', 
             'isbn': '9781234567890', 'total_copies': 5, 'available_copies': 5}
        ]):
            results = search_books_in_catalog("Available", "title")
            
            assert len(results) == 1
            assert results[0]['available_copies'] == results[0]['total_copies']

    def test_tc13_3_search_returns_books_with_partial_availability(self):
        """TC13.3: Verify search includes books with partial availability."""
        with patch('library_service.search_books', return_value=[
            {'id': 1, 'title': 'Partial Book', 'author': 'Test Author', 
             'isbn': '9781234567890', 'total_copies': 10, 'available_copies': 6}
        ]):
            results = search_books_in_catalog("Partial", "title")
            
            assert len(results) == 1
            assert 0 < results[0]['available_copies'] < results[0]['total_copies']

    # ==================== SPECIAL SEARCH SCENARIOS ====================

    def test_tc14_1_search_title_with_apostrophe(self):
        """TC14.1: Verify search with apostrophe in title."""
        with patch('library_service.search_books', return_value=[
            {'id': 1, 'title': "The Handmaid's Tale", 'author': 'Margaret Atwood', 
             'isbn': '9780385490818', 'total_copies': 4, 'available_copies': 2}
        ]):
            results = search_books_in_catalog("Handmaid's", "title")
            
            assert len(results) == 1

    def test_tc14_2_search_title_with_colon(self):
        """TC14.2: Verify search with colon in title."""
        with patch('library_service.search_books', return_value=[
            {'id': 1, 'title': 'Book Title: A Subtitle', 'author': 'Test Author', 
             'isbn': '9781234567890', 'total_copies': 3, 'available_copies': 2}
        ]):
            results = search_books_in_catalog("Book Title:", "title")
            
            assert len(results) == 1

    def test_tc14_3_search_title_with_ampersand(self):
        """TC14.3: Verify search with ampersand in title."""
        with patch('library_service.search_books', return_value=[
            {'id': 1, 'title': 'Pride & Prejudice', 'author': 'Jane Austen', 
             'isbn': '9780141439518', 'total_copies': 4, 'available_copies': 2}
        ]):
            results = search_books_in_catalog("Pride &", "title")
            
            assert len(results) == 1

    def test_tc14_4_search_author_with_middle_initial(self):
        """TC14.4: Verify search for author with middle initial."""
        with patch('library_service.search_books', return_value=[
            {'id': 1, 'title': 'Test Book', 'author': 'J. R. R. Tolkien', 
             'isbn': '9781234567890', 'total_copies': 3, 'available_copies': 2}
        ]):
            results = search_books_in_catalog("J. R. R. Tolkien", "author")
            
            assert len(results) == 1

    def test_tc14_5_search_author_partial_middle_initial(self):
        """TC14.5: Verify partial search including middle initial."""
        with patch('library_service.search_books', return_value=[
            {'id': 1, 'title': 'The Great Gatsby', 'author': 'F. Scott Fitzgerald', 
             'isbn': '9780743273565', 'total_copies': 5, 'available_copies': 3}
        ]):
            results = search_books_in_catalog("F. Scott", "author")
            
            assert len(results) == 1

    # ==================== BOUNDARY CASES ====================

    def test_tc15_1_search_query_with_tab_characters(self):
        """TC15.1: Verify handling of tab characters in query."""
        with patch('library_service.search_books', return_value=[]) as mock_search:
            results = search_books_in_catalog("Test\tBook", "title")
            
            # Tabs should be preserved in the query after strip()
            mock_search.assert_called_once()

    def test_tc15_2_search_query_with_newline(self):
        """TC15.2: Verify handling of newline characters in query."""
        with patch('library_service.search_books', return_value=[]) as mock_search:
            results = search_books_in_catalog("Test\nBook", "title")
            
            mock_search.assert_called_once()

    def test_tc15_3_search_with_leading_zeros_in_title(self):
        """TC15.3: Verify search for title starting with zeros."""
        with patch('library_service.search_books', return_value=[
            {'id': 1, 'title': '007 James Bond', 'author': 'Ian Fleming', 
             'isbn': '9781234567890', 'total_copies': 3, 'available_copies': 2}
        ]):
            results = search_books_in_catalog("007", "title")
            
            assert len(results) == 1

    def test_tc15_4_maximum_results_handling(self):
        """TC15.4: Verify handling of large number of results."""
        # Create 100 mock results
        mock_results = [
            {'id': i, 'title': f'Book {i}', 'author': f'Author {i}', 
             'isbn': f'{1000000000000 + i:013d}', 'total_copies': 3, 'available_copies': 2}
            for i in range(1, 101)
        ]
        
        with patch('library_service.search_books', return_value=mock_results):
            results = search_books_in_catalog("Book", "title")
            
            assert len(results) == 100
            assert isinstance(results, list)

    # ==================== INTEGRATION-STYLE TESTS ====================

    def test_tc16_1_search_same_query_different_types(self):
        """TC16.1: Verify same query returns different results for different search types."""
        query = "Test"
        
        # Title search
        with patch('library_service.search_books', return_value=[
            {'id': 1, 'title': 'Test Book', 'author': 'Author Name', 
             'isbn': '9781234567890', 'total_copies': 3, 'available_copies': 2}
        ]) as mock_search_title:
            results_title = search_books_in_catalog(query, "title")
            mock_search_title.assert_called_once_with(query, "title")
        
        # Author search
        with patch('library_service.search_books', return_value=[
            {'id': 2, 'title': 'Different Book', 'author': 'Test Author', 
             'isbn': '9780987654321', 'total_copies': 4, 'available_copies': 3}
        ]) as mock_search_author:
            results_author = search_books_in_catalog(query, "author")
            mock_search_author.assert_called_once_with(query, "author")

    def test_tc16_2_isbn_search_not_called_for_invalid_format(self):
        """TC16.2: Verify search_books is not called for invalid ISBN format."""
        with patch('library_service.search_books') as mock_search:
            results = search_books_in_catalog("invalid-isbn", "isbn")
            
            # Should not call search_books due to validation failure
            mock_search.assert_not_called()
            assert results == []

    def test_tc16_3_empty_query_not_passed_to_search(self):
        """TC16.3: Verify empty query doesn't call search_books."""
        with patch('library_service.search_books') as mock_search:
            results = search_books_in_catalog("", "title")
            
            mock_search.assert_not_called()
            assert results == []

    # ==================== RETURN FORMAT CONSISTENCY ====================

    def test_tc17_1_all_results_have_consistent_structure(self):
        """TC17.1: Verify all results have consistent structure."""
        with patch('library_service.search_books', return_value=[
            {'id': 1, 'title': 'Book 1', 'author': 'Author 1', 
             'isbn': '9781234567890', 'total_copies': 3, 'available_copies': 2},
            {'id': 2, 'title': 'Book 2', 'author': 'Author 2',
             'isbn': '9780987654321', 'total_copies': 5, 'available_copies': 4}
        ]):
            results = search_books_in_catalog("Book", "title")
            
            # Check all results have same keys
            keys_set = [set(book.keys()) for book in results]
            assert all(keys == keys_set[0] for keys in keys_set)

    def test_tc17_2_numeric_fields_are_correct_types(self):
        """TC17.2: Verify numeric fields are integers."""
        with patch('library_service.search_books', return_value=[
            {'id': 1, 'title': 'Test Book', 'author': 'Test Author', 
             'isbn': '9781234567890', 'total_copies': 3, 'available_copies': 2}
        ]):
            results = search_books_in_catalog("Test", "title")
            
            book = results[0]
            assert isinstance(book['id'], int)
            assert isinstance(book['total_copies'], int)
            assert isinstance(book['available_copies'], int)

    def test_tc17_3_string_fields_are_correct_types(self):
        """TC17.3: Verify string fields are strings."""
        with patch('library_service.search_books', return_value=[
            {'id': 1, 'title': 'Test Book', 'author': 'Test Author', 
             'isbn': '9781234567890', 'total_copies': 3, 'available_copies': 2}
        ]):
            results = search_books_in_catalog("Test", "title")
            
            book = results[0]
            assert isinstance(book['title'], str)
            assert isinstance(book['author'], str)
            assert isinstance(book['isbn'], str)