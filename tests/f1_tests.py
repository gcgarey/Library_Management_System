# PYTHONPATH=. pytest tests/f1_test.py

import pytest
#import sys
#import os
#sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from library_service import (
    add_book_to_catalog
)
'''
def test_add_book_valid_input():
    """Test adding a book with valid input."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "1234567890128", 5)
    
    assert success == True
    assert "successfully added" in message.lower()
'''

def test_add_book_to_catalog_no_title():
    """Test adding a book with no title"""
    success, message = add_book_to_catalog("", "Test Author", 1234567890123, 1)

    assert success == False
    assert "title is required." in message.lower()

def test_add_book_to_catalog_long_title():
    """Test adding a book with a title longer than 200 characters"""
    long_title = "A" * 201
    success, message = add_book_to_catalog(long_title, "Test Author", 1234567890123, 1)

    assert success == False
    assert "title must be less than 200 characters." in message.lower()

def test_add_book_to_catalog_no_author():
    """Test adding a book with no author"""
    success, message = add_book_to_catalog("Test Book", "", 1234567890123, 1)

    assert success == False
    assert "author is required." in message.lower()

def test_add_book_to_catalog_long_author():
    """Test adding a book with an author name longer than 100 characters"""
    long_author = "A" * 101
    success, message = add_book_to_catalog("Test Book", long_author, 1234567890123, 1)

    assert success == False
    assert "author must be less than 100 characters." in message.lower()

def test_add_book_to_catalog_invalid_isbn_length():
    """Test adding a book with an ISBN that is not 13 digits long"""
    success, message = add_book_to_catalog("Test Book", "Test Author", "123456", 1)

    assert success == False
    assert "isbn must be exactly 13 digits." in message.lower()

def test_add_book_to_catalog_negative_copies():
    """Test adding a book with negative total copies"""
    success, message = add_book_to_catalog("Test Book", "Test Author", 1234567890123, -5)

    assert success == False
    assert "total copies must be a positive integer." in message.lower()

def test_add_book_to_catalog_zero_copies():
    """Test adding a book with zero total copies"""
    success, message = add_book_to_catalog("Test Book", "Test Author", 1234567890123, 0)

    assert success == False
    assert "total copies must be a positive integer." in message.lower()