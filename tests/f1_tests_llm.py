# PYTHONPATH=. pytest tests/f1_test.py
import pytest
from unittest.mock import patch, MagicMock
from services.library_service import (
    add_book_to_catalog
)

# ==================== POSITIVE TEST CASES ====================

def test_tc1_1_valid_book_minimum_data():
    """TC1.1: Verify that a book can be added with minimum valid data."""
    with patch('services.library_service.get_book_by_isbn', return_value=None), \
         patch('services.library_service.insert_book', return_value=True):
        success, message = add_book_to_catalog("A", "B", "1234567890123", 1)
        assert success == True
        assert 'book "a" has been successfully added to the catalog.' in message.lower()

def test_tc1_2_valid_book_maximum_data():
    """TC1.2: Verify that a book can be added with maximum allowed character lengths."""
    title_200 = "A" * 200
    author_100 = "B" * 100
    with patch('services.library_service.get_book_by_isbn', return_value=None), \
         patch('services.library_service.insert_book', return_value=True):
        success, message = add_book_to_catalog(title_200, author_100, "9876543210987", 1000)
        assert success == True
        assert "successfully added" in message.lower()

def test_tc1_3_valid_book_typical_data():
    """TC1.3: Verify that a book can be added with typical realistic data."""
    with patch('services.library_service.get_book_by_isbn', return_value=None), \
         patch('services.library_service.insert_book', return_value=True):
        success, message = add_book_to_catalog("The Great Gatsby", "F. Scott Fitzgerald", "9780743273565", 5)
        assert success == True
        assert 'book "the great gatsby" has been successfully added' in message.lower()

def test_tc1_4_valid_book_with_leading_trailing_spaces():
    """TC1.4: Verify that leading and trailing spaces are trimmed before adding."""
    with patch('services.library_service.get_book_by_isbn', return_value=None), \
         patch('services.library_service.insert_book', return_value=True):
        success, message = add_book_to_catalog("  The Catcher in the Rye  ", "  J.D. Salinger  ", "9780316769488", 3)
        assert success == True
        assert 'book "the catcher in the rye" has been successfully added' in message.lower()

# ==================== NEGATIVE TEST CASES - TITLE VALIDATION ====================

def test_tc2_1_empty_title():
    """TC2.1: Verify that empty title is rejected."""
    success, message = add_book_to_catalog("", "John Doe", "1234567890123", 1)
    assert success == False
    assert "title is required." in message.lower()

def test_tc2_2_title_only_whitespace():
    """TC2.2: Verify that title containing only spaces is rejected."""
    success, message = add_book_to_catalog("   ", "John Doe", "1234567890123", 1)
    assert success == False
    assert "title is required." in message.lower()

def test_tc2_3_title_none():
    """TC2.3: Verify that None title is rejected."""
    success, message = add_book_to_catalog(None, "John Doe", "1234567890123", 1)
    assert success == False
    assert "title is required." in message.lower()

def test_tc2_4_title_exceeding_200_characters():
    """TC2.4: Verify that title exceeding 200 characters is rejected."""
    long_title = "A" * 201
    success, message = add_book_to_catalog(long_title, "John Doe", "1234567890123", 1)
    assert success == False
    assert "title must be less than 200 characters." in message.lower()

def test_tc2_5_title_exactly_200_characters_with_spaces():
    """TC2.5: Verify handling of title that is exactly 200 chars after trimming."""
    title_with_spaces = "  " + ("A" * 200) + "  "
    with patch('services.library_service.get_book_by_isbn', return_value=None), \
         patch('services.library_service.insert_book', return_value=True):
        success, message = add_book_to_catalog(title_with_spaces, "John Doe", "1234567890123", 1)
        assert success == True
        assert "successfully added" in message.lower()

def test_tc2_6_title_exceeding_200_characters_after_trimming():
    """TC2.6: Verify that title exceeding 200 characters after trimming is rejected."""
    title_with_spaces = "  " + ("A" * 201) + "  "
    success, message = add_book_to_catalog(title_with_spaces, "John Doe", "1234567890123", 1)
    assert success == False
    assert "title must be less than 200 characters." in message.lower()

# ==================== NEGATIVE TEST CASES - AUTHOR VALIDATION ====================

def test_tc3_1_empty_author():
    """TC3.1: Verify that empty author is rejected."""
    success, message = add_book_to_catalog("Valid Title", "", "1234567890123", 1)
    assert success == False
    assert "author is required." in message.lower()

