"""
Tests for new domain operations: create, transfer, renew, delete, update

Tests for cmd_domain_create, cmd_domain_transfer, cmd_domain_renew,
cmd_domain_delete, and cmd_domain_update commands.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock

from wapi.commands.domain import (
    cmd_domain_create,
    cmd_domain_transfer,
    cmd_domain_renew,
    cmd_domain_delete,
    cmd_domain_update,
)
from wapi.constants import EXIT_SUCCESS, EXIT_ERROR
from wapi.exceptions import (
    WAPIValidationError,
    WAPIRequestError,
    WAPITimeoutError,
)


class TestDomainCreate(unittest.TestCase):
    """Test cmd_domain_create command"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_client = Mock()
        self.mock_args = Mock()
        self.mock_args.domain = "example.com"
        self.mock_args.format = "table"
        self.mock_args.wait = False
        self.mock_args.period = 1
        self.mock_args.owner_c = None
        self.mock_args.admin_c = None
        self.mock_args.nsset = None
        self.mock_args.keyset = None
        self.mock_args.auth_info = None
        self.mock_args.quiet = False

    @patch('wapi.commands.domain.validate_domain')
    @patch('wapi.commands.domain.get_logger')
    def test_domain_create_success(self, mock_get_logger, mock_validate):
        """Test successful domain creation"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        mock_response = {
            'response': {
                'code': '1000',
                'result': 'OK',
                'data': {'domain': {'name': 'example.com'}}
            }
        }
        self.mock_client.domain_create.return_value = mock_response
        
        result = cmd_domain_create(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)
        self.mock_client.domain_create.assert_called_once_with(
            "example.com",
            period=1,
            owner_c=None,
            admin_c=None,
            nsset=None,
            keyset=None,
            auth_info=None
        )

    @patch('wapi.commands.domain.validate_domain')
    @patch('wapi.commands.domain.get_logger')
    def test_domain_create_with_all_params(self, mock_get_logger, mock_validate):
        """Test domain creation with all parameters"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.period = 2
        self.mock_args.owner_c = "OWNER-C"
        self.mock_args.admin_c = "ADMIN-C"
        self.mock_args.nsset = "NSSET-EXAMPLE"
        self.mock_args.keyset = "KEYSET-EXAMPLE"
        self.mock_args.auth_info = "AUTH123"
        
        mock_response = {
            'response': {
                'code': '1000',
                'result': 'OK'
            }
        }
        self.mock_client.domain_create.return_value = mock_response
        
        result = cmd_domain_create(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)
        self.mock_client.domain_create.assert_called_once_with(
            "example.com",
            period=2,
            owner_c="OWNER-C",
            admin_c="ADMIN-C",
            nsset="NSSET-EXAMPLE",
            keyset="KEYSET-EXAMPLE",
            auth_info="AUTH123"
        )

    @patch('wapi.commands.domain.validate_domain')
    @patch('wapi.commands.domain.get_logger')
    def test_domain_create_invalid_domain(self, mock_get_logger, mock_validate):
        """Test domain creation with invalid domain"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (False, "Invalid domain format")
        
        with self.assertRaises(WAPIValidationError):
            cmd_domain_create(self.mock_args, self.mock_client)

    @patch('wapi.commands.domain.validate_domain')
    @patch('wapi.commands.domain.get_logger')
    def test_domain_create_async_with_wait(self, mock_get_logger, mock_validate):
        """Test domain creation with async response and wait"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        self.mock_args.wait = True
        
        # First call returns async (1001), polling returns success (1000)
        async_response = {
            'response': {
                'code': '1001',
                'result': 'Processing'
            }
        }
        success_response = {
            'response': {
                'code': '1000',
                'result': 'OK',
                'data': {'domain': {'name': 'example.com'}}
            }
        }
        self.mock_client.domain_create.return_value = async_response
        self.mock_client.poll_until_complete.return_value = success_response
        
        result = cmd_domain_create(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)
        self.mock_client.poll_until_complete.assert_called_once()

    @patch('wapi.commands.domain.validate_domain')
    @patch('wapi.commands.domain.get_logger')
    def test_domain_create_error(self, mock_get_logger, mock_validate):
        """Test domain creation with error response"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        error_response = {
            'response': {
                'code': '2001',
                'result': 'Domain already exists'
            }
        }
        self.mock_client.domain_create.return_value = error_response
        
        with self.assertRaises(WAPIRequestError):
            cmd_domain_create(self.mock_args, self.mock_client)


class TestDomainTransfer(unittest.TestCase):
    """Test cmd_domain_transfer command"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_client = Mock()
        self.mock_args = Mock()
        self.mock_args.domain = "example.com"
        self.mock_args.format = "table"
        self.mock_args.auth_info = "AUTH123"
        self.mock_args.period = 1

    @patch('wapi.commands.domain.validate_domain')
    @patch('wapi.commands.domain.get_logger')
    def test_domain_transfer_success(self, mock_get_logger, mock_validate):
        """Test successful domain transfer"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        mock_response = {
            'response': {
                'code': '1000',
                'result': 'OK'
            }
        }
        self.mock_client.domain_transfer.return_value = mock_response
        
        result = cmd_domain_transfer(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)
        self.mock_client.domain_transfer.assert_called_once_with(
            "example.com",
            "AUTH123",
            period=1
        )

    @patch('wapi.commands.domain.validate_domain')
    @patch('wapi.commands.domain.get_logger')
    def test_domain_transfer_missing_auth_info(self, mock_get_logger, mock_validate):
        """Test domain transfer without auth_info"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        self.mock_args.auth_info = None
        
        with self.assertRaises(WAPIValidationError):
            cmd_domain_transfer(self.mock_args, self.mock_client)

    @patch('wapi.commands.domain.validate_domain')
    @patch('wapi.commands.domain.get_logger')
    def test_domain_transfer_invalid_domain(self, mock_get_logger, mock_validate):
        """Test domain transfer with invalid domain"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (False, "Invalid domain format")
        
        with self.assertRaises(WAPIValidationError):
            cmd_domain_transfer(self.mock_args, self.mock_client)

    @patch('wapi.commands.domain.validate_domain')
    @patch('wapi.commands.domain.get_logger')
    def test_domain_transfer_async(self, mock_get_logger, mock_validate):
        """Test domain transfer with async response"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        async_response = {
            'response': {
                'code': '1001',
                'result': 'Transfer initiated'
            }
        }
        self.mock_client.domain_transfer.return_value = async_response
        
        result = cmd_domain_transfer(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)

    @patch('wapi.commands.domain.validate_domain')
    @patch('wapi.commands.domain.get_logger')
    def test_domain_transfer_error(self, mock_get_logger, mock_validate):
        """Test domain transfer with error response"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        error_response = {
            'response': {
                'code': '2001',
                'result': 'Transfer failed'
            }
        }
        self.mock_client.domain_transfer.return_value = error_response
        
        with self.assertRaises(WAPIRequestError):
            cmd_domain_transfer(self.mock_args, self.mock_client)


class TestDomainRenew(unittest.TestCase):
    """Test cmd_domain_renew command"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_client = Mock()
        self.mock_args = Mock()
        self.mock_args.domain = "example.com"
        self.mock_args.format = "table"
        self.mock_args.period = 1
        self.mock_args.wait = False
        self.mock_args.quiet = False

    @patch('wapi.commands.domain.validate_domain')
    @patch('wapi.commands.domain.get_logger')
    def test_domain_renew_success(self, mock_get_logger, mock_validate):
        """Test successful domain renewal"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        mock_response = {
            'response': {
                'code': '1000',
                'result': 'OK'
            }
        }
        self.mock_client.domain_renew.return_value = mock_response
        
        result = cmd_domain_renew(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)
        self.mock_client.domain_renew.assert_called_once_with("example.com", period=1)

    @patch('wapi.commands.domain.validate_domain')
    @patch('wapi.commands.domain.get_logger')
    def test_domain_renew_with_period(self, mock_get_logger, mock_validate):
        """Test domain renewal with custom period"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        self.mock_args.period = 2
        
        mock_response = {
            'response': {
                'code': '1000',
                'result': 'OK'
            }
        }
        self.mock_client.domain_renew.return_value = mock_response
        
        result = cmd_domain_renew(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)
        self.mock_client.domain_renew.assert_called_once_with("example.com", period=2)

    @patch('wapi.commands.domain.validate_domain')
    @patch('wapi.commands.domain.get_logger')
    def test_domain_renew_invalid_domain(self, mock_get_logger, mock_validate):
        """Test domain renewal with invalid domain"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (False, "Invalid domain format")
        
        with self.assertRaises(WAPIValidationError):
            cmd_domain_renew(self.mock_args, self.mock_client)

    @patch('wapi.commands.domain.validate_domain')
    @patch('wapi.commands.domain.get_logger')
    def test_domain_renew_async_with_wait(self, mock_get_logger, mock_validate):
        """Test domain renewal with async response and wait"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        self.mock_args.wait = True
        
        async_response = {
            'response': {
                'code': '1001',
                'result': 'Processing'
            }
        }
        success_response = {
            'response': {
                'code': '1000',
                'result': 'OK',
                'data': {'domain': {'name': 'example.com'}}
            }
        }
        self.mock_client.domain_renew.return_value = async_response
        self.mock_client.poll_until_complete.return_value = success_response
        
        result = cmd_domain_renew(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)
        self.mock_client.poll_until_complete.assert_called_once()

    @patch('wapi.commands.domain.validate_domain')
    @patch('wapi.commands.domain.get_logger')
    def test_domain_renew_error(self, mock_get_logger, mock_validate):
        """Test domain renewal with error response"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        error_response = {
            'response': {
                'code': '2001',
                'result': 'Renewal failed'
            }
        }
        self.mock_client.domain_renew.return_value = error_response
        
        with self.assertRaises(WAPIRequestError):
            cmd_domain_renew(self.mock_args, self.mock_client)


class TestDomainDelete(unittest.TestCase):
    """Test cmd_domain_delete command"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_client = Mock()
        self.mock_args = Mock()
        self.mock_args.domain = "example.com"
        self.mock_args.format = "table"
        self.mock_args.force = False
        self.mock_args.delete_after = None

    @patch('wapi.commands.domain.validate_domain')
    @patch('wapi.commands.domain.get_logger')
    def test_domain_delete_without_force(self, mock_get_logger, mock_validate):
        """Test domain deletion without --force flag"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        with self.assertRaises(WAPIValidationError) as context:
            cmd_domain_delete(self.mock_args, self.mock_client)
        
        self.assertIn("force", str(context.exception).lower())

    @patch('wapi.commands.domain.validate_domain')
    @patch('wapi.commands.domain.get_logger')
    def test_domain_delete_success(self, mock_get_logger, mock_validate):
        """Test successful domain deletion"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        self.mock_args.force = True
        
        mock_response = {
            'response': {
                'code': '1000',
                'result': 'OK'
            }
        }
        self.mock_client.domain_delete.return_value = mock_response
        
        result = cmd_domain_delete(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)
        self.mock_client.domain_delete.assert_called_once_with("example.com", delete_after=None)

    @patch('wapi.commands.domain.validate_domain')
    @patch('wapi.commands.domain.get_logger')
    def test_domain_delete_with_date(self, mock_get_logger, mock_validate):
        """Test domain deletion with delete_after date"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        self.mock_args.force = True
        self.mock_args.delete_after = "2025-12-31"
        
        mock_response = {
            'response': {
                'code': '1000',
                'result': 'OK'
            }
        }
        self.mock_client.domain_delete.return_value = mock_response
        
        result = cmd_domain_delete(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)
        self.mock_client.domain_delete.assert_called_once_with("example.com", delete_after="2025-12-31")

    @patch('wapi.commands.domain.validate_domain')
    @patch('wapi.commands.domain.get_logger')
    def test_domain_delete_invalid_domain(self, mock_get_logger, mock_validate):
        """Test domain deletion with invalid domain"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (False, "Invalid domain format")
        self.mock_args.force = True
        
        with self.assertRaises(WAPIValidationError):
            cmd_domain_delete(self.mock_args, self.mock_client)

    @patch('wapi.commands.domain.validate_domain')
    @patch('wapi.commands.domain.get_logger')
    def test_domain_delete_async(self, mock_get_logger, mock_validate):
        """Test domain deletion with async response"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        self.mock_args.force = True
        
        async_response = {
            'response': {
                'code': '1001',
                'result': 'Deletion initiated'
            }
        }
        self.mock_client.domain_delete.return_value = async_response
        
        result = cmd_domain_delete(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)

    @patch('wapi.commands.domain.validate_domain')
    @patch('wapi.commands.domain.get_logger')
    def test_domain_delete_error(self, mock_get_logger, mock_validate):
        """Test domain deletion with error response"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        self.mock_args.force = True
        
        error_response = {
            'response': {
                'code': '2001',
                'result': 'Deletion failed'
            }
        }
        self.mock_client.domain_delete.return_value = error_response
        
        with self.assertRaises(WAPIRequestError):
            cmd_domain_delete(self.mock_args, self.mock_client)


