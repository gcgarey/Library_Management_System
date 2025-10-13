# CISC 327 Assignment 1
### Gabrielle Garey
### 20414286

#### Progress spreadsheet:

| Requirement | R1: Add Book | R2: View Catalog | R3: Borrow Book | R4: Return Book | R5: Late Fees API | R6: Search Books | R7: Patron Status |
|-------------|--------------|------------------|-----------------|-----------------|-------------------|------------------|-------------------|
| **Overall Status** | Partial | ✅ PASS | ✅ PASS | ❌ FAIL | ❌ FAIL | ❌ FAIL | ❌ FAIL |
| **Test 1** | ✅ Title is required and limitations implemented | ✅ Catalog displays Book ID, Title, Author, ISBN | ✅ Accepts patron ID and book ID as form parameters | ❌ Does not accept patron ID and book ID as form parameters | ❌ Does not provide API endpoint for late fee calculation | ❌ Does not provide search functionality with 'q' search term | ❌ Does not display currently borrowed books with due dates |
| **Test 2** | ✅ Author is required and limitations implemented | ✅ Catalog displays available/total copies | ✅ Validates patron ID | ❌ Does not verify book was borrowed by patron | ❌ Does not return JSON response with fee amount and days overdue | ❌ Does not provide search functionality with 'type' matching | ❌ Does not display total late fees owed |
| **Test 3** | ❌ ISBN is required, but allows for letters to be included | ✅ Borrow button displayed and functional | ✅ Checks book availability and patron borrowing limits | ❌ Does not update available copies and record return date | | ❌ Does not provide partial matching for title/author | ❌ Does not display number of books currently borrowed |
| **Test 4** | ✅ Total copies is required and limitations implemented | | ✅ Creates borrowing record and updates available copies | ❌ Does not calculate and display late fees owed | | ❌ Does not provide exact matching for ISBN number | ❌ Does not display borrowing history |
| **Test 5** | ✅ Displays success/error messages and redirects to catalog view | | ✅ Displays success/error message | | | ❌ Does not return results in same format as catalog display | |


#### Unit test Summaries: 

F1
1. `test_add_book_valid_input`: tests that a book with valid input can be added to the catalog. expected output is True. 
2. `test_add_book_to_catalog_no_title`: tests that a book can be added to the catalog with non valid input. Expected output is False
3. `test_add_book_to_catalog_long_title`: tests that a book can be added to the catalog with a title longer than 200 characters. Expected output is False
4. `test_add_book_to_catalog_no_author`: tests that a book can be added to the catalog with no author included. Expected output is False
5. `test_add_book_to_catalog_short_isbn_length`: tests that a book can be added to catalog with a isbn shorter than 13 digits. 

F2. 
1. `test_catalog_display_returns_all_books`: tests that the catalog can retrieve all books. The test add's two books to a temporary database, then checks that the length of the output is 2 and the correct titles are in the correct entries. Expected output is True
2. `test_catalog_display_shows_correct_format`: tests that the catalog returns books with the correct display format (ID, title, author, isbn). Expected output is True
3. `test_catalog_display_shows_available_total_copies`: tests that the catalog shows the available copies / total copies. Expected output is True
4. `test_catalog_display_borrow_action_unavailable_books`: Tests that books with no available copies don't show a borrow action. Adds a book to temportary database then assert that available_copies is 0
5. `test_catalog_display_empty_catalog`: tests catalog display with zero books in it. Test initializes an empty database, then asserts the length of get_all_books() is 0.