def test_tc3_2_author_only_whitespace():
    """TC3.2: Verify that author containing only spaces is rejected."""
    success, message = add_book_to_catalog("Valid Title", "   ", "1234567890123", 1)
    assert success == False
    assert "author is required." in message.lower()

def test_tc3_3_author_none():
    """TC3.3: Verify that None author is rejected."""
    success, message = add_book_to_catalog("Valid Title", None, "1234567890123", 1)
    assert success == False
    assert "author is required." in message.lower()

def test_tc3_4_author_exceeding_100_characters():
    """TC3.4: Verify that author exceeding 100 characters is rejected."""
    long_author = "B" * 101
    success, message = add_book_to_catalog("Valid Title", long_author, "1234567890123", 1)
    assert success == False
    assert "author must be less than 100 characters." in message.lower()

def test_tc3_5_author_exactly_100_characters():
    """TC3.5: Verify that author with exactly 100 characters is accepted."""
    author_100 = "B" * 100
    with patch('services.library_service.get_book_by_isbn', return_value=None), \
         patch('services.library_service.insert_book', return_value=True):
        success, message = add_book_to_catalog("Valid Title", author_100, "1234567890123", 1)
        assert success == True
        assert "successfully added" in message.lower()

def test_tc3_6_author_exceeding_100_characters_after_trimming():
    """TC3.6: Verify that author exceeding 100 characters after trimming is rejected."""
    author_with_spaces = "  " + ("B" * 101) + "  "
    success, message = add_book_to_catalog("Valid Title", author_with_spaces, "1234567890123", 1)
    assert success == False
    assert "author must be less than 100 characters." in message.lower()

# ==================== NEGATIVE TEST CASES - ISBN VALIDATION ====================

def test_tc4_1_isbn_less_than_13_digits():
    """TC4.1: Verify that ISBN with fewer than 13 digits is rejected."""
    success, message = add_book_to_catalog("Valid Title", "Valid Author", "123456789012", 1)
    assert success == False
    assert "isbn must be exactly 13 digits." in message.lower()

def test_tc4_2_isbn_more_than_13_digits():
    """TC4.2: Verify that ISBN with more than 13 digits is rejected."""
    success, message = add_book_to_catalog("Valid Title", "Valid Author", "12345678901234", 1)
    assert success == False
    assert "isbn must be exactly 13 digits." in message.lower()

def test_tc4_3_isbn_with_non_digit_characters():
    """TC4.3: Verify that ISBN containing letters is rejected."""
    success, message = add_book_to_catalog("Valid Title", "Valid Author", "123456789012A", 1)
    assert success == False
    assert "isbn must contian only digits." in message.lower()

def test_tc4_4_isbn_with_special_characters():
    """TC4.4: Verify that ISBN containing special characters is rejected."""
    success, message = add_book_to_catalog("Valid Title", "Valid Author", "123456789012A", 1)
    assert success == False
    assert "isbn must contian only digits." in message.lower()

def test_tc4_5_isbn_with_spaces():
    """TC4.5: Verify that ISBN containing spaces is rejected."""
    success, message = add_book_to_catalog("Valid Title", "Valid Author", "1234 56789012", 1)
    assert success == False
    assert "isbn must contian only digits." in message.lower()

def test_tc4_6_empty_isbn():
    """TC4.6: Verify that empty ISBN is rejected."""
    success, message = add_book_to_catalog("Valid Title", "Valid Author", "", 1)
    assert success == False
    assert "isbn must be exactly 13 digits." in message.lower()

def test_tc4_7_isbn_with_leading_zeros():
    """TC4.7: Verify that ISBN with leading zeros is accepted."""
    with patch('services.library_service.get_book_by_isbn', return_value=None), \
         patch('services.library_service.insert_book', return_value=True):
        success, message = add_book_to_catalog("Valid Title", "Valid Author", "0000000000123", 1)
        assert success == True
        assert "successfully added" in message.lower()

# ==================== NEGATIVE TEST CASES - TOTAL COPIES VALIDATION ====================

def test_tc5_1_zero_total_copies():
    """TC5.1: Verify that zero copies is rejected."""
    success, message = add_book_to_catalog("Valid Title", "Valid Author", "1234567890123", 0)
    assert success == False
    assert "total copies must be a positive integer." in message.lower()

