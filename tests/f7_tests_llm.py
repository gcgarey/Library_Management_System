# PYTHONPATH=. pytest tests/f7_test.py
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from library_service import get_patron_status_report
from database import init_database, get_db_connection


class TestR7PatronStatusReport:
    """Test cases for R7: Patron Status Report"""

    def setup_method(self):
        """Setup test database before each test"""
        init_database()
        # Clear existing data
        conn = get_db_connection()
        conn.execute('DELETE FROM borrow_records')
        conn.execute('DELETE FROM books')
        conn.commit()
        conn.close()

    # ==================== POSITIVE TEST CASES - PATRON WITH BORROWED BOOKS ====================

    def test_tc1_1_patron_with_one_borrowed_book_no_fees(self):
        """TC1.1: Verify status report for patron with one borrowed book and no late fees."""
        due_date = datetime.now() + timedelta(days=7)
        
        with patch('library_service.get_patron_borrowed_books', return_value=[
            {'book_id': 1, 'title': 'Test Book', 'due_date': due_date.isoformat()}
        ]), \
             patch('library_service.calculate_late_fee_for_book', return_value={
                 'status': 'success', 'fee_amount': 0.00, 'days_overdue': 0
             }), \
             patch('library_service.get_borrowing_history', return_value=[]):
            
            result = get_patron_status_report("123456")
            
            assert result['status'] == 'success'
            assert result['patron_id'] == "123456"
            assert len(result['currently_borrowed_books']) == 1
            assert result['total_late_fees'] == 0.00
            assert result['num_books_borrowed'] == 1
            assert result['borrowing_history'] == []

    def test_tc1_2_patron_with_multiple_borrowed_books_no_fees(self):
        """TC1.2: Verify status report for patron with multiple borrowed books and no fees."""
        due_date = datetime.now() + timedelta(days=7)
        
        with patch('library_service.get_patron_borrowed_books', return_value=[
            {'book_id': 1, 'title': 'Book 1', 'due_date': due_date.isoformat()},
            {'book_id': 2, 'title': 'Book 2', 'due_date': due_date.isoformat()},
            {'book_id': 3, 'title': 'Book 3', 'due_date': due_date.isoformat()}
        ]), \
             patch('library_service.calculate_late_fee_for_book', return_value={
                 'status': 'success', 'fee_amount': 0.00, 'days_overdue': 0
             }), \
             patch('library_service.get_borrowing_history', return_value=[]):
            
            result = get_patron_status_report("123456")
            
            assert result['status'] == 'success'
            assert len(result['currently_borrowed_books']) == 3
            assert result['total_late_fees'] == 0.00
            assert result['num_books_borrowed'] == 3

    def test_tc1_3_patron_with_one_overdue_book(self):
        """TC1.3: Verify status report for patron with one overdue book."""
        due_date = datetime.now() - timedelta(days=5)
        
        with patch('library_service.get_patron_borrowed_books', return_value=[
            {'book_id': 1, 'title': 'Overdue Book', 'due_date': due_date.isoformat()}
        ]), \
             patch('library_service.calculate_late_fee_for_book', return_value={
                 'status': 'success', 'fee_amount': 2.50, 'days_overdue': 5
             }), \
             patch('library_service.get_borrowing_history', return_value=[]):
            
            result = get_patron_status_report("123456")
            
            assert result['status'] == 'success'
            assert result['total_late_fees'] == 2.50
            assert result['num_books_borrowed'] == 1

    def test_tc1_4_patron_with_multiple_overdue_books(self):
        """TC1.4: Verify total late fees calculated correctly for multiple overdue books."""
        due_date = datetime.now() - timedelta(days=5)
        
        with patch('library_service.get_patron_borrowed_books', return_value=[
            {'book_id': 1, 'title': 'Book 1', 'due_date': due_date.isoformat()},
            {'book_id': 2, 'title': 'Book 2', 'due_date': due_date.isoformat()},
            {'book_id': 3, 'title': 'Book 3', 'due_date': due_date.isoformat()}
        ]), \
             patch('library_service.calculate_late_fee_for_book', side_effect=[
                 {'status': 'success', 'fee_amount': 2.50, 'days_overdue': 5},
                 {'status': 'success', 'fee_amount': 3.50, 'days_overdue': 7},
                 {'status': 'success', 'fee_amount': 5.00, 'days_overdue': 10}
             ]), \
             patch('library_service.get_borrowing_history', return_value=[]):
            
            result = get_patron_status_report("123456")
            
            assert result['status'] == 'success'
            assert result['total_late_fees'] == 11.00
            assert result['num_books_borrowed'] == 3

    def test_tc1_5_patron_with_mixed_due_and_overdue_books(self):
        """TC1.5: Verify status report for patron with both on-time and overdue books."""
        future_due = datetime.now() + timedelta(days=7)
        past_due = datetime.now() - timedelta(days=3)
        
        with patch('library_service.get_patron_borrowed_books', return_value=[
            {'book_id': 1, 'title': 'On Time Book', 'due_date': future_due.isoformat()},
            {'book_id': 2, 'title': 'Overdue Book', 'due_date': past_due.isoformat()}
        ]), \
             patch('library_service.calculate_late_fee_for_book', side_effect=[
                 {'status': 'success', 'fee_amount': 0.00, 'days_overdue': 0},
                 {'status': 'success', 'fee_amount': 1.50, 'days_overdue': 3}
             ]), \
             patch('library_service.get_borrowing_history', return_value=[]):
            
            result = get_patron_status_report("123456")
            
            assert result['status'] == 'success'
            assert result['total_late_fees'] == 1.50
            assert result['num_books_borrowed'] == 2

    def test_tc1_6_patron_at_borrowing_limit(self):
        """TC1.6: Verify status report for patron at maximum borrowing limit (5 books)."""
        due_date = datetime.now() + timedelta(days=7)
        
        with patch('library_service.get_patron_borrowed_books', return_value=[
            {'book_id': i, 'title': f'Book {i}', 'due_date': due_date.isoformat()}
            for i in range(1, 6)
        ]), \
             patch('library_service.calculate_late_fee_for_book', return_value={
                 'status': 'success', 'fee_amount': 0.00, 'days_overdue': 0
             }), \
             patch('library_service.get_borrowing_history', return_value=[]):
            
            result = get_patron_status_report("123456")
            
            assert result['status'] == 'success'
            assert result['num_books_borrowed'] == 5
            assert len(result['currently_borrowed_books']) == 5

    # ==================== POSITIVE TEST CASES - PATRON WITH NO BORROWED BOOKS ====================

    def test_tc2_1_patron_with_no_borrowed_books(self):
        """TC2.1: Verify status report for patron with no currently borrowed books."""
        with patch('library_service.get_patron_borrowed_books', return_value=[]), \
             patch('library_service.get_borrowing_history', return_value=[]):
            
            result = get_patron_status_report("123456")
            
            assert result['status'] == 'success'
            assert result['patron_id'] == "123456"
            assert result['currently_borrowed_books'] == []
            assert result['total_late_fees'] == 0.00
            assert result['num_books_borrowed'] == 0
            assert result['borrowing_history'] == []

    def test_tc2_2_new_patron_no_history(self):
        """TC2.2: Verify status report for new patron with no borrowing history."""
        with patch('library_service.get_patron_borrowed_books', return_value=[]), \
             patch('library_service.get_borrowing_history', return_value=[]):
            
            result = get_patron_status_report("000001")
            
            assert result['status'] == 'success'
            assert result['num_books_borrowed'] == 0
            assert len(result['borrowing_history']) == 0

    # ==================== POSITIVE TEST CASES - BORROWING HISTORY ====================

    def test_tc3_1_patron_with_borrowing_history_no_current_books(self):
        """TC3.1: Verify status report includes borrowing history when no books currently borrowed."""
        with patch('library_service.get_patron_borrowed_books', return_value=[]), \
             patch('library_service.get_borrowing_history', return_value=[
                 {'book_id': 1, 'title': 'Returned Book 1', 'borrow_date': '2024-01-01', 'return_date': '2024-01-15'},
                 {'book_id': 2, 'title': 'Returned Book 2', 'borrow_date': '2024-02-01', 'return_date': '2024-02-10'}
             ]):
            
            result = get_patron_status_report("123456")
            
            assert result['status'] == 'success'
            assert result['num_books_borrowed'] == 0
            assert len(result['borrowing_history']) == 2

    def test_tc3_2_patron_with_borrowing_history_and_current_books(self):
        """TC3.2: Verify status report includes both current books and history."""
        due_date = datetime.now() + timedelta(days=7)
        
        with patch('library_service.get_patron_borrowed_books', return_value=[
            {'book_id': 3, 'title': 'Current Book', 'due_date': due_date.isoformat()}
        ]), \
             patch('library_service.calculate_late_fee_for_book', return_value={
                 'status': 'success', 'fee_amount': 0.00, 'days_overdue': 0
             }), \
             patch('library_service.get_borrowing_history', return_value=[
                 {'book_id': 1, 'title': 'Returned Book 1', 'borrow_date': '2024-01-01', 'return_date': '2024-01-15'},
                 {'book_id': 2, 'title': 'Returned Book 2', 'borrow_date': '2024-02-01', 'return_date': '2024-02-10'}
             ]):
            
            result = get_patron_status_report("123456")
            
            assert result['status'] == 'success'
            assert result['num_books_borrowed'] == 1
            assert len(result['borrowing_history']) == 2

    def test_tc3_3_patron_with_extensive_borrowing_history(self):
        """TC3.3: Verify status report handles extensive borrowing history."""
        history = [
            {'book_id': i, 'title': f'Returned Book {i}', 
             'borrow_date': '2024-01-01', 'return_date': '2024-01-15'}
            for i in range(1, 21)
        ]
        
        with patch('library_service.get_patron_borrowed_books', return_value=[]), \
             patch('library_service.get_borrowing_history', return_value=history):
            
            result = get_patron_status_report("123456")
            
            assert result['status'] == 'success'
            assert len(result['borrowing_history']) == 20

    # ==================== NEGATIVE TEST CASES - INVALID PATRON ID ====================

    def test_tc4_1_empty_patron_id(self):
        """TC4.1: Verify error response for empty patron ID."""
        result = get_patron_status_report("")
        
        assert result['status'] == 'error'
        assert 'invalid patron id' in result['message'].lower()
        assert result['currently_borrowed_books'] == []
        assert result['total_late_fees'] == 0.00
        assert result['num_books_borrowed'] == 0
        assert result['borrowing_history'] == []

    def test_tc4_2_none_patron_id(self):
        """TC4.2: Verify error response for None patron ID."""
        result = get_patron_status_report(None)
        
        assert result['status'] == 'error'
        assert 'invalid patron id' in result['message'].lower()

    def test_tc4_3_patron_id_less_than_6_digits(self):
        """TC4.3: Verify error for patron ID with fewer than 6 digits."""
        result = get_patron_status_report("12345")
        
        assert result['status'] == 'error'
        assert 'must be exactly 6 digits' in result['message'].lower()

    def test_tc4_4_patron_id_more_than_6_digits(self):
        """TC4.4: Verify error for patron ID with more than 6 digits."""
        result = get_patron_status_report("1234567")
        
        assert result['status'] == 'error'
        assert 'must be exactly 6 digits' in result['message'].lower()

    def test_tc4_5_patron_id_with_letters(self):
        """TC4.5: Verify error for patron ID containing letters."""
        result = get_patron_status_report("12345A")
        
        assert result['status'] == 'error'
        assert 'invalid patron id' in result['message'].lower()

    def test_tc4_6_patron_id_with_special_characters(self):
        """TC4.6: Verify error for patron ID with special characters."""
        result = get_patron_status_report("123-456")
        
        assert result['status'] == 'error'
        assert 'invalid patron id' in result['message'].lower()

    def test_tc4_7_patron_id_with_spaces(self):
        """TC4.7: Verify error for patron ID with spaces."""
        result = get_patron_status_report("123 456")
        
        assert result['status'] == 'error'
        assert 'invalid patron id' in result['message'].lower()

    # ==================== RESPONSE FORMAT VALIDATION ====================

    def test_tc5_1_response_contains_all_required_fields(self):
        """TC5.1: Verify response contains all required fields."""
        with patch('library_service.get_patron_borrowed_books', return_value=[]), \
             patch('library_service.get_borrowing_history', return_value=[]):
            
            result = get_patron_status_report("123456")
            
            assert 'status' in result
            assert 'patron_id' in result
            assert 'currently_borrowed_books' in result
            assert 'total_late_fees' in result
            assert 'num_books_borrowed' in result
            assert 'borrowing_history' in result

    def test_tc5_2_currently_borrowed_books_is_list(self):
        """TC5.2: Verify currently_borrowed_books is a list."""
        with patch('library_service.get_patron_borrowed_books', return_value=[]), \
             patch('library_service.get_borrowing_history', return_value=[]):
            
            result = get_patron_status_report("123456")
            
            assert isinstance(result['currently_borrowed_books'], list)

    def test_tc5_3_total_late_fees_is_float(self):
        """TC5.3: Verify total_late_fees is a float."""
        with patch('library_service.get_patron_borrowed_books', return_value=[]), \
             patch('library_service.get_borrowing_history', return_value=[]):
            
            result = get_patron_status_report("123456")
            
            assert isinstance(result['total_late_fees'], float)

    def test_tc5_4_num_books_borrowed_is_integer(self):
        """TC5.4: Verify num_books_borrowed is an integer."""
        with patch('library_service.get_patron_borrowed_books', return_value=[]), \
             patch('library_service.get_borrowing_history', return_value=[]):
            
            result = get_patron_status_report("123456")
            
            assert isinstance(result['num_books_borrowed'], int)

    def test_tc5_5_borrowing_history_is_list(self):
        """TC5.5: Verify borrowing_history is a list."""
        with patch('library_service.get_patron_borrowed_books', return_value=[]), \
             patch('library_service.get_borrowing_history', return_value=[]):
            
            result = get_patron_status_report("123456")
            
            assert isinstance(result['borrowing_history'], list)

    def test_tc5_6_total_late_fees_rounded_to_two_decimals(self):
        """TC5.6: Verify total_late_fees is rounded to 2 decimal places."""
        due_date = datetime.now() - timedelta(days=3)
        
        with patch('library_service.get_patron_borrowed_books', return_value=[
            {'book_id': 1, 'title': 'Book 1', 'due_date': due_date.isoformat()}
        ]), \
             patch('library_service.calculate_late_fee_for_book', return_value={
                 'status': 'success', 'fee_amount': 1.567, 'days_overdue': 3
             }), \
             patch('library_service.get_borrowing_history', return_value=[]):
            
            result = get_patron_status_report("123456")
            
            assert result['total_late_fees'] == round(result['total_late_fees'], 2)

    # ==================== LATE FEE CALCULATION EDGE CASES ====================

    def test_tc6_1_late_fee_calculation_error_handled(self):
        """TC6.1: Verify late fee calculation errors are handled gracefully."""
        due_date = datetime.now() - timedelta(days=5)
        
        with patch('library_service.get_patron_borrowed_books', return_value=[
            {'book_id': 1, 'title': 'Book 1', 'due_date': due_date.isoformat()}
        ]), \
             patch('library_service.calculate_late_fee_for_book', return_value={
                 'status': 'error', 'fee_amount': 0.00, 'days_overdue': 0
             }), \
             patch('library_service.get_borrowing_history', return_value=[]):
            
            result = get_patron_status_report("123456")
            
            assert result['status'] == 'success'
            assert result['total_late_fees'] == 0.00

    def test_tc6_2_multiple_books_some_with_fee_errors(self):
        """TC6.2: Verify total fees calculated correctly when some fee calculations error."""
        due_date = datetime.now() - timedelta(days=5)
        
        with patch('library_service.get_patron_borrowed_books', return_value=[
            {'book_id': 1, 'title': 'Book 1', 'due_date': due_date.isoformat()},
            {'book_id': 2, 'title': 'Book 2', 'due_date': due_date.isoformat()},
            {'book_id': 3, 'title': 'Book 3', 'due_date': due_date.isoformat()}
        ]), \
             patch('library_service.calculate_late_fee_for_book', side_effect=[
                 {'status': 'success', 'fee_amount': 2.50, 'days_overdue': 5},
                 {'status': 'error', 'fee_amount': 0.00, 'days_overdue': 0},
                 {'status': 'success', 'fee_amount': 3.00, 'days_overdue': 6}
             ]), \
             patch('library_service.get_borrowing_history', return_value=[]):
            
            result = get_patron_status_report("123456")
            
            assert result['status'] == 'success'
            assert result['total_late_fees'] == 5.50

    def test_tc6_3_patron_with_maximum_late_fees(self):
        """TC6.3: Verify status report with maximum late fees ($15.00 per book)."""
        due_date = datetime.now() - timedelta(days=30)
        
        with patch('library_service.get_patron_borrowed_books', return_value=[
            {'book_id': 1, 'title': 'Book 1', 'due_date': due_date.isoformat()},
            {'book_id': 2, 'title': 'Book 2', 'due_date': due_date.isoformat()}
        ]), \
             patch('library_service.calculate_late_fee_for_book', return_value={
                 'status': 'success', 'fee_amount': 15.00, 'days_overdue': 30
             }), \
             patch('library_service.get_borrowing_history', return_value=[]):
            
            result = get_patron_status_report("123456")
            
            assert result['status'] == 'success'
            assert result['total_late_fees'] == 30.00

    # ==================== EDGE CASES ====================

    def test_tc7_1_patron_id_all_zeros(self):
        """TC7.1: Verify status report works with patron ID of all zeros."""
        with patch('library_service.get_patron_borrowed_books', return_value=[]), \
             patch('library_service.get_borrowing_history', return_value=[]):
            
            result = get_patron_status_report("000000")
            
            assert result['status'] == 'success'
            assert result['patron_id'] == "000000"

    def test_tc7_2_patron_id_all_nines(self):
        """TC7.2: Verify status report works with patron ID of all nines."""
        with patch('library_service.get_patron_borrowed_books', return_value=[]), \
             patch('library_service.get_borrowing_history', return_value=[]):
            
            result = get_patron_status_report("999999")
            
            assert result['status'] == 'success'
            assert result['patron_id'] == "999999"

    def test_tc7_3_patron_id_with_leading_zeros(self):
        """TC7.3: Verify status report preserves leading zeros in patron ID."""
        with patch('library_service.get_patron_borrowed_books', return_value=[]), \
             patch('library_service.get_borrowing_history', return_value=[]):
            
            result = get_patron_status_report("000123")
            
            assert result['status'] == 'success'
            assert result['patron_id'] == "000123"

    def test_tc7_4_patron_with_books_having_various_due_dates(self):
        """TC7.4: Verify status report with books having various due dates."""
        with patch('library_service.get_patron_borrowed_books', return_value=[
            {'book_id': 1, 'title': 'Book 1', 'due_date': (datetime.now() + timedelta(days=1)).isoformat()},
            {'book_id': 2, 'title': 'Book 2', 'due_date': (datetime.now() + timedelta(days=7)).isoformat()},
            {'book_id': 3, 'title': 'Book 3', 'due_date': (datetime.now() + timedelta(days=14)).isoformat()}
        ]), \
             patch('library_service.calculate_late_fee_for_book', return_value={
                 'status': 'success', 'fee_amount': 0.00, 'days_overdue': 0
             }), \
             patch('library_service.get_borrowing_history', return_value=[]):
            
            result = get_patron_status_report("123456")
            
            assert result['status'] == 'success'
            assert result['num_books_borrowed'] == 3

    # ==================== BORROWED BOOKS DETAILS ====================

    def test_tc8_1_borrowed_books_include_due_dates(self):
        """TC8.1: Verify borrowed books include due date information."""
        due_date = datetime.now() + timedelta(days=7)
        
        with patch('library_service.get_patron_borrowed_books', return_value=[
            {'book_id': 1, 'title': 'Test Book', 'due_date': due_date.isoformat(), 
             'author': 'Test Author', 'isbn': '9781234567890'}
        ]), \
             patch('library_service.calculate_late_fee_for_book', return_value={
                 'status': 'success', 'fee_amount': 0.00, 'days_overdue': 0
             }), \
             patch('library_service.get_borrowing_history', return_value=[]):
            
            result = get_patron_status_report("123456")
            
            assert result['status'] == 'success'
            assert 'due_date' in result['currently_borrowed_books'][0]

    def test_tc8_2_borrowed_books_include_book_details(self):
        """TC8.2: Verify borrowed books include book details (title, author, ISBN)."""
        due_date = datetime.now() + timedelta(days=7)
        
        with patch('library_service.get_patron_borrowed_books', return_value=[
            {'book_id': 1, 'title': 'The Great Gatsby', 'due_date': due_date.isoformat(),
             'author': 'F. Scott Fitzgerald', 'isbn': '9780743273565'}
        ]), \
             patch('library_service.calculate_late_fee_for_book', return_value={
                 'status': 'success', 'fee_amount': 0.00, 'days_overdue': 0
             }), \
             patch('library_service.get_borrowing_history', return_value=[]):
            
            result = get_patron_status_report("123456")
            
            book = result['currently_borrowed_books'][0]
            assert 'title' in book
            assert book['title'] == 'The Great Gatsby'

    # ==================== NUM_BOOKS_BORROWED VALIDATION ====================

    def test_tc9_1_num_books_borrowed_matches_list_length(self):
        """TC9.1: Verify num_books_borrowed matches length of currently_borrowed_books list."""
        due_date = datetime.now() + timedelta(days=7)
        
        with patch('library_service.get_patron_borrowed_books', return_value=[
            {'book_id': 1, 'title': 'Book 1', 'due_date': due_date.isoformat()},
            {'book_id': 2, 'title': 'Book 2', 'due_date': due_date.isoformat()},
            {'book_id': 3, 'title': 'Book 3', 'due_date': due_date.isoformat()}
        ]), \
             patch('library_service.calculate_late_fee_for_book', return_value={
                 'status': 'success', 'fee_amount': 0.00, 'days_overdue': 0
             }), \
             patch('library_service.get_borrowing_history', return_value=[]):
            
            result = get_patron_status_report("123456")
            
            assert result['num_books_borrowed'] == len(result['currently_borrowed_books'])

    def test_tc9_2_num_books_borrowed_zero_when_no_books(self):
        """TC9.2: Verify num_books_borrowed is 0 when patron has no books."""
        with patch('library_service.get_patron_borrowed_books', return_value=[]), \
             patch('library_service.get_borrowing_history', return_value=[]):
            
            result = get_patron_status_report("123456")
            
            assert result['num_books_borrowed'] == 0
            assert len(result['currently_borrowed_books']) == 0

    # ==================== ERROR RESPONSE CONSISTENCY ====================

    def test_tc10_1_error_response_has_default_values(self):
        """TC10.1: Verify error response contains default values for all fields."""
        result = get_patron_status_report("ABC123")
        
        assert result['status'] == 'error'
        assert result['currently_borrowed_books'] == []
        assert result['total_late_fees'] == 0.00
        assert result['num_books_borrowed'] == 0
        assert result['borrowing_history'] == []
        assert 'message' in result
        assert 'patron_id' in result

    def test_tc10_2_error_response_includes_patron_id(self):
        """TC10.2: Verify error response includes the invalid patron ID."""
        result = get_patron_status_report("12345")
        
        assert result['status'] == 'error'
        assert result['patron_id'] == "12345"

    def test_tc10_3_error_message_is_descriptive(self):
        """TC10.3: Verify error message is descriptive."""
        result = get_patron_status_report("")
        
        assert result['status'] == 'error'
        assert len(result['message']) > 0
        assert isinstance(result['message'], str)

    # ==================== LATE FEE AGGREGATION ====================

    def test_tc11_1_late_fees_sum_correctly_various_amounts(self):
        """TC11.1: Verify late fees from multiple books sum correctly."""
        due_date = datetime.now() - timedelta(days=5)
        
        with patch('library_service.get_patron_borrowed_books', return_value=[
            {'book_id': 1, 'title': 'Book 1', 'due_date': due_date.isoformat()},
            {'book_id': 2, 'title': 'Book 2', 'due_date': due_date.isoformat()},
            {'book_id': 3, 'title': 'Book 3', 'due_date': due_date.isoformat()},
            {'book_id': 4, 'title': 'Book 4', 'due_date': due_date.isoformat()}
        ]), \
             patch('library_service.calculate_late_fee_for_book', side_effect=[
                 {'status': 'success', 'fee_amount': 1.50, 'days_overdue': 3},
                 {'status': 'success', 'fee_amount': 2.00, 'days_overdue': 4},
                 {'status': 'success', 'fee_amount': 0.50, 'days_overdue': 1},
                 {'status': 'success', 'fee_amount': 3.50, 'days_overdue': 7}
             ]), \
             patch('library_service.get_borrowing_history', return_value=[]):
            
            result = get_patron_status_report("123456")
            
            assert result['status'] == 'success'
            assert result['total_late_fees'] == 7.50

    def test_tc11_2_late_fees_zero_when_all_books_on_time(self):
        """TC11.2: Verify late fees are 0.00 when all books are on time."""
        due_date = datetime.now() + timedelta(days=7)
        
        with patch('library_service.get_patron_borrowed_books', return_value=[
            {'book_id': 1, 'title': 'Book 1', 'due_date': due_date.isoformat()},
            {'book_id': 2, 'title': 'Book 2', 'due_date': due_date.isoformat()}
        ]), \
             patch('library_service.calculate_late_fee_for_book', return_value={
                 'status': 'success', 'fee_amount': 0.00, 'days_overdue': 0
             }), \
             patch('library_service.get_borrowing_history', return_value=[]):
            
            result = get_patron_status_report("123456")
            
            assert result['status'] == 'success'
            assert result['total_late_fees'] == 0.00

    def test_tc11_3_late_fees_with_decimal_precision(self):
        """TC11.3: Verify late fees maintain proper decimal precision."""
        due_date = datetime.now() - timedelta(days=5)
        
        with patch('library_service.get_patron_borrowed_books', return_value=[
            {'book_id': 1, 'title': 'Book 1', 'due_date': due_date.isoformat()},
            {'book_id': 2, 'title': 'Book 2', 'due_date': due_date.isoformat()}
        ]), \
             patch('library_service.calculate_late_fee_for_book', side_effect=[
                 {'status': 'success', 'fee_amount': 1.55, 'days_overdue': 3},
                 {'status': 'success', 'fee_amount': 2.67, 'days_overdue': 5}
             ]), \
             patch('library_service.get_borrowing_history', return_value=[]):
            
            result = get_patron_status_report("123456")
            
            assert result['status'] == 'success'
            assert result['total_late_fees'] == 4.22

    # ==================== BORROWING HISTORY DETAILS ====================

    def test_tc12_1_borrowing_history_includes_return_dates(self):
        """TC12.1: Verify borrowing history includes return dates."""
        with patch('library_service.get_patron_borrowed_books', return_value=[]), \
             patch('library_service.get_borrowing_history', return_value=[
                 {'book_id': 1, 'title': 'Returned Book', 'borrow_date': '2024-01-01', 
                  'return_date': '2024-01-15', 'due_date': '2024-01-14'}
             ]):
            
            result = get_patron_status_report("123456")
            
            assert result['status'] == 'success'
            assert 'return_date' in result['borrowing_history'][0]

    def test_tc12_2_borrowing_history_includes_borrow_dates(self):
        """TC12.2: Verify borrowing history includes borrow dates."""
        with patch('library_service.get_patron_borrowed_books', return_value=[]), \
             patch('library_service.get_borrowing_history', return_value=[
                 {'book_id': 1, 'title': 'Returned Book', 'borrow_date': '2024-01-01', 
                  'return_date': '2024-01-15'}
             ]):
            
            result = get_patron_status_report("123456")
            
            assert result['status'] == 'success'
            assert 'borrow_date' in result['borrowing_history'][0]

    def test_tc12_3_borrowing_history_includes_book_details(self):
        """TC12.3: Verify borrowing history includes book details."""
        with patch('library_service.get_patron_borrowed_books', return_value=[]), \
             patch('library_service.get_borrowing_history', return_value=[
                 {'book_id': 1, 'title': 'The Great Gatsby', 'author': 'F. Scott Fitzgerald',
                  'isbn': '9780743273565', 'borrow_date': '2024-01-01', 'return_date': '2024-01-15'}
             ]):
            
            result = get_patron_status_report("123456")
            
            history_item = result['borrowing_history'][0]
            assert 'title' in history_item
            assert 'book_id' in history_item

    def test_tc12_4_borrowing_history_chronological_order(self):
        """TC12.4: Verify borrowing history maintains order (most recent first or oldest first)."""
        with patch('library_service.get_patron_borrowed_books', return_value=[]), \
             patch('library_service.get_borrowing_history', return_value=[
                 {'book_id': 1, 'title': 'Book 1', 'borrow_date': '2024-01-01', 'return_date': '2024-01-15'},
                 {'book_id': 2, 'title': 'Book 2', 'borrow_date': '2024-02-01', 'return_date': '2024-02-15'},
                 {'book_id': 3, 'title': 'Book 3', 'borrow_date': '2024-03-01', 'return_date': '2024-03-15'}
             ]):
            
            result = get_patron_status_report("123456")
            
            assert result['status'] == 'success'
            assert len(result['borrowing_history']) == 3
            # Verify order is maintained as returned from database
            assert result['borrowing_history'][0]['book_id'] == 1
            assert result['borrowing_history'][1]['book_id'] == 2
            assert result['borrowing_history'][2]['book_id'] == 3

    # ==================== COMPREHENSIVE STATUS SCENARIOS ====================

    def test_tc13_1_active_patron_full_scenario(self):
        """TC13.1: Verify complete status report for active patron with mixed status."""
        current_due = datetime.now() + timedelta(days=7)
        overdue_date = datetime.now() - timedelta(days=5)
        
        with patch('library_service.get_patron_borrowed_books', return_value=[
            {'book_id': 1, 'title': 'Current Book 1', 'due_date': current_due.isoformat()},
            {'book_id': 2, 'title': 'Overdue Book', 'due_date': overdue_date.isoformat()}
        ]), \
             patch('library_service.calculate_late_fee_for_book', side_effect=[
                 {'status': 'success', 'fee_amount': 0.00, 'days_overdue': 0},
                 {'status': 'success', 'fee_amount': 2.50, 'days_overdue': 5}
             ]), \
             patch('library_service.get_borrowing_history', return_value=[
                 {'book_id': 3, 'title': 'Returned Book 1', 'borrow_date': '2024-01-01', 'return_date': '2024-01-15'},
                 {'book_id': 4, 'title': 'Returned Book 2', 'borrow_date': '2024-02-01', 'return_date': '2024-02-10'}
             ]):
            
            result = get_patron_status_report("123456")
            
            assert result['status'] == 'success'
            assert result['patron_id'] == "123456"
            assert result['num_books_borrowed'] == 2
            assert result['total_late_fees'] == 2.50
            assert len(result['currently_borrowed_books']) == 2
            assert len(result['borrowing_history']) == 2

    def test_tc13_2_patron_with_only_overdue_books(self):
        """TC13.2: Verify status report for patron with all books overdue."""
        overdue_date = datetime.now() - timedelta(days=10)
        
        with patch('library_service.get_patron_borrowed_books', return_value=[
            {'book_id': 1, 'title': 'Overdue Book 1', 'due_date': overdue_date.isoformat()},
            {'book_id': 2, 'title': 'Overdue Book 2', 'due_date': overdue_date.isoformat()},
            {'book_id': 3, 'title': 'Overdue Book 3', 'due_date': overdue_date.isoformat()}
        ]), \
             patch('library_service.calculate_late_fee_for_book', return_value={
                 'status': 'success', 'fee_amount': 6.50, 'days_overdue': 10
             }), \
             patch('library_service.get_borrowing_history', return_value=[]):
            
            result = get_patron_status_report("123456")
            
            assert result['status'] == 'success'
            assert result['num_books_borrowed'] == 3
            assert result['total_late_fees'] == 19.50  # 6.50 * 3

    def test_tc13_3_patron_recently_returned_all_books(self):
        """TC13.3: Verify status report for patron who recently returned all books."""
        with patch('library_service.get_patron_borrowed_books', return_value=[]), \
             patch('library_service.get_borrowing_history', return_value=[
                 {'book_id': 1, 'title': 'Recently Returned', 'borrow_date': '2024-10-01', 
                  'return_date': '2024-10-13'}
             ]):
            
            result = get_patron_status_report("123456")
            
            assert result['status'] == 'success'
            assert result['num_books_borrowed'] == 0
            assert result['total_late_fees'] == 0.00
            assert len(result['borrowing_history']) == 1

    # ==================== SPECIAL CHARACTERS AND UNICODE ====================

    def test_tc14_1_books_with_special_characters_in_titles(self):
        """TC14.1: Verify status report handles book titles with special characters."""
        due_date = datetime.now() + timedelta(days=7)
        
        with patch('library_service.get_patron_borrowed_books', return_value=[
            {'book_id': 1, 'title': 'Book: A Journey! @2024 #1', 'due_date': due_date.isoformat()}
        ]), \
             patch('library_service.calculate_late_fee_for_book', return_value={
                 'status': 'success', 'fee_amount': 0.00, 'days_overdue': 0
             }), \
             patch('library_service.get_borrowing_history', return_value=[]):
            
            result = get_patron_status_report("123456")
            
            assert result['status'] == 'success'
            assert result['currently_borrowed_books'][0]['title'] == 'Book: A Journey! @2024 #1'

    def test_tc14_2_books_with_unicode_titles(self):
        """TC14.2: Verify status report handles book titles with Unicode characters."""
        due_date = datetime.now() + timedelta(days=7)
        
        with patch('library_service.get_patron_borrowed_books', return_value=[
            {'book_id': 1, 'title': '日本語のタイトル', 'due_date': due_date.isoformat()}
        ]), \
             patch('library_service.calculate_late_fee_for_book', return_value={
                 'status': 'success', 'fee_amount': 0.00, 'days_overdue': 0
             }), \
             patch('library_service.get_borrowing_history', return_value=[]):
            
            result = get_patron_status_report("123456")
            
            assert result['status'] == 'success'
            assert result['currently_borrowed_books'][0]['title'] == '日本語のタイトル'

    # ==================== RETURN TYPE VALIDATION ====================

    def test_tc15_1_function_returns_dictionary(self):
        """TC15.1: Verify function returns a dictionary."""
        with patch('library_service.get_patron_borrowed_books', return_value=[]), \
             patch('library_service.get_borrowing_history', return_value=[]):
            
            result = get_patron_status_report("123456")
            
            assert isinstance(result, dict)

    def test_tc15_2_status_field_is_string(self):
        """TC15.2: Verify status field is a string."""
        with patch('library_service.get_patron_borrowed_books', return_value=[]), \
             patch('library_service.get_borrowing_history', return_value=[]):
            
            result = get_patron_status_report("123456")
            
            assert isinstance(result['status'], str)
            assert result['status'] in ['success', 'error']

    def test_tc15_3_patron_id_field_is_string(self):
        """TC15.3: Verify patron_id field is a string."""
        with patch('library_service.get_patron_borrowed_books', return_value=[]), \
             patch('library_service.get_borrowing_history', return_value=[]):
            
            result = get_patron_status_report("123456")
            
            assert isinstance(result['patron_id'], str)

    # ==================== BOUNDARY AND EDGE VALUES ====================

    def test_tc16_1_very_large_late_fees(self):
        """TC16.1: Verify handling of very large total late fees (multiple max fees)."""
        due_date = datetime.now() - timedelta(days=100)
        
        with patch('library_service.get_patron_borrowed_books', return_value=[
            {'book_id': i, 'title': f'Book {i}', 'due_date': due_date.isoformat()}
            for i in range(1, 6)
        ]), \
             patch('library_service.calculate_late_fee_for_book', return_value={
                 'status': 'success', 'fee_amount': 15.00, 'days_overdue': 100
             }), \
             patch('library_service.get_borrowing_history', return_value=[]):
            
            result = get_patron_status_report("123456")
            
            assert result['status'] == 'success'
            assert result['total_late_fees'] == 75.00  # 15.00 * 5

    def test_tc16_2_patron_with_zero_late_fees_but_overdue_books(self):
        """TC16.2: Verify patron with overdue books due exactly today shows $0.00 fees."""
        due_date = datetime.now()
        
        with patch('library_service.get_patron_borrowed_books', return_value=[
            {'book_id': 1, 'title': 'Due Today', 'due_date': due_date.isoformat()}
        ]), \
             patch('library_service.calculate_late_fee_for_book', return_value={
                 'status': 'success', 'fee_amount': 0.00, 'days_overdue': 0
             }), \
             patch('library_service.get_borrowing_history', return_value=[]):
            
            result = get_patron_status_report("123456")
            
            assert result['status'] == 'success'
            assert result['total_late_fees'] == 0.00

    def test_tc16_3_empty_borrowing_history_list(self):
        """TC16.3: Verify empty borrowing history returns empty list, not None."""
        with patch('library_service.get_patron_borrowed_books', return_value=[]), \
             patch('library_service.get_borrowing_history', return_value=[]):
            
            result = get_patron_status_report("123456")
            
            assert result['borrowing_history'] == []
            assert result['borrowing_history'] is not None

    # ==================== CONSISTENCY CHECKS ====================

    def test_tc17_1_repeated_calls_return_consistent_results(self):
        """TC17.1: Verify repeated calls with same patron ID return consistent results."""
        due_date = datetime.now() + timedelta(days=7)
        
        with patch('library_service.get_patron_borrowed_books', return_value=[
            {'book_id': 1, 'title': 'Test Book', 'due_date': due_date.isoformat()}
        ]), \
             patch('library_service.calculate_late_fee_for_book', return_value={
                 'status': 'success', 'fee_amount': 0.00, 'days_overdue': 0
             }), \
             patch('library_service.get_borrowing_history', return_value=[]):
            
            result1 = get_patron_status_report("123456")
            result2 = get_patron_status_report("123456")
            
            assert result1 == result2

    def test_tc17_2_different_patrons_return_independent_results(self):
        """TC17.2: Verify different patron IDs return independent results."""
        due_date = datetime.now() + timedelta(days=7)
        
        # Patron 1
        with patch('library_service.get_patron_borrowed_books', return_value=[
            {'book_id': 1, 'title': 'Book 1', 'due_date': due_date.isoformat()}
        ]), \
             patch('library_service.calculate_late_fee_for_book', return_value={
                 'status': 'success', 'fee_amount': 0.00, 'days_overdue': 0
             }), \
             patch('library_service.get_borrowing_history', return_value=[]):
            
            result1 = get_patron_status_report("123456")
        
        # Patron 2
        with patch('library_service.get_patron_borrowed_books', return_value=[
            {'book_id': 2, 'title': 'Book 2', 'due_date': due_date.isoformat()},
            {'book_id': 3, 'title': 'Book 3', 'due_date': due_date.isoformat()}
        ]), \
             patch('library_service.calculate_late_fee_for_book', return_value={
                 'status': 'success', 'fee_amount': 0.00, 'days_overdue': 0
             }), \
             patch('library_service.get_borrowing_history', return_value=[]):
            
            result2 = get_patron_status_report("654321")
        
        assert result1['patron_id'] != result2['patron_id']
        assert result1['num_books_borrowed'] == 1
        assert result2['num_books_borrowed'] == 2

    # ==================== LATE FEE PRECISION ====================

    def test_tc18_1_late_fees_not_negative(self):
        """TC18.1: Verify late fees are never negative."""
        with patch('library_service.get_patron_borrowed_books', return_value=[]), \
             patch('library_service.get_borrowing_history', return_value=[]):
            
            result = get_patron_status_report("123456")
            
            assert result['total_late_fees'] >= 0.00

    def test_tc18_2_late_fees_with_floating_point_precision(self):
        """TC18.2: Verify late fees handle floating point precision correctly."""
        due_date = datetime.now() - timedelta(days=5)
        
        with patch('library_service.get_patron_borrowed_books', return_value=[
            {'book_id': 1, 'title': 'Book 1', 'due_date': due_date.isoformat()},
            {'book_id': 2, 'title': 'Book 2', 'due_date': due_date.isoformat()},
            {'book_id': 3, 'title': 'Book 3', 'due_date': due_date.isoformat()}
        ]), \
             patch('library_service.calculate_late_fee_for_book', side_effect=[
                 {'status': 'success', 'fee_amount': 0.10, 'days_overdue': 1},
                 {'status': 'success', 'fee_amount': 0.20, 'days_overdue': 1},
                 {'status': 'success', 'fee_amount': 0.03, 'days_overdue': 1}
             ]), \
             patch('library_service.get_borrowing_history', return_value=[]):
            
            result = get_patron_status_report("123456")
            
            assert result['status'] == 'success'
            assert result['total_late_fees'] == 0.33