class TestDomainUpdate(unittest.TestCase):
    """Test cmd_domain_update command"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_client = Mock()
        self.mock_args = Mock()
        self.mock_args.domain = "example.com"
        self.mock_args.format = "table"
        self.mock_args.owner_c = None
        self.mock_args.admin_c = None
        self.mock_args.tech_c = None
        self.mock_args.nsset = None
        self.mock_args.keyset = None
        self.mock_args.auth_info = None
        self.mock_args.wait = False
        self.mock_args.quiet = False

    @patch('wapi.commands.domain.validate_domain')
    @patch('wapi.commands.domain.get_logger')
    def test_domain_update_no_params(self, mock_get_logger, mock_validate):
        """Test domain update without any parameters"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        with self.assertRaises(WAPIValidationError) as context:
            cmd_domain_update(self.mock_args, self.mock_client)
        
        self.assertIn("parameter", str(context.exception).lower())

    @patch('wapi.commands.domain.validate_domain')
    @patch('wapi.commands.domain.get_logger')
    def test_domain_update_success(self, mock_get_logger, mock_validate):
        """Test successful domain update"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        self.mock_args.owner_c = "OWNER-C"
        
        mock_response = {
            'response': {
                'code': '1000',
                'result': 'OK'
            }
        }
        self.mock_client.domain_update.return_value = mock_response
        
        result = cmd_domain_update(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)
        self.mock_client.domain_update.assert_called_once_with(
            "example.com",
            owner_c="OWNER-C",
            admin_c=None,
            tech_c=None,
            nsset=None,
            keyset=None,
            auth_info=None
        )

    @patch('wapi.commands.domain.validate_domain')
    @patch('wapi.commands.domain.get_logger')
    def test_domain_update_with_all_params(self, mock_get_logger, mock_validate):
        """Test domain update with all parameters"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        self.mock_args.owner_c = "OWNER-C"
        self.mock_args.admin_c = "ADMIN-C"
        self.mock_args.tech_c = "TECH-C"
        self.mock_args.nsset = "NSSET-EXAMPLE"
        self.mock_args.keyset = "KEYSET-EXAMPLE"
        self.mock_args.auth_info = "AUTH123"
        
        mock_response = {
            'response': {
                'code': '1000',
                'result': 'OK'
            }
        }
        self.mock_client.domain_update.return_value = mock_response
        
        result = cmd_domain_update(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)
        self.mock_client.domain_update.assert_called_once_with(
            "example.com",
            owner_c="OWNER-C",
            admin_c="ADMIN-C",
            tech_c="TECH-C",
            nsset="NSSET-EXAMPLE",
            keyset="KEYSET-EXAMPLE",
            auth_info="AUTH123"
        )

    @patch('wapi.commands.domain.validate_domain')
    @patch('wapi.commands.domain.get_logger')
    def test_domain_update_invalid_domain(self, mock_get_logger, mock_validate):
        """Test domain update with invalid domain"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (False, "Invalid domain format")
        self.mock_args.owner_c = "OWNER-C"
        
        with self.assertRaises(WAPIValidationError):
            cmd_domain_update(self.mock_args, self.mock_client)

    @patch('wapi.commands.domain.validate_domain')
    @patch('wapi.commands.domain.get_logger')
    def test_domain_update_async_with_wait(self, mock_get_logger, mock_validate):
        """Test domain update with async response and wait"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        self.mock_args.owner_c = "OWNER-C"
        self.mock_args.wait = True
        
        async_response = {
            'response': {
                'code': '1001',
                'result': 'Processing'
            }
        }
        success_response = {
            'response': {
                'code': '1000',
                'result': 'OK',
                'data': {'domain': {'name': 'example.com'}}
            }
        }
        self.mock_client.domain_update.return_value = async_response
        self.mock_client.poll_until_complete.return_value = success_response
        
        result = cmd_domain_update(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)
        self.mock_client.poll_until_complete.assert_called_once()

    @patch('wapi.commands.domain.validate_domain')
    @patch('wapi.commands.domain.get_logger')
    def test_domain_update_error(self, mock_get_logger, mock_validate):
        """Test domain update with error response"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        self.mock_args.owner_c = "OWNER-C"
        
        error_response = {
            'response': {
                'code': '2001',
                'result': 'Update failed'
            }
        }
        self.mock_client.domain_update.return_value = error_response
        
        with self.assertRaises(WAPIRequestError):
            cmd_domain_update(self.mock_args, self.mock_client)


if __name__ == '__main__':
    unittest.main()
