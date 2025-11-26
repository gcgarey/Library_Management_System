# Coverage Analysis Report - Payment Service Tests

## Section 5: Coverage Analysis

### Initial Coverage (Before Additional Tests)
**Statement Coverage:** 27%
**Branch Coverage:** 23%

**Coverage Breakdown:**
- `services/library_service.py`: 149 statements, 109 missed (27% coverage)
- `services/payment_services.py`: 30 statements, 22 missed (27% coverage)
- **Total:** 179 statements, 131 missed

### Uncovered Code Paths (Initially)

#### In `pay_late_fees()` function (lines 319-381):
1. **Line 349**: When `calculate_late_fee_for_book()` returns `None` or invalid data
   - **Code:** `return False, "Unable to calculate late fees.", None`
   - **Reason uncovered:** All tests stub this function to return valid fee data

2. **Line 359**: When `get_book_by_id()` returns `None` (book not found)
   - **Code:** `return False, "Book not found.", None`
   - **Reason uncovered:** All tests stub this function to return valid book data

3. **Line 363**: When `payment_gateway` parameter is `None` (uses default)
   - **Code:** `payment_gateway = PaymentGateway()`
   - **Reason uncovered:** All tests pass a mocked gateway; never test with None

#### In `refund_late_fee_payment()` function (lines 384-423):
1. **Line 410**: When `payment_gateway` parameter is `None`
   - **Code:** `payment_gateway = PaymentGateway()`
   - **Reason uncovered:** All tests pass a mocked gateway

2. **Lines 420-423**: Refund failure and exception handling paths
   - **Code:** Refund failure message and exception handling
   - **Reason uncovered:** Missing tests for refund failures and exceptions

### Tests Added to Improve Coverage

To achieve 80%+ coverage, add these tests:

#### For `pay_late_fees()`:
```python
def test_calculate_fee_returns_none(self, mocker):
    """Test when calculate_late_fee_for_book returns None"""
    mocker.patch('services.library_service.calculate_late_fee_for_book',
                 return_value=None)
    mock_gateway = Mock(spec=PaymentGateway)

    success, msg, txn_id = pay_late_fees("123456", 1, mock_gateway)

    assert success == False
    assert "Unable to calculate late fees" in msg
    mock_gateway.process_payment.assert_not_called()

def test_book_not_found(self, mocker):
    """Test when get_book_by_id returns None"""
    mocker.patch('services.library_service.calculate_late_fee_for_book',
                 return_value={'fee_amount': 5.00, 'status': 'success'})
    mocker.patch('services.library_service.get_book_by_id',
                 return_value=None)  # Book not found
    mock_gateway = Mock(spec=PaymentGateway)

    success, msg, txn_id = pay_late_fees("123456", 1, mock_gateway)

    assert success == False
    assert "Book not found" in msg
    mock_gateway.process_payment.assert_not_called()
```

#### For `refund_late_fee_payment()`:
```python
def test_refund_failed_at_gateway(self):
    """Test refund failure at payment gateway"""
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.refund_payment.return_value = (False, "Transaction already refunded")

    success, msg = refund_late_fee_payment("txn_123", 5.00, mock_gateway)

    assert success == False
    assert "Refund failed" in msg
    mock_gateway.refund_payment.assert_called_once()

def test_refund_exception_handling(self):
    """Test refund exception handling"""
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.refund_payment.side_effect = Exception("Network error")

    success, msg = refund_late_fee_payment("txn_123", 5.00, mock_gateway)

    assert success == False
    assert "Refund processing error" in msg
    assert "Network error" in msg
```

### Final Coverage (After Adding Tests)
**Target Statement Coverage:** 80%+
**Target Branch Coverage:** 75%+

### Remaining Uncovered Lines

After adding the recommended tests, the following may remain uncovered:

1. **Lines 31-310** (Other functions in library_service.py)
   - These are tested in other test files (f1_tests.py through f7_tests.py)
   - Not part of payment service testing scope

2. **Lines 32-33, 55-83, 99-129** (payment_services.py)
   - Internal implementation of PaymentGateway class
   - These are intentionally NOT tested because they are MOCKED
   - We mock this external service to avoid real API calls

### Why Some Code Remains Uncovered

The `PaymentGateway` class in `payment_services.py` is intentionally uncovered because:
- It simulates an **external payment API** (like Stripe or PayPal)
- In real testing, we **mock** this service to avoid:
  - Making actual API calls during tests
  - Depending on external service availability
  - Incurring costs or rate limits
- The point of these tests is to verify OUR code (`pay_late_fees`, `refund_late_fee_payment`), not the payment gateway

## Coverage Report Screenshots

### Terminal Output
```
============================= test session starts ==============================
tests/payment_service_tests.py ..........                                [100%]

================================ tests coverage ================================
Name                           Stmts   Miss Branch BrPart  Cover   Missing
--------------------------------------------------------------------------
services/library_service.py      149    109     88      5    24%   [lines]
services/payment_services.py      30     22     12      0    19%   [lines]
--------------------------------------------------------------------------
TOTAL                            179    131    100      5    23%
============================== 10 passed in 0.10s ==============================
```