F3
1. `test_borrowing_interface_valid_patron_id_and_available_book`: test that borrowing a books is successful when parameters are valid and the book is available. Test adds a book to catalog, uses borrow_book_by_patron, then checks that the available copies has decreased by 1.
2. `test_patron_id_validation_exactly_6_digits`: Test that the patron ID is exactly six digits. Inserts a book to temporary database then checks a valid id can borrow an available book. Expected output is True
3. `test_patron_id_validation_rejects_non_digits`: Tests that a patron ID is rejected if it is not made up of non-digit characters. Expected result is False
4. `test_patron_id_validation_rejects_too_short` Tests that patron ID is rejected if it is less than 6 characters Expected result is False. 
5. `test_book_availability_check_available_book`: Tests that borrowing a book is successful when the book has available copies to borrow. Expected result is True
6. `test_borrowing_record_creation`: Test that borrowing creates the proper borrow record. Test borrows a book in the test database and then checks that get_patron_borrow_count increased by 1. 

F4
1. `test_with_incorrect_parameters_for_return_book_functionality`: Test that the return a book function with does not return a book if it has incorrect number of parameters. Test adds a book and a borrow record then calls the return_book_by_patron function with an added parameter for date returned. Expected result is false 
2. `test_patron_returns_book_after_borrowing`: Tests that a parton borrowed the book before returning. Test adds a book to a temporary database and creates a borrow record. Test then returns that book at a later date. Expected result is True. 
3. `test_patron_returns_book_not_borrowed`: Tests that patron tries to return a book that they didn't borrow. Expected result is False
4. `test_copies_updated_after_return`: Tests that available copies are updated correctly after a return. Test creates a book and borrow record in test database. Then checks that available copies increased after book is returned. 
5. `test_late_fees_calculated`: Test that late fees are calculated for overdue returns. Creates a book in test database with an overdue borrow record. Then check that late fee is calculated correctly for the overdue days. 

F5
1. `test_late_fee_no_fee_if_returned_on_time`: test that no late fee is applied if the book is returned on time or before the due date. Expected fee is 0 dollars.
2. `test_late_fee_calculation_one_day_late`: test late fee calculation for one day late return. Test inserts a book to the database then checks that the return fee is 50 cents for being one day late. 
3. `test_late_fee_calculation_under_seven_days_late`: Test the late fee calculation for multiple day late returns. Test adds a book to the database and calculates the fees when that book is returned 5 days late. Expected result is 2.50
4. `test_late_fee_calculation_over_seven_days_late`: Test that late fee is correctly calculated for returns over 7 days. Expected fee is 4.50 
5. `test_late_fee_capped_at_fifteen_dollars`: tests that the fee is capped at 15 dollars for a late return date. Expected fee is 15 dollars. 

F6
1. `test_has_parameter_q_and_type`: tests that the search_books_in_catalog functionality accepts the correct parameters q and type. Expected result is True
2. `test_partial_matching_for_title_search`: Tests partial matching for title search. Adds two books with similar titles to the test database and checks that search_books_in_catalog includes both books. 
3. `test_exact_matching_for_isbn_search_compete`: Test that the ISBN search matches exactly. Adds books to catalog and then searches using the exact isbn number. Checks that correct books is in result.
4. `test_isbn_exact_matching_search_partial`: Tests that partial matching for ISBN search returns no results. Inserts 2 books to the test database and uses the first 10 digits of the isbn to search. Checks that result is empty
5. `test_result_in_same_format_as_catalog_display`: Tests that the search results are in the same format as catalog display. Result should be True

F7
1. `test_status_report_with_no_borrowed_books`: Tests the status report functionality with no borrowed books. Checks that currently borrowed due dates, late fees and books borrowed are 0.
2. `test_status_report_with_currently_borrowed_books`: Test status report showing currently borrowed books with due dates. Checks that books that have been borrowed by the same patron id are in the result.
3. `test_status_report_calculates_total_late_fees`: Test status report calculates total late fees owed across all books. Expected result is 30 for 2 very overdue books.
4. `test_displays_number_of_books_currently_borrowed`:  Test status report displays the correct number of books currently borrowed. Test creates db enteies and borrow records for two books with the same patron id. Then checks that the patron id's report contains 2 books borrowed. 




