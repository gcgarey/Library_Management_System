# PYTHONPATH=. pytest tests/f5_test.py
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from library_service import calculate_late_fee_for_book
from database import init_database, get_db_connection


class TestR5LateFeeCalculation:
    """Test cases for R5: Late Fee Calculation API"""

    def setup_method(self):
        """Setup test database before each test"""
        init_database()
        # Clear existing data
        conn = get_db_connection()
        conn.execute('DELETE FROM borrow_records')
        conn.execute('DELETE FROM books')
        conn.commit()
        conn.close()

    # ==================== POSITIVE TEST CASES - NO LATE FEE ====================

    def test_tc1_1_book_not_overdue(self):
        """TC1.1: Verify zero fee when book is not yet due."""
        due_date = datetime.now() + timedelta(days=5)
        
        with patch('library_service.get_borrow_record', return_value={
            'patron_id': '123456',
            'book_id': 1,
            'due_date': due_date.isoformat(),
            'return_date': None
        }):
            result = calculate_late_fee_for_book("123456", 1)
            
            assert result['status'] == 'success'
            assert result['fee_amount'] == 0.00
            assert result['days_overdue'] == 0
            assert 'not overdue' in result['message'].lower()

    def test_tc1_2_book_due_today(self):
        """TC1.2: Verify zero fee when book is due today (boundary - not overdue)."""
        due_date = datetime.now()
        
        with patch('library_service.get_borrow_record', return_value={
            'patron_id': '123456',
            'book_id': 1,
            'due_date': due_date.isoformat(),
            'return_date': None
        }):
            result = calculate_late_fee_for_book("123456", 1)
            
            assert result['status'] == 'success'
            assert result['fee_amount'] == 0.00
            assert result['days_overdue'] == 0
            assert 'not overdue' in result['message'].lower()

    def test_tc1_3_book_returned_on_time(self):
        """TC1.3: Verify zero fee for book returned before due date."""
        due_date = datetime.now() + timedelta(days=7)
        
        with patch('library_service.get_borrow_record', return_value={
            'patron_id': '123456',
            'book_id': 1,
            'due_date': due_date.isoformat(),
            'return_date': None
        }):
            result = calculate_late_fee_for_book("123456", 1)
            
            assert result['status'] == 'success'
            assert result['fee_amount'] == 0.00
            assert result['days_overdue'] == 0

    # ==================== POSITIVE TEST CASES - FEES FOR 1-7 DAYS ($0.50/DAY) ====================

    def test_tc2_1_one_day_overdue(self):
        """TC2.1: Verify fee for 1 day overdue ($0.50)."""
        due_date = datetime.now() - timedelta(days=1)
        
        with patch('library_service.get_borrow_record', return_value={
            'patron_id': '123456',
            'book_id': 1,
            'due_date': due_date.isoformat(),
            'return_date': None
        }):
            result = calculate_late_fee_for_book("123456", 1)
            
            assert result['status'] == 'success'
            assert result['fee_amount'] == 0.50
            assert result['days_overdue'] == 1
            assert '1 day(s) overdue' in result['message']

    def test_tc2_2_two_days_overdue(self):
        """TC2.2: Verify fee for 2 days overdue ($1.00)."""
        due_date = datetime.now() - timedelta(days=2)
        
        with patch('library_service.get_borrow_record', return_value={
            'patron_id': '123456',
            'book_id': 1,
            'due_date': due_date.isoformat(),
            'return_date': None
        }):
            result = calculate_late_fee_for_book("123456", 1)
            
            assert result['status'] == 'success'
            assert result['fee_amount'] == 1.00
            assert result['days_overdue'] == 2

    def test_tc2_3_three_days_overdue(self):
        """TC2.3: Verify fee for 3 days overdue ($1.50)."""
        due_date = datetime.now() - timedelta(days=3)
        
        with patch('library_service.get_borrow_record', return_value={
            'patron_id': '123456',
            'book_id': 1,
            'due_date': due_date.isoformat(),
            'return_date': None
        }):
            result = calculate_late_fee_for_book("123456", 1)
            
            assert result['status'] == 'success'
            assert result['fee_amount'] == 1.50
            assert result['days_overdue'] == 3

    def test_tc2_4_four_days_overdue(self):
        """TC2.4: Verify fee for 4 days overdue ($2.00)."""
        due_date = datetime.now() - timedelta(days=4)
        
        with patch('library_service.get_borrow_record', return_value={
            'patron_id': '123456',
            'book_id': 1,
            'due_date': due_date.isoformat(),
            'return_date': None
        }):
            result = calculate_late_fee_for_book("123456", 1)
            
            assert result['status'] == 'success'
            assert result['fee_amount'] == 2.00
            assert result['days_overdue'] == 4

    def test_tc2_5_five_days_overdue(self):
        """TC2.5: Verify fee for 5 days overdue ($2.50)."""
        due_date = datetime.now() - timedelta(days=5)
        
        with patch('library_service.get_borrow_record', return_value={
            'patron_id': '123456',
            'book_id': 1,
            'due_date': due_date.isoformat(),
            'return_date': None
        }):
            result = calculate_late_fee_for_book("123456", 1)
            
            assert result['status'] == 'success'
            assert result['fee_amount'] == 2.50
            assert result['days_overdue'] == 5

    def test_tc2_6_six_days_overdue(self):
        """TC2.6: Verify fee for 6 days overdue ($3.00)."""
        due_date = datetime.now() - timedelta(days=6)
        
        with patch('library_service.get_borrow_record', return_value={
            'patron_id': '123456',
            'book_id': 1,
            'due_date': due_date.isoformat(),
            'return_date': None
        }):
            result = calculate_late_fee_for_book("123456", 1)
            
            assert result['status'] == 'success'
            assert result['fee_amount'] == 3.00
            assert result['days_overdue'] == 6

    def test_tc2_7_seven_days_overdue(self):
        """TC2.7: Verify fee for 7 days overdue ($3.50 - boundary)."""
        due_date = datetime.now() - timedelta(days=7)
        
        with patch('library_service.get_borrow_record', return_value={
            'patron_id': '123456',
            'book_id': 1,
            'due_date': due_date.isoformat(),
            'return_date': None
        }):
            result = calculate_late_fee_for_book("123456", 1)
            
            assert result['status'] == 'success'
            assert result['fee_amount'] == 3.50
            assert result['days_overdue'] == 7

    # ==================== POSITIVE TEST CASES - FEES FOR 8+ DAYS ($1.00/DAY AFTER 7) ====================

    def test_tc3_1_eight_days_overdue(self):
        """TC3.1: Verify fee for 8 days overdue ($4.50 - rate changes after day 7)."""
        due_date = datetime.now() - timedelta(days=8)
        
        with patch('library_service.get_borrow_record', return_value={
            'patron_id': '123456',
            'book_id': 1,
            'due_date': due_date.isoformat(),
            'return_date': None
        }):
            result = calculate_late_fee_for_book("123456", 1)
            
            assert result['status'] == 'success'
            assert result['fee_amount'] == 4.50
            assert result['days_overdue'] == 8

    def test_tc3_2_nine_days_overdue(self):
        """TC3.2: Verify fee for 9 days overdue ($5.50)."""
        due_date = datetime.now() - timedelta(days=9)
        
        with patch('library_service.get_borrow_record', return_value={
            'patron_id': '123456',
            'book_id': 1,
            'due_date': due_date.isoformat(),
            'return_date': None
        }):
            result = calculate_late_fee_for_book("123456", 1)
            
            assert result['status'] == 'success'
            assert result['fee_amount'] == 5.50
            assert result['days_overdue'] == 9

    def test_tc3_3_ten_days_overdue(self):
        """TC3.3: Verify fee for 10 days overdue ($6.50)."""
        due_date = datetime.now() - timedelta(days=10)
        
        with patch('library_service.get_borrow_record', return_value={
            'patron_id': '123456',
            'book_id': 1,
            'due_date': due_date.isoformat(),
            'return_date': None
        }):
            result = calculate_late_fee_for_book("123456", 1)
            
            assert result['status'] == 'success'
            assert result['fee_amount'] == 6.50
            assert result['days_overdue'] == 10

    def test_tc3_4_fifteen_days_overdue(self):
        """TC3.4: Verify fee for 15 days overdue ($11.50)."""
        due_date = datetime.now() - timedelta(days=15)
        
        with patch('library_service.get_borrow_record', return_value={
            'patron_id': '123456',
            'book_id': 1,
            'due_date': due_date.isoformat(),
            'return_date': None
        }):
            result = calculate_late_fee_for_book("123456", 1)
            
            assert result['status'] == 'success'
            assert result['fee_amount'] == 11.50
            assert result['days_overdue'] == 15

    def test_tc3_5_twenty_days_overdue(self):
        """TC3.5: Verify fee for 20 days overdue ($15.00 - reaches cap)."""
        due_date = datetime.now() - timedelta(days=20)
        
        with patch('library_service.get_borrow_record', return_value={
            'patron_id': '123456',
            'book_id': 1,
            'due_date': due_date.isoformat(),
            'return_date': None
        }):
            result = calculate_late_fee_for_book("123456", 1)
            
            assert result['status'] == 'success'
            assert result['fee_amount'] == 15.00
            assert result['days_overdue'] == 20

    def test_tc3_6_twentytwo_days_overdue(self):
        """TC3.6: Verify fee caps at $15.00 for 22 days overdue."""
        due_date = datetime.now() - timedelta(days=22)
        
        with patch('library_service.get_borrow_record', return_value={
            'patron_id': '123456',
            'book_id': 1,
            'due_date': due_date.isoformat(),
            'return_date': None
        }):
            result = calculate_late_fee_for_book("123456", 1)
            
            assert result['status'] == 'success'
            assert result['fee_amount'] == 15.00
            assert result['days_overdue'] == 22

    def test_tc3_7_thirty_days_overdue(self):
        """TC3.7: Verify fee remains capped at $15.00 for 30 days overdue."""
        due_date = datetime.now() - timedelta(days=30)
        
        with patch('library_service.get_borrow_record', return_value={
            'patron_id': '123456',
            'book_id': 1,
            'due_date': due_date.isoformat(),
            'return_date': None
        }):
            result = calculate_late_fee_for_book("123456", 1)
            
            assert result['status'] == 'success'
            assert result['fee_amount'] == 15.00
            assert result['days_overdue'] == 30

    def test_tc3_8_hundred_days_overdue(self):
        """TC3.8: Verify fee remains capped at $15.00 even for extremely overdue books (100 days)."""
        due_date = datetime.now() - timedelta(days=100)
        
        with patch('library_service.get_borrow_record', return_value={
            'patron_id': '123456',
            'book_id': 1,
            'due_date': due_date.isoformat(),
            'return_date': None
        }):
            result = calculate_late_fee_for_book("123456", 1)
            
            assert result['status'] == 'success'
            assert result['fee_amount'] == 15.00
            assert result['days_overdue'] == 100

    # ==================== NEGATIVE TEST CASES - PATRON ID VALIDATION ====================

    def test_tc4_1_empty_patron_id(self):
        """TC4.1: Verify error response for empty patron ID."""
        result = calculate_late_fee_for_book("", 1)
        
        assert result['status'] == 'error'
        assert result['fee_amount'] == 0.00
        assert result['days_overdue'] == 0
        assert 'invalid patron id' in result['message'].lower()

    def test_tc4_2_none_patron_id(self):
        """TC4.2: Verify error response for None patron ID."""
        result = calculate_late_fee_for_book(None, 1)
        
        assert result['status'] == 'error'
        assert result['fee_amount'] == 0.00
        assert result['days_overdue'] == 0
        assert 'invalid patron id' in result['message'].lower()

    def test_tc4_3_patron_id_less_than_6_digits(self):
        """TC4.3: Verify error for patron ID with fewer than 6 digits."""
        result = calculate_late_fee_for_book("12345", 1)
        
        assert result['status'] == 'error'
        assert result['fee_amount'] == 0.00
        assert 'must be exactly 6 digits' in result['message'].lower()

    def test_tc4_4_patron_id_more_than_6_digits(self):
        """TC4.4: Verify error for patron ID with more than 6 digits."""
        result = calculate_late_fee_for_book("1234567", 1)
        
        assert result['status'] == 'error'
        assert result['fee_amount'] == 0.00
        assert 'must be exactly 6 digits' in result['message'].lower()

    def test_tc4_5_patron_id_with_letters(self):
        """TC4.5: Verify error for patron ID containing letters."""
        result = calculate_late_fee_for_book("12345A", 1)
        
        assert result['status'] == 'error'
        assert result['fee_amount'] == 0.00
        assert 'invalid patron id' in result['message'].lower()

    def test_tc4_6_patron_id_with_special_characters(self):
        """TC4.6: Verify error for patron ID with special characters."""
        result = calculate_late_fee_for_book("123-456", 1)
        
        assert result['status'] == 'error'
        assert result['fee_amount'] == 0.00
        assert 'invalid patron id' in result['message'].lower()

    def test_tc4_7_patron_id_with_spaces(self):
        """TC4.7: Verify error for patron ID with spaces."""
        result = calculate_late_fee_for_book("123 456", 1)
        
        assert result['status'] == 'error'
        assert result['fee_amount'] == 0.00
        assert 'invalid patron id' in result['message'].lower()

    # ==================== NEGATIVE TEST CASES - NO BORROW RECORD ====================

    def test_tc5_1_no_borrow_record_found(self):
        """TC5.1: Verify error when no borrow record exists."""
        with patch('library_service.get_borrow_record', return_value=None):
            result = calculate_late_fee_for_book("123456", 1)
            
            assert result['status'] == 'error'
            assert result['fee_amount'] == 0.00
            assert result['days_overdue'] == 0
            assert 'no active borrow record found' in result['message'].lower()

    def test_tc5_2_wrong_patron_book_combination(self):
        """TC5.2: Verify error for non-existent patron-book combination."""
        with patch('library_service.get_borrow_record', return_value=None):
            result = calculate_late_fee_for_book("999999", 999)
            
            assert result['status'] == 'error'
            assert result['fee_amount'] == 0.00
            assert 'no active borrow record found' in result['message'].lower()

    def test_tc5_3_invalid_book_id(self):
        """TC5.3: Verify error for invalid book ID."""
        with patch('library_service.get_borrow_record', return_value=None):
            result = calculate_late_fee_for_book("123456", -1)
            
            assert result['status'] == 'error'
            assert result['fee_amount'] == 0.00

    # ==================== RESPONSE FORMAT VALIDATION ====================

    def test_tc6_1_response_contains_all_required_fields(self):
        """TC6.1: Verify response contains all required JSON fields."""
        due_date = datetime.now() - timedelta(days=5)
        
        with patch('library_service.get_borrow_record', return_value={
            'patron_id': '123456',
            'book_id': 1,
            'due_date': due_date.isoformat(),
            'return_date': None
        }):
            result = calculate_late_fee_for_book("123456", 1)
            
            assert 'fee_amount' in result
            assert 'days_overdue' in result
            assert 'status' in result
            assert 'message' in result

    def test_tc6_2_fee_amount_is_float_with_two_decimals(self):
        """TC6.2: Verify fee_amount is properly rounded to 2 decimal places."""
        due_date = datetime.now() - timedelta(days=1)
        
        with patch('library_service.get_borrow_record', return_value={
            'patron_id': '123456',
            'book_id': 1,
            'due_date': due_date.isoformat(),
            'return_date': None
        }):
            result = calculate_late_fee_for_book("123456", 1)
            
            assert isinstance(result['fee_amount'], float)
            assert result['fee_amount'] == round(result['fee_amount'], 2)

    def test_tc6_3_days_overdue_is_integer(self):
        """TC6.3: Verify days_overdue is an integer."""
        due_date = datetime.now() - timedelta(days=3)
        
        with patch('library_service.get_borrow_record', return_value={
            'patron_id': '123456',
            'book_id': 1,
            'due_date': due_date.isoformat(),
            'return_date': None
        }):
            result = calculate_late_fee_for_book("123456", 1)
            
            assert isinstance(result['days_overdue'], int)

    def test_tc6_4_status_is_success_or_error(self):
        """TC6.4: Verify status field contains either 'success' or 'error'."""
        due_date = datetime.now() - timedelta(days=1)
        
        with patch('library_service.get_borrow_record', return_value={
            'patron_id': '123456',
            'book_id': 1,
            'due_date': due_date.isoformat(),
            'return_date': None
        }):
            result = calculate_late_fee_for_book("123456", 1)
            
            assert result['status'] in ['success', 'error']

    def test_tc6_5_message_field_is_string(self):
        """TC6.5: Verify message field is a string."""
        due_date = datetime.now() - timedelta(days=2)
        
        with patch('library_service.get_borrow_record', return_value={
            'patron_id': '123456',
            'book_id': 1,
            'due_date': due_date.isoformat(),
            'return_date': None
        }):
            result = calculate_late_fee_for_book("123456", 1)
            
            assert isinstance(result['message'], str)
            assert len(result['message']) > 0

    # ==================== EDGE CASES ====================

    def test_tc7_1_patron_id_all_zeros(self):
        """TC7.1: Verify calculation works with patron ID of all zeros."""
        due_date = datetime.now() - timedelta(days=3)
        
        with patch('library_service.get_borrow_record', return_value={
            'patron_id': '000000',
            'book_id': 1,
            'due_date': due_date.isoformat(),
            'return_date': None
        }):
            result = calculate_late_fee_for_book("000000", 1)
            
            assert result['status'] == 'success'
            assert result['fee_amount'] == 1.50

    def test_tc7_2_patron_id_all_nines(self):
        """TC7.2: Verify calculation works with patron ID of all nines."""
        due_date = datetime.now() - timedelta(days=4)
        
        with patch('library_service.get_borrow_record', return_value={
            'patron_id': '999999',
            'book_id': 1,
            'due_date': due_date.isoformat(),
            'return_date': None
        }):
            result = calculate_late_fee_for_book("999999", 1)
            
            assert result['status'] == 'success'
            assert result['fee_amount'] == 2.00

    def test_tc7_3_patron_id_with_leading_zeros(self):
        """TC7.3: Verify calculation with patron ID containing leading zeros."""
        due_date = datetime.now() - timedelta(days=2)
        
        with patch('library_service.get_borrow_record', return_value={
            'patron_id': '000123',
            'book_id': 1,
            'due_date': due_date.isoformat(),
            'return_date': None
        }):
            result = calculate_late_fee_for_book("000123", 1)
            
            assert result['status'] == 'success'
            assert result['fee_amount'] == 1.00

    def test_tc7_4_large_book_id(self):
        """TC7.4: Verify calculation with very large book ID."""
        due_date = datetime.now() - timedelta(days=5)
        
        with patch('library_service.get_borrow_record', return_value={
            'patron_id': '123456',
            'book_id': 999999999,
            'due_date': due_date.isoformat(),
            'return_date': None
        }):
            result = calculate_late_fee_for_book("123456", 999999999)
            
            assert result['status'] == 'success'
            assert result['fee_amount'] == 2.50

    def test_tc7_5_book_id_zero(self):
        """TC7.5: Verify handling of book ID zero."""
        with patch('library_service.get_borrow_record', return_value=None):
            result = calculate_late_fee_for_book("123456", 0)
            
            assert result['status'] == 'error'
            assert result['fee_amount'] == 0.00

    def test_tc7_6_book_id_negative(self):
        """TC7.6: Verify handling of negative book ID."""
        with patch('library_service.get_borrow_record', return_value=None):
            result = calculate_late_fee_for_book("123456", -999)
            
            assert result['status'] == 'error'
            assert result['fee_amount'] == 0.00

    # ==================== BOUNDARY TESTING - FEE CALCULATION ====================

    def test_tc8_1_boundary_exactly_seven_days(self):
        """TC8.1: Verify fee calculation boundary at exactly 7 days ($3.50)."""
        due_date = datetime.now() - timedelta(days=7)
        
        with patch('library_service.get_borrow_record', return_value={
            'patron_id': '123456',
            'book_id': 1,
            'due_date': due_date.isoformat(),
            'return_date': None
        }):
            result = calculate_late_fee_for_book("123456", 1)
            
            assert result['fee_amount'] == 3.50
            assert result['days_overdue'] == 7

    def test_tc8_2_boundary_exactly_eight_days(self):
        """TC8.2: Verify rate change boundary at 8 days ($4.50)."""
        due_date = datetime.now() - timedelta(days=8)
        
        with patch('library_service.get_borrow_record', return_value={
            'patron_id': '123456',
            'book_id': 1,
            'due_date': due_date.isoformat(),
            'return_date': None
        }):
            result = calculate_late_fee_for_book("123456", 1)
            
            assert result['fee_amount'] == 4.50
            assert result['days_overdue'] == 8

    def test_tc8_3_boundary_fee_reaches_cap_at_22_days(self):
        """TC8.3: Verify fee reaches $15.00 cap at 22 days (7*0.50 + 15*1.00 = 18.50, capped at 15)."""
        due_date = datetime.now() - timedelta(days=22)
        
        with patch('library_service.get_borrow_record', return_value={
            'patron_id': '123456',
            'book_id': 1,
            'due_date': due_date.isoformat(),
            'return_date': None
        }):
            result = calculate_late_fee_for_book("123456", 1)
            
            assert result['fee_amount'] == 15.00
            assert result['days_overdue'] == 22

    def test_tc8_4_boundary_one_day_before_cap(self):
        """TC8.4: Verify fee at 21 days (21 days = $17.50 before cap, capped at $15.00)."""
        due_date = datetime.now() - timedelta(days=21)

        with patch('library_service.get_borrow_record', return_value={
            'patron_id': '123456',
            'book_id': 1,
            'due_date': due_date.isoformat(),
            'return_date': None
        }):
            result = calculate_late_fee_for_book("123456", 1)

            assert result['fee_amount'] == 15.00
            assert result['days_overdue'] == 21

    # ==================== MULTIPLE CALCULATIONS ====================

    def test_tc9_1_same_patron_different_books(self):
        """TC9.1: Verify fee calculation for same patron with different books."""
        due_date = datetime.now() - timedelta(days=3)
        
        # First book
        with patch('library_service.get_borrow_record', return_value={
            'patron_id': '123456',
            'book_id': 1,
            'due_date': due_date.isoformat(),
            'return_date': None
        }):
            result1 = calculate_late_fee_for_book("123456", 1)
            assert result1['fee_amount'] == 1.50
        
        # Second book with different overdue days
        due_date2 = datetime.now() - timedelta(days=10)
        with patch('library_service.get_borrow_record', return_value={
            'patron_id': '123456',
            'book_id': 2,
            'due_date': due_date2.isoformat(),
            'return_date': None
        }):
            result2 = calculate_late_fee_for_book("123456", 2)
            assert result2['fee_amount'] == 6.50

    def test_tc9_2_different_patrons_same_book(self):
        """TC9.2: Verify fee calculation for different patrons with same book (shouldn't happen, but test API)."""
        due_date = datetime.now() - timedelta(days=5)
        
        # First patron
        with patch('library_service.get_borrow_record', return_value={
            'patron_id': '111111',
            'book_id': 1,
            'due_date': due_date.isoformat(),
            'return_date': None
        }):
            result1 = calculate_late_fee_for_book("111111", 1)
            assert result1['fee_amount'] == 2.50
        
        # Second patron (different record)
        with patch('library_service.get_borrow_record', return_value={
            'patron_id': '222222',
            'book_id': 1,
            'due_date': due_date.isoformat(),
            'return_date': None
        }):
            result2 = calculate_late_fee_for_book("222222", 1)
            assert result2['fee_amount'] == 2.50

    def test_tc9_3_patron_with_no_overdue_and_overdue_books(self):
        """TC9.3: Verify same patron can have books with and without fees."""
        # Book 1: Not overdue
        due_date_future = datetime.now() + timedelta(days=3)
        with patch('library_service.get_borrow_record', return_value={
            'patron_id': '123456',
            'book_id': 1,
            'due_date': due_date_future.isoformat(),
            'return_date': None
        }):
            result1 = calculate_late_fee_for_book("123456", 1)
            assert result1['fee_amount'] == 0.00
            assert result1['status'] == 'success'
        
        # Book 2: Overdue
        due_date_past = datetime.now() - timedelta(days=5)
        with patch('library_service.get_borrow_record', return_value={
            'patron_id': '123456',
            'book_id': 2,
            'due_date': due_date_past.isoformat(),
            'return_date': None
        }):
            result2 = calculate_late_fee_for_book("123456", 2)
            assert result2['fee_amount'] == 2.50
            assert result2['status'] == 'success'

    # ==================== MESSAGE CONTENT VERIFICATION ====================

    def test_tc10_1_success_message_includes_days_overdue(self):
        """TC10.1: Verify success message includes number of days overdue."""
        due_date = datetime.now() - timedelta(days=12)
        
        with patch('library_service.get_borrow_record', return_value={
            'patron_id': '123456',
            'book_id': 1,
            'due_date': due_date.isoformat(),
            'return_date': None
        }):
            result = calculate_late_fee_for_book("123456", 1)
            
            assert result['status'] == 'success'
            assert '12 day(s) overdue' in result['message']

    def test_tc10_2_not_overdue_message_clear(self):
        """TC10.2: Verify clear message when book is not overdue."""
        due_date = datetime.now() + timedelta(days=3)
        
        with patch('library_service.get_borrow_record', return_value={
            'patron_id': '123456',
            'book_id': 1,
            'due_date': due_date.isoformat(),
            'return_date': None
        }):
            result = calculate_late_fee_for_book("123456", 1)
            
            assert 'not overdue' in result['message'].lower()

    def test_tc10_3_error_message_for_invalid_patron(self):
        """TC10.3: Verify clear error message for invalid patron ID."""
        result = calculate_late_fee_for_book("ABC123", 1)
        
        assert 'invalid patron id' in result['message'].lower()
        assert 'must be exactly 6 digits' in result['message'].lower()

    def test_tc10_4_error_message_for_no_record(self):
        """TC10.4: Verify clear error message when no borrow record found."""
        with patch('library_service.get_borrow_record', return_value=None):
            result = calculate_late_fee_for_book("123456", 1)
            
            assert 'no active borrow record found' in result['message'].lower()

    # ==================== SPECIFIC DAY CALCULATIONS ====================

    def test_tc11_1_eleven_days_overdue(self):
        """TC11.1: Verify fee for 11 days overdue ($7.50 = 7*0.50 + 4*1.00)."""
        due_date = datetime.now() - timedelta(days=11)
        
        with patch('library_service.get_borrow_record', return_value={
            'patron_id': '123456',
            'book_id': 1,
            'due_date': due_date.isoformat(),
            'return_date': None
        }):
            result = calculate_late_fee_for_book("123456", 1)
            
            assert result['status'] == 'success'
            assert result['fee_amount'] == 7.50
            assert result['days_overdue'] == 11

    def test_tc11_2_twelve_days_overdue(self):
        """TC11.2: Verify fee for 12 days overdue ($8.50)."""
        due_date = datetime.now() - timedelta(days=12)
        
        with patch('library_service.get_borrow_record', return_value={
            'patron_id': '123456',
            'book_id': 1,
            'due_date': due_date.isoformat(),
            'return_date': None
        }):
            result = calculate_late_fee_for_book("123456", 1)
            
            assert result['status'] == 'success'
            assert result['fee_amount'] == 8.50
            assert result['days_overdue'] == 12

    def test_tc11_3_thirteen_days_overdue(self):
        """TC11.3: Verify fee for 13 days overdue ($9.50)."""
        due_date = datetime.now() - timedelta(days=13)
        
        with patch('library_service.get_borrow_record', return_value={
            'patron_id': '123456',
            'book_id': 1,
            'due_date': due_date.isoformat(),
            'return_date': None
        }):
            result = calculate_late_fee_for_book("123456", 1)
            
            assert result['status'] == 'success'
            assert result['fee_amount'] == 9.50
            assert result['days_overdue'] == 13

    def test_tc11_4_fourteen_days_overdue(self):
        """TC11.4: Verify fee for 14 days overdue ($10.50 - exactly 2 weeks late)."""
        due_date = datetime.now() - timedelta(days=14)
        
        with patch('library_service.get_borrow_record', return_value={
            'patron_id': '123456',
            'book_id': 1,
            'due_date': due_date.isoformat(),
            'return_date': None
        }):
            result = calculate_late_fee_for_book("123456", 1)
            
            assert result['status'] == 'success'
            assert result['fee_amount'] == 10.50
            assert result['days_overdue'] == 14

    def test_tc11_5_nineteen_days_overdue(self):
        """TC11.5: Verify fee for 19 days overdue ($15.00 - at cap)."""
        due_date = datetime.now() - timedelta(days=19)
        
        with patch('library_service.get_borrow_record', return_value={
            'patron_id': '123456',
            'book_id': 1,
            'due_date': due_date.isoformat(),
            'return_date': None
        }):
            result = calculate_late_fee_for_book("123456", 1)
            
            assert result['status'] == 'success'
            assert result['fee_amount'] == 15.00
            assert result['days_overdue'] == 19

    def test_tc11_6_twentyone_days_overdue(self):
        """TC11.6: Verify fee for 21 days overdue ($17.50 = 7*0.50 + 14*1.00, capped at $15.00)."""
        due_date = datetime.now() - timedelta(days=21)

        with patch('library_service.get_borrow_record', return_value={
            'patron_id': '123456',
            'book_id': 1,
            'due_date': due_date.isoformat(),
            'return_date': None
        }):
            result = calculate_late_fee_for_book("123456", 1)

            assert result['status'] == 'success'
            assert result['fee_amount'] == 15.00
            assert result['days_overdue'] == 21

    # ==================== RETURN VALUE TYPE VERIFICATION ====================

    def test_tc12_1_return_type_is_dictionary(self):
        """TC12.1: Verify function returns a dictionary."""
        due_date = datetime.now() - timedelta(days=5)
        
        with patch('library_service.get_borrow_record', return_value={
            'patron_id': '123456',
            'book_id': 1,
            'due_date': due_date.isoformat(),
            'return_date': None
        }):
            result = calculate_late_fee_for_book("123456", 1)
            
            assert isinstance(result, dict)

    def test_tc12_2_fee_amount_never_negative(self):
        """TC12.2: Verify fee_amount is never negative."""
        # Not overdue case
        due_date = datetime.now() + timedelta(days=5)
        
        with patch('library_service.get_borrow_record', return_value={
            'patron_id': '123456',
            'book_id': 1,
            'due_date': due_date.isoformat(),
            'return_date': None
        }):
            result = calculate_late_fee_for_book("123456", 1)
            
            assert result['fee_amount'] >= 0.00

    def test_tc12_3_days_overdue_never_negative_in_response(self):
        """TC12.3: Verify days_overdue is never negative in response (shows 0 when not overdue)."""
        due_date = datetime.now() + timedelta(days=5)
        
        with patch('library_service.get_borrow_record', return_value={
            'patron_id': '123456',
            'book_id': 1,
            'due_date': due_date.isoformat(),
            'return_date': None
        }):
            result = calculate_late_fee_for_book("123456", 1)
            
            assert result['days_overdue'] >= 0

    def test_tc12_4_fee_never_exceeds_maximum(self):
        """TC12.4: Verify fee_amount never exceeds $15.00 maximum."""
        test_days = [20, 22, 30, 50, 100, 365]
        
        for days in test_days:
            due_date = datetime.now() - timedelta(days=days)
            
            with patch('library_service.get_borrow_record', return_value={
                'patron_id': '123456',
                'book_id': 1,
                'due_date': due_date.isoformat(),
                'return_date': None
            }):
                result = calculate_late_fee_for_book("123456", 1)
                
                assert result['fee_amount'] <= 15.00, f"Fee exceeded maximum for {days} days"

    # ==================== ERROR RESPONSE CONSISTENCY ====================

    def test_tc13_1_all_error_responses_have_zero_fee(self):
        """TC13.1: Verify all error responses return 0.00 fee."""
        # Empty patron ID
        result1 = calculate_late_fee_for_book("", 1)
        assert result1['fee_amount'] == 0.00
        
        # Invalid patron ID
        result2 = calculate_late_fee_for_book("ABC123", 1)
        assert result2['fee_amount'] == 0.00
        
        # No record
        with patch('library_service.get_borrow_record', return_value=None):
            result3 = calculate_late_fee_for_book("123456", 1)
            assert result3['fee_amount'] == 0.00

    def test_tc13_2_all_error_responses_have_zero_days_overdue(self):
        """TC13.2: Verify all error responses return 0 days_overdue."""
        # Empty patron ID
        result1 = calculate_late_fee_for_book("", 1)
        assert result1['days_overdue'] == 0
        
        # No record
        with patch('library_service.get_borrow_record', return_value=None):
            result2 = calculate_late_fee_for_book("123456", 1)
            assert result2['days_overdue'] == 0

    def test_tc13_3_all_error_responses_have_error_status(self):
        """TC13.3: Verify all error responses have 'error' status."""
        # Invalid patron ID
        result1 = calculate_late_fee_for_book("12345", 1)
        assert result1['status'] == 'error'
        
        # No record
        with patch('library_service.get_borrow_record', return_value=None):
            result2 = calculate_late_fee_for_book("123456", 1)
            assert result2['status'] == 'error'

    # ==================== COMPREHENSIVE FEE PROGRESSION TEST ====================

    def test_tc14_1_fee_progression_days_1_through_25(self):
        """TC14.1: Verify correct fee calculation for days 1-25 (comprehensive progression)."""
        expected_fees = {
            1: 0.50, 2: 1.00, 3: 1.50, 4: 2.00, 5: 2.50, 6: 3.00, 7: 3.50,
            8: 4.50, 9: 5.50, 10: 6.50, 11: 7.50, 12: 8.50, 13: 9.50, 14: 10.50,
            15: 11.50, 16: 12.50, 17: 13.50, 18: 14.50, 19: 15.00, 20: 15.00,
            21: 15.00, 22: 15.00, 23: 15.00, 24: 15.00, 25: 15.00
        }
        
        for days, expected_fee in expected_fees.items():
            due_date = datetime.now() - timedelta(days=days)
            
            with patch('library_service.get_borrow_record', return_value={
                'patron_id': '123456',
                'book_id': 1,
                'due_date': due_date.isoformat(),
                'return_date': None
            }):
                result = calculate_late_fee_for_book("123456", 1)
                
                assert result['fee_amount'] == expected_fee, \
                    f"Day {days}: Expected ${expected_fee}, got ${result['fee_amount']}"
                assert result['days_overdue'] == days