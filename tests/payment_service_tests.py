import pytest
from unittest.mock import Mock, MagicMock
from services.payment_services import PaymentGateway
from services.library_service import pay_late_fees, refund_late_fee_payment

class TestPayLateFees:
    
    # stub calculate_late_fee_for_book to return fake fee data
    def test_successful_payment(self, mocker):
        mock_fee_info = {
            'fee_amount' : 2.50,
            'days_overdue': 5,
            'status': 'success',
            'message': 'Late fee calculated'
        }
        mocker.patch('services.library_service.calculate_late_fee_for_book', 
                     return_value=mock_fee_info)
        
        # stub get_book_by_id to return fake data for book
        mock_book_info = {
            'id': 1,
            'title': 'test book',
            'author': 'test author',
            'isbn': 1234567890123,
            'total_copies': 1,
            'available_copies': 1
        }
        mocker.patch('services.library_service.get_book_by_id',
                     return_value=mock_book_info)
        
        # mock the paymentGateway
        mock_gateway = Mock(spec=PaymentGateway)
        mock_gateway.process_payment.return_value = (True, 'txn_123', 'Payment successful')

        success, msg, txn_id = pay_late_fees('123456', 1, mock_gateway)

        assert success == True
        assert "Payment successful" in msg
        assert txn_id == 'txn_123'

        # verify the mock was called correctly
        mock_gateway.process_payment.assert_called_once()
        mock_gateway.process_payment.assert_called_with(
            patron_id='123456',
            amount=2.50,
            description="Late fees for 'test book'"
        )

    def test_payment_declined_by_gateway(self, mocker):
        ''' Test payment declined at gateway'''
        # stub database funtions with false data
        mocker.patch('services.library_service.calculate_late_fee_for_book', 
                     return_value={'fee_amount': 1.00, 'days_overdue': 2, 'status': 'success'})
        mocker.patch('services.library_service.get_book_by_id',
                     return_value={'id': 1, 'title': 'Test Book'})
        
        # Mock gateway to return Failure
        mock_gateway = Mock(spec=PaymentGateway)
        mock_gateway.process_payment.return_value = (False, None, "Card Declined")

        # call function
        success, msg, txn_id = pay_late_fees('123456', 1, mock_gateway)

        assert success == False
        assert "Card Declined" in msg
        assert txn_id == None

        mock_gateway.process_payment.assert_called_once()

    def test_invalid_patron_id(self):
        '''Test invalid patron id (mocker shoud not be called)'''
        mock_gateway = Mock(spec=PaymentGateway)

        success, msg, txn_id = pay_late_fees('12345', 1, mock_gateway)

        assert success == False
        assert "Invalid patron ID" in msg
        assert txn_id is None

        mock_gateway.process_payment.assert_not_called()


    def test_zero_late_fees(self, mocker):
        ''' Test zero late fees (mocker should not be called) '''
        mocker.patch('services.library_service.calculate_late_fee_for_book',
                     return_value={'fee_amount': 0.00, 'days_overdue': 0, 'status': 'success'})
        mock_gateway = Mock(spec=PaymentGateway)

        success, msg, txn_id = pay_late_fees('123456', -1, mock_gateway)

        assert success == False
        assert 'No late fees to pay' in msg
        assert txn_id is None

        mock_gateway.process_payment.assert_not_called()

    def test_network_error_handeling(self, mocker):
        mocker.patch('services.library_service.calculate_late_fee_for_book',
                     return_value={'fee_amount': 5.00, 'status': 'success'})
        mocker.patch('services.library_service.get_book_by_id', 
                     return_value={'id': 1, 'title': 'Test Book'})
        
        mock_gateway = Mock(spec=PaymentGateway)
        mock_gateway.process_payment.side_effect = Exception("Network timeout")

        success, msg, txn_id = pay_late_fees('123456', 1, mock_gateway)

        assert success == False
        assert "Network timeout" in msg
        assert txn_id is None

class TestRefundLateFeePayment:

    def test_successful_refund(self):
        ''' tests refund_late_fee_payment for a successful refund '''

        mock_gateway = Mock(spec=PaymentGateway)
        mock_gateway.refund_payment.return_value = True, "Refund Successful"

        success, msg = refund_late_fee_payment('txn_123', 2.00, mock_gateway)

        assert success == True
        assert "Refund Successful" in msg

        mock_gateway.refund_payment.assert_called_once_with("txn_123", 2.00)

    def test_invalid_id_rejection(self):
        ''' Test that an invalid return id is rejected '''
        mock_gateway = Mock(spec=PaymentGateway)

        success, msg= refund_late_fee_payment('1234', 5.00)

        assert success == False
        assert "Invalid transaction ID." in msg
        

        mock_gateway.process_payment.assert_not_called()


    def test_invalid_refund_amounts_negative(self):
        ''' Test that an invalid refund amount that is negative is rejected '''
        mock_gateway = Mock(spec=PaymentGateway)

        success, msg= refund_late_fee_payment('txn_123', -5.00)

        assert success == False
        assert "Refund amount must be greater than 0." in msg
        

        mock_gateway.process_payment.assert_not_called()

    def test_invalid_refund_amounts_zero(self):
        ''' Test that an invalid refund amount that is zero is rejected '''
        mock_gateway = Mock(spec=PaymentGateway)

        success, msg= refund_late_fee_payment('txn_123', 0.00)

        assert success == False
        assert "Refund amount must be greater than 0." in msg
        

        mock_gateway.process_payment.assert_not_called()

    def test_invalid_refund_amounts_exceeds_15(self):
        ''' Test that an invalid refund amount that is over 15 is rejected '''
        mock_gateway = Mock(spec=PaymentGateway)

        success, msg= refund_late_fee_payment('txn_123', 16.00)

        assert success == False
        assert "Refund amount exceeds maximum late fee." in msg
        

        mock_gateway.process_payment.assert_not_called()



