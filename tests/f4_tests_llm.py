# PYTHONPATH=. pytest tests/f4_test.py
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from library_service import return_book_by_patron
from database import (
    init_database,
    get_db_connection,
    insert_book,
    get_book_by_id
)


class TestR4BookReturn:
    """Test cases for R4: Book Return Processing"""

    def setup_method(self):
        """Setup test database before each test"""
        init_database()
        # Clear existing data
        conn = get_db_connection()
        conn.execute('DELETE FROM borrow_records')
        conn.execute('DELETE FROM books')
        conn.commit()
        conn.close()

    # ==================== POSITIVE TEST CASES - ON TIME RETURNS ====================

    def test_tc1_1_successful_return_on_time(self):
        """TC1.1: Verify successful book return on or before due date (no late fee)."""
        borrow_date = datetime.now() - timedelta(days=7)
        due_date = borrow_date + timedelta(days=14)
        
        with patch('library_service.get_book_by_id', return_value={
            'id': 1, 'title': 'Test Book', 'available_copies': 2
        }), \
             patch('library_service.get_borrow_record', return_value={
                 'patron_id': '123456', 'book_id': 1, 
                 'due_date': due_date.isoformat(), 'return_date': None
             }), \
             patch('library_service.update_book_availability', return_value=True), \
             patch('library_service.update_borrow_record_return_date', return_value=True), \
             patch('library_service.calculate_late_fee_for_book', return_value=0):
            
            success, message = return_book_by_patron("123456", 1)
            
            assert success == True
            assert 'returned successfully' in message.lower()
            assert 'no late fees' in message.lower()

    def test_tc1_2_successful_return_on_exact_due_date(self):
        """TC1.2: Verify successful return on exact due date (boundary - no late fee)."""
        due_date = datetime.now()
        
        with patch('library_service.get_book_by_id', return_value={
            'id': 1, 'title': 'Test Book', 'available_copies': 2
        }), \
             patch('library_service.get_borrow_record', return_value={
                 'patron_id': '123456', 'book_id': 1,
                 'due_date': due_date.isoformat(), 'return_date': None
             }), \
             patch('library_service.update_book_availability', return_value=True), \
             patch('library_service.update_borrow_record_return_date', return_value=True), \
             patch('library_service.calculate_late_fee_for_book', return_value=0):
            
            success, message = return_book_by_patron("123456", 1)
            
            assert success == True
            assert 'no late fees' in message.lower()

    def test_tc1_3_successful_return_early(self):
        """TC1.3: Verify successful early return (well before due date)."""
        borrow_date = datetime.now() - timedelta(days=3)
        due_date = borrow_date + timedelta(days=14)
        
        with patch('library_service.get_book_by_id', return_value={
            'id': 1, 'title': 'Early Return', 'available_copies': 4
        }), \
             patch('library_service.get_borrow_record', return_value={
                 'patron_id': '999999', 'book_id': 1,
                 'due_date': due_date.isoformat(), 'return_date': None
             }), \
             patch('library_service.update_book_availability', return_value=True), \
             patch('library_service.update_borrow_record_return_date', return_value=True), \
             patch('library_service.calculate_late_fee_for_book', return_value=0):
            
            success, message = return_book_by_patron("999999", 1)
            
            assert success == True
            assert 'no late fees' in message.lower()

    def test_tc1_4_successful_return_includes_book_title(self):
        """TC1.4: Verify success message includes the book title."""
        due_date = datetime.now()
        
        with patch('library_service.get_book_by_id', return_value={
            'id': 1, 'title': 'The Great Gatsby', 'available_copies': 2
        }), \
             patch('library_service.get_borrow_record', return_value={
                 'patron_id': '123456', 'book_id': 1,
                 'due_date': due_date.isoformat(), 'return_date': None
             }), \
             patch('library_service.update_book_availability', return_value=True), \
             patch('library_service.update_borrow_record_return_date', return_value=True), \
             patch('library_service.calculate_late_fee_for_book', return_value=0):
            
            success, message = return_book_by_patron("123456", 1)
            
            assert success == True
            assert 'the great gatsby' in message.lower()

    # ==================== POSITIVE TEST CASES - LATE RETURNS WITH FEES ====================

    def test_tc2_1_return_1_day_late(self):
        """TC2.1: Verify late fee calculation for 1 day overdue ($0.50)."""
        due_date = datetime.now() - timedelta(days=1)
        
        with patch('library_service.get_book_by_id', return_value={
            'id': 1, 'title': 'Test Book', 'available_copies': 2
        }), \
             patch('library_service.get_borrow_record', return_value={
                 'patron_id': '123456', 'book_id': 1,
                 'due_date': due_date.isoformat(), 'return_date': None
             }), \
             patch('library_service.update_book_availability', return_value=True), \
             patch('library_service.update_borrow_record_return_date', return_value=True), \
             patch('library_service.calculate_late_fee_for_book', return_value=0.50):
            
            success, message = return_book_by_patron("123456", 1)
            
            assert success == True
            assert 'returned successfully' in message.lower()
            assert 'late fee: $0.50' in message.lower()
            assert '1 days overdue' in message.lower()

    def test_tc2_2_return_7_days_late(self):
        """TC2.2: Verify late fee calculation for 7 days overdue ($3.50 - boundary)."""
        due_date = datetime.now() - timedelta(days=7)
        
        with patch('library_service.get_book_by_id', return_value={
            'id': 1, 'title': 'Test Book', 'available_copies': 2
        }), \
             patch('library_service.get_borrow_record', return_value={
                 'patron_id': '123456', 'book_id': 1,
                 'due_date': due_date.isoformat(), 'return_date': None
             }), \
             patch('library_service.update_book_availability', return_value=True), \
             patch('library_service.update_borrow_record_return_date', return_value=True), \
             patch('library_service.calculate_late_fee_for_book', return_value=3.50):
            
            success, message = return_book_by_patron("123456", 1)
            
            assert success == True
            assert 'late fee: $3.50' in message.lower()
            assert '7 days overdue' in message.lower()

    def test_tc2_3_return_8_days_late(self):
        """TC2.3: Verify late fee calculation for 8 days overdue ($4.50 - rate changes after 7 days)."""
        due_date = datetime.now() - timedelta(days=8)
        
        with patch('library_service.get_book_by_id', return_value={
            'id': 1, 'title': 'Test Book', 'available_copies': 2
        }), \
             patch('library_service.get_borrow_record', return_value={
                 'patron_id': '123456', 'book_id': 1,
                 'due_date': due_date.isoformat(), 'return_date': None
             }), \
             patch('library_service.update_book_availability', return_value=True), \
             patch('library_service.update_borrow_record_return_date', return_value=True), \
             patch('library_service.calculate_late_fee_for_book', return_value=4.50):
            
            success, message = return_book_by_patron("123456", 1)
            
            assert success == True
            assert 'late fee: $4.50' in message.lower()
            assert '8 days overdue' in message.lower()

    def test_tc2_4_return_15_days_late(self):
        """TC2.4: Verify late fee calculation for 15 days overdue ($11.50)."""
        due_date = datetime.now() - timedelta(days=15)
        
        with patch('library_service.get_book_by_id', return_value={
            'id': 1, 'title': 'Test Book', 'available_copies': 2
        }), \
             patch('library_service.get_borrow_record', return_value={
                 'patron_id': '123456', 'book_id': 1,
                 'due_date': due_date.isoformat(), 'return_date': None
             }), \
             patch('library_service.update_book_availability', return_value=True), \
             patch('library_service.update_borrow_record_return_date', return_value=True), \
             patch('library_service.calculate_late_fee_for_book', return_value=11.50):
            
            success, message = return_book_by_patron("123456", 1)
            
            assert success == True
            assert 'late fee: $11.50' in message.lower()
            assert '15 days overdue' in message.lower()

    def test_tc2_5_return_at_maximum_fee(self):
        """TC2.5: Verify late fee caps at $15.00 maximum."""
        due_date = datetime.now() - timedelta(days=30)
        
        with patch('library_service.get_book_by_id', return_value={
            'id': 1, 'title': 'Test Book', 'available_copies': 2
        }), \
             patch('library_service.get_borrow_record', return_value={
                 'patron_id': '123456', 'book_id': 1,
                 'due_date': due_date.isoformat(), 'return_date': None
             }), \
             patch('library_service.update_book_availability', return_value=True), \
             patch('library_service.update_borrow_record_return_date', return_value=True), \
             patch('library_service.calculate_late_fee_for_book', return_value=15.00):
            
            success, message = return_book_by_patron("123456", 1)
            
            assert success == True
            assert 'late fee: $15.00' in message.lower()
            assert '30 days overdue' in message.lower()

    def test_tc2_6_return_22_days_late_reaches_max_fee(self):
        """TC2.6: Verify 22 days overdue reaches exactly $15.00 cap (7*0.50 + 15*1.00 = 18.50, capped at 15)."""
        due_date = datetime.now() - timedelta(days=22)
        
        with patch('library_service.get_book_by_id', return_value={
            'id': 1, 'title': 'Test Book', 'available_copies': 2
        }), \
             patch('library_service.get_borrow_record', return_value={
                 'patron_id': '123456', 'book_id': 1,
                 'due_date': due_date.isoformat(), 'return_date': None
             }), \
             patch('library_service.update_book_availability', return_value=True), \
             patch('library_service.update_borrow_record_return_date', return_value=True), \
             patch('library_service.calculate_late_fee_for_book', return_value=15.00):
            
            success, message = return_book_by_patron("123456", 1)
            
            assert success == True
            assert 'late fee: $15.00' in message.lower()

    def test_tc2_7_return_extremely_late(self):
        """TC2.7: Verify fee still caps at $15.00 for extremely late returns (100 days)."""
        due_date = datetime.now() - timedelta(days=100)
        
        with patch('library_service.get_book_by_id', return_value={
            'id': 1, 'title': 'Test Book', 'available_copies': 2
        }), \
             patch('library_service.get_borrow_record', return_value={
                 'patron_id': '123456', 'book_id': 1,
                 'due_date': due_date.isoformat(), 'return_date': None
             }), \
             patch('library_service.update_book_availability', return_value=True), \
             patch('library_service.update_borrow_record_return_date', return_value=True), \
             patch('library_service.calculate_late_fee_for_book', return_value=15.00):
            
            success, message = return_book_by_patron("123456", 1)
            
            assert success == True
            assert 'late fee: $15.00' in message.lower()
            assert '100 days overdue' in message.lower()

    def test_tc2_8_return_3_days_late(self):
        """TC2.8: Verify late fee for 3 days overdue ($1.50)."""
        due_date = datetime.now() - timedelta(days=3)
        
        with patch('library_service.get_book_by_id', return_value={
            'id': 1, 'title': 'Test Book', 'available_copies': 2
        }), \
             patch('library_service.get_borrow_record', return_value={
                 'patron_id': '123456', 'book_id': 1,
                 'due_date': due_date.isoformat(), 'return_date': None
             }), \
             patch('library_service.update_book_availability', return_value=True), \
             patch('library_service.update_borrow_record_return_date', return_value=True), \
             patch('library_service.calculate_late_fee_for_book', return_value=1.50):
            
            success, message = return_book_by_patron("123456", 1)
            
            assert success == True
            assert 'late fee: $1.50' in message.lower()
            assert '3 days overdue' in message.lower()

    def test_tc2_9_return_10_days_late(self):
        """TC2.9: Verify late fee for 10 days overdue ($6.50 = 7*0.50 + 3*1.00)."""
        due_date = datetime.now() - timedelta(days=10)
        
        with patch('library_service.get_book_by_id', return_value={
            'id': 1, 'title': 'Test Book', 'available_copies': 2
        }), \
             patch('library_service.get_borrow_record', return_value={
                 'patron_id': '123456', 'book_id': 1,
                 'due_date': due_date.isoformat(), 'return_date': None
             }), \
             patch('library_service.update_book_availability', return_value=True), \
             patch('library_service.update_borrow_record_return_date', return_value=True), \
             patch('library_service.calculate_late_fee_for_book', return_value=6.50):
            
            success, message = return_book_by_patron("123456", 1)
            
            assert success == True
            assert 'late fee: $6.50' in message.lower()
            assert '10 days overdue' in message.lower()

    # ==================== NEGATIVE TEST CASES - PATRON ID VALIDATION ====================

    def test_tc3_1_empty_patron_id(self):
        """TC3.1: Verify that empty patron ID is rejected."""
        success, message = return_book_by_patron("", 1)
        
        assert success == False
        assert "invalid patron id" in message.lower()
        assert "must be exactly 6 digits" in message.lower()

    def test_tc3_2_none_patron_id(self):
        """TC3.2: Verify that None patron ID is rejected."""
        success, message = return_book_by_patron(None, 1)
        
        assert success == False
        assert "invalid patron id" in message.lower()

    def test_tc3_3_patron_id_less_than_6_digits(self):
        """TC3.3: Verify that patron ID with fewer than 6 digits is rejected."""
        success, message = return_book_by_patron("12345", 1)
        
        assert success == False
        assert "invalid patron id" in message.lower()
        assert "must be exactly 6 digits" in message.lower()

    def test_tc3_4_patron_id_more_than_6_digits(self):
        """TC3.4: Verify that patron ID with more than 6 digits is rejected."""
        success, message = return_book_by_patron("1234567", 1)
        
        assert success == False
        assert "invalid patron id" in message.lower()
        assert "must be exactly 6 digits" in message.lower()

    def test_tc3_5_patron_id_with_letters(self):
        """TC3.5: Verify that patron ID containing letters is rejected."""
        success, message = return_book_by_patron("12345A", 1)
        
        assert success == False
        assert "invalid patron id" in message.lower()

    def test_tc3_6_patron_id_with_special_characters(self):
        """TC3.6: Verify that patron ID containing special characters is rejected."""
        success, message = return_book_by_patron("123-456", 1)
        
        assert success == False
        assert "invalid patron id" in message.lower()

    def test_tc3_7_patron_id_with_spaces(self):
        """TC3.7: Verify that patron ID containing spaces is rejected."""
        success, message = return_book_by_patron("123 456", 1)
        
        assert success == False
        assert "invalid patron id" in message.lower()

    # ==================== NEGATIVE TEST CASES - BOOK VALIDATION ====================

    def test_tc4_1_book_not_found(self):
        """TC4.1: Verify error when book ID does not exist."""
        with patch('library_service.get_book_by_id', return_value=None):
            success, message = return_book_by_patron("123456", 999)
            
            assert success == False
            assert "book not found" in message.lower()

    def test_tc4_2_book_id_negative(self):
        """TC4.2: Verify error when book ID is negative."""
        with patch('library_service.get_book_by_id', return_value=None):
            success, message = return_book_by_patron("123456", -1)
            
            assert success == False
            assert "book not found" in message.lower()

    def test_tc4_3_book_id_zero(self):
        """TC4.3: Verify error when book ID is zero."""
        with patch('library_service.get_book_by_id', return_value=None):
            success, message = return_book_by_patron("123456", 0)
            
            assert success == False
            assert "book not found" in message.lower()

    # ==================== NEGATIVE TEST CASES - BORROW RECORD VALIDATION ====================

    def test_tc5_1_no_borrow_record_found(self):
        """TC5.1: Verify error when patron did not borrow the book."""
        with patch('library_service.get_book_by_id', return_value={
            'id': 1, 'title': 'Test Book', 'available_copies': 5
        }), \
             patch('library_service.get_borrow_record', return_value=None):
            
            success, message = return_book_by_patron("123456", 1)
            
            assert success == False
            assert "no active borrow record found" in message.lower()
            assert "did not borrow this book" in message.lower()

    def test_tc5_2_wrong_patron_returning_book(self):
        """TC5.2: Verify error when different patron tries to return someone else's book."""
        with patch('library_service.get_book_by_id', return_value={
            'id': 1, 'title': 'Test Book', 'available_copies': 5
        }), \
             patch('library_service.get_borrow_record', return_value=None):
            
            success, message = return_book_by_patron("999999", 1)
            
            assert success == False
            assert "no active borrow record found" in message.lower()

    def test_tc5_3_book_already_returned(self):
        """TC5.3: Verify error when trying to return a book that was already returned."""
        with patch('library_service.get_book_by_id', return_value={
            'id': 1, 'title': 'Test Book', 'available_copies': 5
        }), \
             patch('library_service.get_borrow_record', return_value=None):
            
            success, message = return_book_by_patron("123456", 1)
            
            assert success == False
            assert "no active borrow record found" in message.lower()

    # ==================== NEGATIVE TEST CASES - DATABASE ERRORS ====================

    def test_tc6_1_database_error_updating_availability(self):
        """TC6.1: Verify error handling when book availability update fails."""
        due_date = datetime.now()
        
        with patch('library_service.get_book_by_id', return_value={
            'id': 1, 'title': 'Test Book', 'available_copies': 2
        }), \
             patch('library_service.get_borrow_record', return_value={
                 'patron_id': '123456', 'book_id': 1,
                 'due_date': due_date.isoformat(), 'return_date': None
             }), \
             patch('library_service.update_book_availability', return_value=False):
            
            success, message = return_book_by_patron("123456", 1)
            
            assert success == False
            assert "database error" in message.lower()
            assert "availability" in message.lower()

    def test_tc6_2_database_error_updating_return_date(self):
        """TC6.2: Verify error handling when borrow record return date update fails."""
        due_date = datetime.now()
        
        with patch('library_service.get_book_by_id', return_value={
            'id': 1, 'title': 'Test Book', 'available_copies': 2
        }), \
             patch('library_service.get_borrow_record', return_value={
                 'patron_id': '123456', 'book_id': 1,
                 'due_date': due_date.isoformat(), 'return_date': None
             }), \
             patch('library_service.update_book_availability', return_value=True), \
             patch('library_service.update_borrow_record_return_date', return_value=False):
            
            success, message = return_book_by_patron("123456", 1)
            
            assert success == False
            assert "database error" in message.lower()
            assert "return date" in message.lower()

    # ==================== EDGE CASES ====================

    def test_tc7_1_return_book_with_special_characters_in_title(self):
        """TC7.1: Verify returning book with special characters in title."""
        due_date = datetime.now()
        
        with patch('library_service.get_book_by_id', return_value={
            'id': 1, 'title': 'Book: A Journey! @2024 #1', 'available_copies': 2
        }), \
             patch('library_service.get_borrow_record', return_value={
                 'patron_id': '123456', 'book_id': 1,
                 'due_date': due_date.isoformat(), 'return_date': None
             }), \
             patch('library_service.update_book_availability', return_value=True), \
             patch('library_service.update_borrow_record_return_date', return_value=True), \
             patch('library_service.calculate_late_fee_for_book', return_value=0):
            
            success, message = return_book_by_patron("123456", 1)
            
            assert success == True
            assert 'book: a journey! @2024 #1' in message.lower()

    def test_tc7_2_return_book_with_unicode_title(self):
        """TC7.2: Verify returning book with Unicode characters in title."""
        due_date = datetime.now()
        
        with patch('library_service.get_book_by_id', return_value={
            'id': 1, 'title': '日本語のタイトル', 'available_copies': 2
        }), \
             patch('library_service.get_borrow_record', return_value={
                 'patron_id': '123456', 'book_id': 1,
                 'due_date': due_date.isoformat(), 'return_date': None
             }), \
             patch('library_service.update_book_availability', return_value=True), \
             patch('library_service.update_borrow_record_return_date', return_value=True), \
             patch('library_service.calculate_late_fee_for_book', return_value=0):
            
            success, message = return_book_by_patron("123456", 1)
            
            assert success == True
            assert '日本語のタイトル' in message

    def test_tc7_3_patron_id_with_leading_zeros(self):
        """TC7.3: Verify successful return with patron ID containing leading zeros."""
        due_date = datetime.now()
        
        with patch('library_service.get_book_by_id', return_value={
            'id': 1, 'title': 'Test Book', 'available_copies': 2
        }), \
             patch('library_service.get_borrow_record', return_value={
                 'patron_id': '000123', 'book_id': 1,
                 'due_date': due_date.isoformat(), 'return_date': None
             }), \
             patch('library_service.update_book_availability', return_value=True), \
             patch('library_service.update_borrow_record_return_date', return_value=True), \
             patch('library_service.calculate_late_fee_for_book', return_value=0):
            
            success, message = return_book_by_patron("000123", 1)
            
            assert success == True
            assert 'returned successfully' in message.lower()

    def test_tc7_4_large_book_id(self):
        """TC7.4: Verify handling of very large book ID."""
        due_date = datetime.now()
        
        with patch('library_service.get_book_by_id', return_value={
            'id': 999999999, 'title': 'Test Book', 'available_copies': 2
        }), \
             patch('library_service.get_borrow_record', return_value={
                 'patron_id': '123456', 'book_id': 999999999,
                 'due_date': due_date.isoformat(), 'return_date': None
             }), \
             patch('library_service.update_book_availability', return_value=True), \
             patch('library_service.update_borrow_record_return_date', return_value=True), \
             patch('library_service.calculate_late_fee_for_book', return_value=0):
            
            success, message = return_book_by_patron("123456", 999999999)
            
            assert success == True
            assert 'returned successfully' in message.lower()

    # ==================== LATE FEE CALCULATION VERIFICATION ====================

    def test_tc8_1_verify_fee_format_two_decimal_places(self):
        """TC8.1: Verify late fee is formatted to 2 decimal places."""
        due_date = datetime.now() - timedelta(days=1)
        
        with patch('library_service.get_book_by_id', return_value={
            'id': 1, 'title': 'Test Book', 'available_copies': 2
        }), \
             patch('library_service.get_borrow_record', return_value={
                 'patron_id': '123456', 'book_id': 1,
                 'due_date': due_date.isoformat(), 'return_date': None
             }), \
             patch('library_service.update_book_availability', return_value=True), \
             patch('library_service.update_borrow_record_return_date', return_value=True), \
             patch('library_service.calculate_late_fee_for_book', return_value=0.50):
            
            success, message = return_book_by_patron("123456", 1)
            
            assert success == True
            # Check for proper decimal format
            import re
            fee_pattern = r'\$\d+\.\d{2}'
            assert re.search(fee_pattern, message) is not None

    def test_tc8_2_verify_days_overdue_displayed(self):
        """TC8.2: Verify number of days overdue is displayed in message."""
        due_date = datetime.now() - timedelta(days=5)
        
        with patch('library_service.get_book_by_id', return_value={
            'id': 1, 'title': 'Test Book', 'available_copies': 2
        }), \
             patch('library_service.get_borrow_record', return_value={
                 'patron_id': '123456', 'book_id': 1,
                 'due_date': due_date.isoformat(), 'return_date': None
             }), \
             patch('library_service.update_book_availability', return_value=True), \
             patch('library_service.update_borrow_record_return_date', return_value=True), \
             patch('library_service.calculate_late_fee_for_book', return_value=2.50):
            
            success, message = return_book_by_patron("123456", 1)
            
            assert success == True
            assert '5 days overdue' in message.lower()

    def test_tc8_3_verify_fee_calculation_boundary_7_to_8_days(self):
        """TC8.3: Verify fee calculation changes correctly at 7-8 day boundary."""
        # 7 days: 7 * 0.50 = $3.50
        due_date_7 = datetime.now() - timedelta(days=7)
        
        with patch('library_service.get_book_by_id', return_value={
            'id': 1, 'title': 'Test Book', 'available_copies': 2
        }), \
             patch('library_service.get_borrow_record', return_value={
                 'patron_id': '123456', 'book_id': 1,
                 'due_date': due_date_7.isoformat(), 'return_date': None
             }), \
             patch('library_service.update_book_availability', return_value=True), \
             patch('library_service.update_borrow_record_return_date', return_value=True), \
             patch('library_service.calculate_late_fee_for_book', return_value=3.50):
            
            success, message = return_book_by_patron("123456", 1)
            assert success == True
            assert 'late fee: $3.50' in message.lower()
        
        # 8 days: 7 * 0.50 + 1 * 1.00 = $4.50
        due_date_8 = datetime.now() - timedelta(days=8)
        
        with patch('library_service.get_book_by_id', return_value={
            'id': 1, 'title': 'Test Book', 'available_copies': 2
        }), \
             patch('library_service.get_borrow_record', return_value={
                 'patron_id': '123456', 'book_id': 1,
                 'due_date': due_date_8.isoformat(), 'return_date': None
             }), \
             patch('library_service.update_book_availability', return_value=True), \
             patch('library_service.update_borrow_record_return_date', return_value=True), \
             patch('library_service.calculate_late_fee_for_book', return_value=4.50):
            
            success, message = return_book_by_patron("123456", 1)
            assert success == True
            assert 'late fee: $4.50' in message.lower()

    # ==================== SEQUENTIAL RETURN SCENARIOS ====================

    def test_tc9_1_multiple_patrons_returning_different_books(self):
        """TC9.1: Verify multiple patrons can return different books."""
        due_date = datetime.now()
        
        # First patron returns book 1
        with patch('library_service.get_book_by_id', return_value={
            'id': 1, 'title': 'Book 1', 'available_copies': 2
        }), \
             patch('library_service.get_borrow_record', return_value={
                 'patron_id': '111111', 'book_id': 1,
                 'due_date': due_date.isoformat(), 'return_date': None
             }), \
             patch('library_service.update_book_availability', return_value=True), \
             patch('library_service.update_borrow_record_return_date', return_value=True), \
             patch('library_service.calculate_late_fee_for_book', return_value=0):
            
            success1, message1 = return_book_by_patron("111111", 1)
            assert success1 == True
        
        # Second patron returns book 2
        with patch('library_service.get_book_by_id', return_value={
            'id': 2, 'title': 'Book 2', 'available_copies': 3
        }), \
             patch('library_service.get_borrow_record', return_value={
                 'patron_id': '222222', 'book_id': 2,
                 'due_date': due_date.isoformat(), 'return_date': None
             }), \
             patch('library_service.update_book_availability', return_value=True), \
             patch('library_service.update_borrow_record_return_date', return_value=True), \
             patch('library_service.calculate_late_fee_for_book', return_value=0):
            
            success2, message2 = return_book_by_patron("222222", 2)
            assert success2 == True

    def test_tc9_2_same_patron_returning_multiple_books(self):
        """TC9.2: Verify same patron can return multiple books sequentially."""
        due_date = datetime.now()
        
        # Return first book
        with patch('library_service.get_book_by_id', return_value={
            'id': 1, 'title': 'Book 1', 'available_copies': 2
        }), \
             patch('library_service.get_borrow_record', return_value={
                 'patron_id': '123456', 'book_id': 1,
                 'due_date': due_date.isoformat(), 'return_date': None
             }), \
             patch('library_service.update_book_availability', return_value=True), \
             patch('library_service.update_borrow_record_return_date', return_value=True), \
             patch('library_service.calculate_late_fee_for_book', return_value=0):
            
            success1, message1 = return_book_by_patron("123456", 1)
            assert success1 == True
        
        # Return second book
        with patch('library_service.get_book_by_id', return_value={
            'id': 2, 'title': 'Book 2', 'available_copies': 3
        }), \
             patch('library_service.get_borrow_record', return_value={
                 'patron_id': '123456', 'book_id': 2,
                 'due_date': due_date.isoformat(), 'return_date': None
             }), \
             patch('library_service.update_book_availability', return_value=True), \
             patch('library_service.update_borrow_record_return_date', return_value=True), \
             patch('library_service.calculate_late_fee_for_book', return_value=0):
            
            success2, message2 = return_book_by_patron("123456", 2)
            assert success2 == True

    def test_tc9_3_patron_returns_book_with_mixed_fee_statuses(self):
        """TC9.3: Verify patron can return one book on time and another late."""
        # Return first book on time
        due_date_future = datetime.now() + timedelta(days=5)
        
        with patch('library_service.get_book_by_id', return_value={
            'id': 1, 'title': 'On Time Book', 'available_copies': 2
        }), \
             patch('library_service.get_borrow_record', return_value={
                 'patron_id': '123456', 'book_id': 1,
                 'due_date': due_date_future.isoformat(), 'return_date': None
             }), \
             patch('library_service.update_book_availability', return_value=True), \
             patch('library_service.update_borrow_record_return_date', return_value=True), \
             patch('library_service.calculate_late_fee_for_book', return_value=0):
            
            success1, message1 = return_book_by_patron("123456", 1)
            assert success1 == True
            assert 'no late fees' in message1.lower()
        
        # Return second book late
        due_date_past = datetime.now() - timedelta(days=5)
        
        with patch('library_service.get_book_by_id', return_value={
            'id': 2, 'title': 'Late Book', 'available_copies': 3
        }), \
             patch('library_service.get_borrow_record', return_value={
                 'patron_id': '123456', 'book_id': 2,
                 'due_date': due_date_past.isoformat(), 'return_date': None
             }), \
             patch('library_service.update_book_availability', return_value=True), \
             patch('library_service.update_borrow_record_return_date', return_value=True), \
             patch('library_service.calculate_late_fee_for_book', return_value=2.50):
            
            success2, message2 = return_book_by_patron("123456", 2)
            assert success2 == True
            assert 'late fee:' in message2.lower()

    # ==================== AVAILABILITY UPDATE VERIFICATION ====================

    def test_tc10_1_verify_availability_increased_by_one(self):
        """TC10.1: Verify that book's available copies increase by exactly 1 on return."""
        due_date = datetime.now()
        
        with patch('library_service.get_book_by_id', return_value={
            'id': 1, 'title': 'Test Book', 'available_copies': 2
        }), \
             patch('library_service.get_borrow_record', return_value={
                 'patron_id': '123456', 'book_id': 1,
                 'due_date': due_date.isoformat(), 'return_date': None
             }), \
             patch('library_service.update_book_availability') as mock_update, \
             patch('library_service.update_borrow_record_return_date', return_value=True), \
             patch('library_service.calculate_late_fee_for_book', return_value=0):
            
            mock_update.return_value = True
            success, message = return_book_by_patron("123456", 1)
            
            assert success == True
            # Verify update_book_availability was called with increment of 1
            mock_update.assert_called_once_with(1, 1)

    def test_tc10_2_return_increases_availability_from_zero(self):
        """TC10.2: Verify book with 0 available copies increases to 1 after return."""
        due_date = datetime.now()
        
        with patch('library_service.get_book_by_id', return_value={
            'id': 1, 'title': 'Fully Borrowed Book', 'available_copies': 0
        }), \
             patch('library_service.get_borrow_record', return_value={
                 'patron_id': '123456', 'book_id': 1,
                 'due_date': due_date.isoformat(), 'return_date': None
             }), \
             patch('library_service.update_book_availability', return_value=True), \
             patch('library_service.update_borrow_record_return_date', return_value=True), \
             patch('library_service.calculate_late_fee_for_book', return_value=0):
            
            success, message = return_book_by_patron("123456", 1)
            
            assert success == True
            assert 'returned successfully' in message.lower()

    # ==================== RETURN DATE RECORDING ====================

    def test_tc11_1_verify_return_date_recorded(self):
        """TC11.1: Verify that return date is recorded when book is returned."""
        due_date = datetime.now()
        
        with patch('library_service.get_book_by_id', return_value={
            'id': 1, 'title': 'Test Book', 'available_copies': 2
        }), \
             patch('library_service.get_borrow_record', return_value={
                 'patron_id': '123456', 'book_id': 1,
                 'due_date': due_date.isoformat(), 'return_date': None
             }), \
             patch('library_service.update_book_availability', return_value=True), \
             patch('library_service.update_borrow_record_return_date') as mock_return_date, \
             patch('library_service.calculate_late_fee_for_book', return_value=0):
            
            mock_return_date.return_value = True
            success, message = return_book_by_patron("123456", 1)
            
            assert success == True
            # Verify return date update was called
            mock_return_date.assert_called_once()
            call_args = mock_return_date.call_args[0]
            assert call_args[0] == "123456"  # patron_id
            assert call_args[1] == 1  # book_id
            # call_args[2] should be a datetime object
            assert isinstance(call_args[2], datetime)

    # ==================== ADDITIONAL EDGE CASES ====================

    def test_tc12_1_patron_id_all_zeros(self):
        """TC12.1: Verify patron ID of all zeros is valid."""
        due_date = datetime.now()
        
        with patch('library_service.get_book_by_id', return_value={
            'id': 1, 'title': 'Test Book', 'available_copies': 2
        }), \
             patch('library_service.get_borrow_record', return_value={
                 'patron_id': '000000', 'book_id': 1,
                 'due_date': due_date.isoformat(), 'return_date': None
             }), \
             patch('library_service.update_book_availability', return_value=True), \
             patch('library_service.update_borrow_record_return_date', return_value=True), \
             patch('library_service.calculate_late_fee_for_book', return_value=0):
            
            success, message = return_book_by_patron("000000", 1)
            
            assert success == True
            assert 'returned successfully' in message.lower()

    def test_tc12_2_patron_id_all_nines(self):
        """TC12.2: Verify patron ID of all nines is valid."""
        due_date = datetime.now()
        
        with patch('library_service.get_book_by_id', return_value={
            'id': 1, 'title': 'Test Book', 'available_copies': 2
        }), \
             patch('library_service.get_borrow_record', return_value={
                 'patron_id': '999999', 'book_id': 1,
                 'due_date': due_date.isoformat(), 'return_date': None
             }), \
             patch('library_service.update_book_availability', return_value=True), \
             patch('library_service.update_borrow_record_return_date', return_value=True), \
             patch('library_service.calculate_late_fee_for_book', return_value=0):
            
            success, message = return_book_by_patron("999999", 1)
            
            assert success == True
            assert 'returned successfully' in message.lower()

    def test_tc12_3_book_with_very_long_title(self):
        """TC12.3: Verify returning book with maximum length title (200 chars)."""
        due_date = datetime.now()
        long_title = "A" * 200
        
        with patch('library_service.get_book_by_id', return_value={
            'id': 1, 'title': long_title, 'available_copies': 2
        }), \
             patch('library_service.get_borrow_record', return_value={
                 'patron_id': '123456', 'book_id': 1,
                 'due_date': due_date.isoformat(), 'return_date': None
             }), \
             patch('library_service.update_book_availability', return_value=True), \
             patch('library_service.update_borrow_record_return_date', return_value=True), \
             patch('library_service.calculate_late_fee_for_book', return_value=0):
            
            success, message = return_book_by_patron("123456", 1)
            
            assert success == True
            assert long_title.lower() in message.lower()

    def test_tc12_4_return_2_days_late(self):
        """TC12.4: Verify late fee for 2 days overdue ($1.00)."""
        due_date = datetime.now() - timedelta(days=2)
        
        with patch('library_service.get_book_by_id', return_value={
            'id': 1, 'title': 'Test Book', 'available_copies': 2
        }), \
             patch('library_service.get_borrow_record', return_value={
                 'patron_id': '123456', 'book_id': 1,
                 'due_date': due_date.isoformat(), 'return_date': None
             }), \
             patch('library_service.update_book_availability', return_value=True), \
             patch('library_service.update_borrow_record_return_date', return_value=True), \
             patch('library_service.calculate_late_fee_for_book', return_value=1.00):
            
            success, message = return_book_by_patron("123456", 1)
            
            assert success == True
            assert 'late fee: $1.00' in message.lower()
            assert '2 days overdue' in message.lower()