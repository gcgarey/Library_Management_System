import pytest
import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.library_service import calculate_late_fee_for_book
from database import init_database, get_db_connection, insert_book, insert_borrow_record

class TestR5Requirements:
    """Test cases for R5: Late Fee Calculation"""

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

    def test_late_fee_no_fee_if_returned_on_time(self):
        """Test no late fee if book is returned on or before due date"""
        insert_book("Test Book", "Test Author", "1234567890123", 3, 3)

        borrow_date = datetime.now()
        due_date = datetime.now() + timedelta(days=7)
        insert_borrow_record("123456", 1, borrow_date, due_date)

        result = calculate_late_fee_for_book("123456", 1)
        assert result['fee_amount'] == 0.0

    def test_late_fee_calculation_one_day_late(self):
        """Test late fee calculation for one day late return"""
        insert_book("Test Book", "Test Author", "1234567890123", 3, 3)

        borrow_date = datetime.now() - timedelta(days=15)
        due_date = datetime.now() - timedelta(days=1)
        insert_borrow_record("123456", 1, borrow_date, due_date)

        result = calculate_late_fee_for_book("123456", 1)
        assert result['fee_amount'] == 0.50

    def test_late_fee_calculation_under_seven_days_late(self):
        """Test late fee calculation for multiple days late return"""
        insert_book("Test Book", "Test Author", "1234567890123", 3, 3)

        borrow_date = datetime.now() - timedelta(days=19)
        due_date = datetime.now() - timedelta(days=5)
        insert_borrow_record("123456", 1, borrow_date, due_date)

        result = calculate_late_fee_for_book("123456", 1)
        assert result['fee_amount'] == 2.50  # 5 days late at $0.50/day

    def test_late_fee_calculation_over_seven_days_late(self):
        """Test that late fee is correctly calculated for returns over 7 days"""
        insert_book("Test Book", "Test Author", "1234567890123", 3, 3)

        borrow_date = datetime.now() - timedelta(days=22)
        due_date = datetime.now() - timedelta(days=8)
        insert_borrow_record("123456", 1, borrow_date, due_date)

        result = calculate_late_fee_for_book("123456", 1)
        assert result['fee_amount'] == 4.50  # 7 days at $0.50 + 1 day at $1.00

    def test_late_fee_capped_at_fifteen_dollars(self):
        """Test that late fee is capped at $15.00"""
        insert_book("Test Book", "Test Author", "1234567890123", 3, 3)

        borrow_date = datetime.now() - timedelta(days=54)
        due_date = datetime.now() - timedelta(days=40)  # 40 days late
        insert_borrow_record("123456", 1, borrow_date, due_date)

        result = calculate_late_fee_for_book("123456", 1)
        assert result['fee_amount'] == 15.00  # Capped at $15.00