def test_tc5_2_negative_total_copies():
    """TC5.2: Verify that negative copies is rejected."""
    success, message = add_book_to_catalog("Valid Title", "Valid Author", "1234567890123", -5)
    assert success == False
    assert "total copies must be a positive integer." in message.lower()

def test_tc5_3_non_integer_total_copies_float():
    """TC5.3: Verify that float value is rejected."""
    success, message = add_book_to_catalog("Valid Title", "Valid Author", "1234567890123", 5.5)
    assert success == False
    assert "total copies must be a positive integer." in message.lower()

def test_tc5_4_non_integer_total_copies_string():
    """TC5.4: Verify that string value is rejected."""
    success, message = add_book_to_catalog("Valid Title", "Valid Author", "1234567890123", "5")
    assert success == False
    assert "total copies must be a positive integer." in message.lower()

def test_tc5_5_none_as_total_copies():
    """TC5.5: Verify that None value is rejected."""
    success, message = add_book_to_catalog("Valid Title", "Valid Author", "1234567890123", None)
    assert success == False
    assert "total copies must be a positive integer." in message.lower()

def test_tc5_6_very_large_total_copies():
    """TC5.6: Verify that very large positive integer is accepted."""
    with patch('services.library_service.get_book_by_isbn', return_value=None), \
         patch('services.library_service.insert_book', return_value=True):
        success, message = add_book_to_catalog("Valid Title", "Valid Author", "1234567890123", 999999999)
        assert success == True
        assert "successfully added" in message.lower()

# ==================== NEGATIVE TEST CASES - BUSINESS LOGIC ====================

def test_tc6_1_duplicate_isbn():
    """TC6.1: Verify that duplicate ISBN is rejected."""
    with patch('services.library_service.get_book_by_isbn', return_value={"isbn": "1234567890123"}):
        success, message = add_book_to_catalog("Different Title", "Different Author", "1234567890123", 5)
        assert success == False
        assert "a book with this isbn already exists." in message.lower()

def test_tc6_2_database_insert_failure():
    """TC6.2: Verify proper error handling when database insert fails."""
    with patch('services.library_service.get_book_by_isbn', return_value=None), \
         patch('services.library_service.insert_book', return_value=False):
        success, message = add_book_to_catalog("Valid Title", "Valid Author", "1234567890123", 1)
        assert success == False
        assert "database error occurred while adding the book." in message.lower()

# ==================== EDGE CASES AND SPECIAL CHARACTERS ====================

def test_tc7_1_title_with_special_characters():
    """TC7.1: Verify that title with special characters is accepted."""
    with patch('services.library_service.get_book_by_isbn', return_value=None), \
         patch('services.library_service.insert_book', return_value=True):
        success, message = add_book_to_catalog("Book: A Journey! @2024 #1", "Valid Author", "1234567890123", 1)
        assert success == True
        assert "successfully added" in message.lower()

def test_tc7_2_author_with_special_characters():
    """TC7.2: Verify that author with special characters is accepted."""
    with patch('services.library_service.get_book_by_isbn', return_value=None), \
         patch('services.library_service.insert_book', return_value=True):
        success, message = add_book_to_catalog("Valid Title", "O'Brien, Jr.", "1234567890123", 1)
        assert success == True
        assert "successfully added" in message.lower()

def test_tc7_3_title_with_unicode_characters():
    """TC7.3: Verify that title with Unicode characters is accepted."""
    with patch('services.library_service.get_book_by_isbn', return_value=None), \
         patch('services.library_service.insert_book', return_value=True):
        success, message = add_book_to_catalog("日本語のタイトル", "Valid Author", "1234567890123", 1)
        assert success == True
        assert "successfully added" in message.lower()

def test_tc7_4_author_with_unicode_characters():
    """TC7.4: Verify that author with Unicode characters is accepted."""
    with patch('services.library_service.get_book_by_isbn', return_value=None), \
         patch('services.library_service.insert_book', return_value=True):
        success, message = add_book_to_catalog("Valid Title", "José García", "1234567890123", 1)
        assert success == True
        assert "successfully added" in message.lower()

def test_tc7_5_multiple_consecutive_spaces_in_title():
    """TC7.5: Verify handling of multiple spaces within title."""
    with patch('services.library_service.get_book_by_isbn', return_value=None), \
         patch('services.library_service.insert_book', return_value=True):
        success, message = add_book_to_catalog("The    Great    Book", "Valid Author", "1234567890123", 1)
        assert success == True
        assert "successfully added" in message.lower()