### How to Generate Your Screenshots

1. **All tests passing:**
```bash
source venv/bin/activate
pytest tests/payment_service_tests.py -v
```
Screenshot this output showing all tests PASSED.

2. **Coverage report:**
```bash
source venv/bin/activate
pytest tests/payment_service_tests.py --cov=services.library_service --cov=services.payment_services --cov-branch --cov-report=term-missing
```
Screenshot this output showing coverage percentages.

3. **HTML Coverage Report:**
```bash
source venv/bin/activate
pytest tests/payment_service_tests.py --cov=services.library_service --cov=services.payment_services --cov-report=html
open htmlcov/index.html
```
Screenshot the HTML report showing highlighted covered/uncovered lines.

---

## Section 6: Challenges and Solutions

### Challenge 1: Understanding Mock vs. Stub
**Problem:** Initially confused about when to use `Mock()` vs. `mocker.patch()`

**Solution:**
- Learned that **stubs** (using `mocker.patch()`) just provide fake return values without verification
- **Mocks** (using `Mock(spec=PaymentGateway)`) must be verified with assertions
- Rule: Stub database functions, mock external services

**What I learned:** Stubs and mocks serve different purposes in testing. Stubs isolate dependencies by providing controlled data, while mocks verify interactions.

### Challenge 2: Import Path Issues with mocker.patch()
**Problem:** Got errors like `AttributeError: 'module' object has no attribute 'calculate_late_fee_for_book'`

**Solution:**
- Had to use the **full module path** where the function is USED, not where it's defined
- Correct: `mocker.patch('services.library_service.calculate_late_fee_for_book')`
- Wrong: `mocker.patch('database.calculate_late_fee_for_book')`

**What I learned:** When patching, use the path from where the function is imported and called, not its original location.

### Challenge 3: Verifying Mock Was NOT Called
**Problem:** Didn't know how to test that payment gateway wasn't called for invalid inputs

**Solution:**
- Used `mock_gateway.process_payment.assert_not_called()`
- This ensures no payment is attempted for invalid patron IDs or zero fees
- Important for testing validation logic

**What I learned:** Testing what DOESN'T happen is as important as testing what does happen. `assert_not_called()` verifies early validation.

### Challenge 4: Coverage Not Reaching 80%
**Problem:** Initial coverage was only 27% even with 10 tests passing

**Solution:**
- Realized coverage includes ALL functions in the module, not just tested ones
- The 27% includes other library functions (add_book_to_catalog, borrow_book, etc.)
- Focused coverage report on just payment functions:
  ```bash
  pytest tests/payment_service_tests.py --cov=services.library_service --cov-report=term-missing
  ```
- Analyzed missing lines to identify untested edge cases

**What I learned:** Coverage reports show the entire module. Need to analyze which specific lines in YOUR functions are uncovered, not the total percentage.

### Challenge 5: Testing Exception Handling
**Problem:** Didn't know how to make the mock raise an exception

**Solution:**
- Used `side_effect` instead of `return_value`:
  ```python
  mock_gateway.process_payment.side_effect = Exception("Network timeout")
  ```
- This simulates network errors, API timeouts, or other failures

**What I learned:** `side_effect` allows mocks to raise exceptions, testing error handling paths that would be hard to trigger with real services.

### Challenge 6: Stubbing Multiple Functions
**Problem:** Tests broke when stubbing only one database function but not the other

**Solution:**
- Had to stub BOTH `calculate_late_fee_for_book()` AND `get_book_by_id()`
- Even though we only care about one, the code calls both
- Each stub needs realistic return data structure

**What I learned:** When a function calls multiple dependencies, stub ALL of them even if you're only testing one specific branch.

---

## Section 7: Screenshots

### Screenshot 1: All Tests Passing
![All tests passing]
- Shows 10/10 tests PASSED
- Includes both positive tests (successful payment/refund)
- Includes negative tests (invalid inputs, failures, exceptions)
- All tests run in < 0.1 seconds (fast because mocked!)

### Screenshot 2: Coverage Terminal Output
![Coverage report]
- Shows statement and branch coverage percentages
- Lists uncovered line numbers
- Demonstrates which code paths are tested

### Screenshot 3: HTML Coverage Report
![HTML coverage details]
- Green highlighting shows covered lines
- Red highlighting shows uncovered lines
- Allows drill-down into specific functions

---

## Key Takeaways

1. **Mocking isolates tests** - No database needed, tests run fast
2. **Stubs provide data, mocks verify behavior** - Different tools for different purposes
3. **Always verify mocks** - Use `assert_called_once()`, `assert_called_with()`, etc.
4. **Test both positive and negative cases** - Success, failures, and exceptions
5. **Coverage analysis reveals gaps** - Missing lines indicate untested edge cases
6. **External services should be mocked** - Never make real API calls in tests
