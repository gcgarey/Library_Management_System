import re
from playwright.sync_api import Page, expect
import pytest
import os
from database import get_db_connection, init_database, DATABASE
import database


@pytest.fixture(scope="module", autouse=True)
def setup_test_database():
    """Set up test database before all e2e tests run"""
    # Set environment variable for test database
    os.environ['DATABASE_NAME'] = 'test_library_e2e.db'

    # Reload database module to pick up new environment variable
    import importlib
    importlib.reload(database)

    # Initialize the test database
    init_database()

    yield  # Tests run here

    # Teardown: Clean up test database after all tests
    if os.path.exists("test_library_e2e.db"):
        os.remove("test_library_e2e.db")

    # Clean up environment variable
    if 'DATABASE_NAME' in os.environ:
        del os.environ['DATABASE_NAME']


@pytest.fixture(autouse=True)
def cleanup_database():
    """Clean database before each test"""
    conn = get_db_connection()
    conn.execute('DELETE FROM borrow_records')
    conn.execute('DELETE FROM books')
    conn.execute('DELETE FROM sqlite_sequence WHERE name="books"')
    conn.execute('DELETE FROM sqlite_sequence WHERE name="borrow_records"')
    conn.commit()
    conn.close()

    yield  # Test runs here



def test_add_new_book_to_catalog_then_borrow(page: Page):
    page.goto('http://127.0.0.1:5000/catalog')

    expect(page).to_have_title(re.compile("Library Management System"))
    # get the locator: add new book
    page.get_by_role("link", name="Add New Book").click()

    expect(page).to_have_url(re.compile(".*add_book"))

    # Fill in the text boxes for the book
    page.locator("#title").fill("Crime and Punishment")
    page.locator("#author").fill("Fyodor Dostoyevsky")
    page.locator("#isbn").fill("1234567890123")
    page.locator("#total_copies").fill("1")

    # click add book to catalog
    page.get_by_role("button", name="Add Book to Catalog").click()

    # Wait for navigation back to catalog
    expect(page).to_have_url(re.compile(".*catalog"))

    # Verify book appears in catalog
    expect(page.get_by_role("cell", name="Crime and Punishment")).to_be_visible()

    # Fill in patron ID to borrow the book
    page.locator("[name='patron_id']").fill("123456")

    # click borrow to borrow the book
    page.get_by_role("button", name="Borrow").click()

    # verify successful message is displayed
    expect(page.locator(".flash-success")).to_be_visible()

def test_add_new_book_search_for_it_and_borrow(page: Page):
    page.goto('http://127.0.0.1:5000/catalog')

    expect(page).to_have_title(re.compile("Library Management System"))
    # get the locator: add new book
    page.get_by_role("link", name="Add New Book").click()

    expect(page).to_have_url(re.compile(".*add_book"))

    # Fill in the text boxes for the book
    page.locator("#title").fill("Great Expectations")
    page.locator("#author").fill("Charles Dickens")
    page.locator("#isbn").fill("1234567890124")
    page.locator("#total_copies").fill("1")

    # click add book to catalog
    page.get_by_role("button", name="Add Book to Catalog").click()

    # Wait for navigation back to catalog
    expect(page).to_have_url(re.compile(".*catalog"))

    # Verify book appears in catalog
    expect(page.get_by_role("cell", name="Great Expectations")).to_be_visible()

    # navigate to search page
    page.get_by_role("link", name="Search").click()

    # fill in the search boxes
    page.locator("#q").fill("Great")
    page.locator("#type").select_option("title")

    # click button to search
    page.get_by_role("button", name="Search").click()

    # verify the book shows up
    expect(page.get_by_role("cell", name="Great Expectations")).to_be_visible()

    # enter a patron_id and borrow the book
    page.locator("[name='patron_id']").fill("123456")
    page.get_by_role("button", name="Borrow").click()

    # check the success message is displayed and the book is now unavailable
    expect(page.locator(".flash-success")).to_be_visible()
    expect(page.locator(".status-unavailable")).to_have_text("Not Available")







