"""
Complete tests for wapi.commands.nsset module to achieve 100% coverage

Tests for missing lines: edge cases in NSSET commands.
"""

import unittest
from unittest.mock import Mock, patch

from wapi.commands.nsset import cmd_nsset_create, cmd_nsset_info
from wapi.constants import EXIT_SUCCESS
from wapi.exceptions import WAPIValidationError, WAPIRequestError


class TestNSSETCreateEdgeCases(unittest.TestCase):
    """Test cmd_nsset_create edge cases"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_client = Mock()
        self.mock_args = Mock()

    @patch('wapi.commands.nsset.enhance_nameserver_with_ipv6')
    @patch('wapi.commands.nsset.validate_nameserver')
    @patch('wapi.commands.nsset.get_logger')
    def test_nsset_create_no_nameservers(self, mock_get_logger, mock_validate, mock_enhance):
        """Test cmd_nsset_create without nameservers (lines 29-32)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        self.mock_args.name = 'NS-EXAMPLE'
        self.mock_args.nameserver = None
        self.mock_args.tld = 'cz'
        self.mock_args.no_ipv6_discovery = False
        
        with self.assertRaises(WAPIValidationError) as context:
            cmd_nsset_create(self.mock_args, self.mock_client)
        
        self.assertIn("At least one nameserver required", str(context.exception))

    @patch('wapi.commands.nsset.enhance_nameserver_with_ipv6')
    @patch('wapi.commands.nsset.validate_nameserver')
    @patch('wapi.commands.nsset.get_logger')
    def test_nsset_create_invalid_nameserver(self, mock_get_logger, mock_validate, mock_enhance):
        """Test cmd_nsset_create with invalid nameserver (lines 40-43)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (False, None, "Invalid format")
        
        self.mock_args.name = 'NS-EXAMPLE'
        self.mock_args.nameserver = ['invalid-ns']
        self.mock_args.tld = 'cz'
        self.mock_args.no_ipv6_discovery = False
        
        with self.assertRaises(WAPIValidationError) as context:
            cmd_nsset_create(self.mock_args, self.mock_client)
        
        self.assertIn("Invalid nameserver format", str(context.exception))

    @patch('wapi.commands.nsset.enhance_nameserver_with_ipv6')
    @patch('wapi.commands.nsset.validate_nameserver')
    @patch('wapi.commands.nsset.get_logger')
    def test_nsset_create_ipv6_discovery_success(self, mock_get_logger, mock_validate, mock_enhance):
        """Test cmd_nsset_create with IPv6 discovery success (lines 46-52)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, {'name': 'ns1.example.com', 'addr_ipv4': '192.0.2.1'}, None)
        mock_enhance.return_value = (
            {'name': 'ns1.example.com', 'addr_ipv4': '192.0.2.1', 'addr_ipv6': '2001:db8::1'},
            True,
            None
        )
        
        self.mock_args.name = 'NS-EXAMPLE'
        self.mock_args.nameserver = ['ns1.example.com/192.0.2.1']
        self.mock_args.tld = 'cz'
        self.mock_args.no_ipv6_discovery = False
        
        self.mock_client.call.return_value = {
            'response': {
                'code': '1000',
                'data': {'nsset': 'NS-EXAMPLE'}
            }
        }
        
        result = cmd_nsset_create(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)
        mock_enhance.assert_called_once()

    @patch('wapi.commands.nsset.enhance_nameserver_with_ipv6')
    @patch('wapi.commands.nsset.validate_nameserver')
    @patch('wapi.commands.nsset.get_logger')
    def test_nsset_create_ipv6_discovery_warning(self, mock_get_logger, mock_validate, mock_enhance):
        """Test cmd_nsset_create with IPv6 discovery warning (lines 53-55)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, {'name': 'ns1.example.com', 'addr_ipv4': '192.0.2.1'}, None)
        mock_enhance.return_value = (
            {'name': 'ns1.example.com', 'addr_ipv4': '192.0.2.1'},
            False,
            "Could not find IPv6"
        )
        
        self.mock_args.name = 'NS-EXAMPLE'
        self.mock_args.nameserver = ['ns1.example.com/192.0.2.1']
        self.mock_args.tld = 'cz'
        self.mock_args.no_ipv6_discovery = False
        
        self.mock_client.call.return_value = {
            'response': {
                'code': '1000',
                'data': {'nsset': 'NS-EXAMPLE'}
            }
        }
        
        result = cmd_nsset_create(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)

    @patch('wapi.commands.nsset.enhance_nameserver_with_ipv6')
    @patch('wapi.commands.nsset.validate_nameserver')
    @patch('wapi.commands.nsset.get_logger')
    def test_nsset_create_no_ipv6_discovery(self, mock_get_logger, mock_validate, mock_enhance):
        """Test cmd_nsset_create with IPv6 discovery disabled (lines 56-57)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, {'name': 'ns1.example.com', 'addr_ipv4': '192.0.2.1'}, None)
        
        self.mock_args.name = 'NS-EXAMPLE'
        self.mock_args.nameserver = ['ns1.example.com/192.0.2.1']
        self.mock_args.tld = 'cz'
        self.mock_args.no_ipv6_discovery = True
        
        self.mock_client.call.return_value = {
            'response': {
                'code': '1000',
                'data': {'nsset': 'NS-EXAMPLE'}
            }
        }
        
        result = cmd_nsset_create(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)
        mock_enhance.assert_not_called()

    @patch('wapi.commands.nsset.enhance_nameserver_with_ipv6')
    @patch('wapi.commands.nsset.validate_nameserver')
    @patch('wapi.commands.nsset.get_logger')
    def test_nsset_create_ipv6_discovery_success_messages(self, mock_get_logger, mock_validate, mock_enhance):
        """Test cmd_nsset_create IPv6 discovery success messages (lines 62-63)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, {'name': 'ns1.example.com', 'addr_ipv4': '192.0.2.1'}, None)
        mock_enhance.return_value = (
            {'name': 'ns1.example.com', 'addr_ipv4': '192.0.2.1', 'addr_ipv6': '2001:db8::1'},
            True,
            None
        )
        
        self.mock_args.name = 'NS-EXAMPLE'
        self.mock_args.nameserver = ['ns1.example.com/192.0.2.1']
        self.mock_args.tld = 'cz'
        self.mock_args.no_ipv6_discovery = False
        
        self.mock_client.call.return_value = {
            'response': {
                'code': '1000',
                'data': {'nsset': 'NS-EXAMPLE'}
            }
        }
        
        result = cmd_nsset_create(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)

    @patch('wapi.commands.nsset.enhance_nameserver_with_ipv6')
    @patch('wapi.commands.nsset.validate_nameserver')
    @patch('wapi.commands.nsset.get_logger')
    def test_nsset_create_ipv6_discovery_warning_messages(self, mock_get_logger, mock_validate, mock_enhance):
        """Test cmd_nsset_create IPv6 discovery warning messages (lines 64-66)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, {'name': 'ns1.example.com', 'addr_ipv4': '192.0.2.1'}, None)
        mock_enhance.return_value = (
            {'name': 'ns1.example.com', 'addr_ipv4': '192.0.2.1'},
            False,
            "Could not find IPv6"
        )
        
        self.mock_args.name = 'NS-EXAMPLE'
        self.mock_args.nameserver = ['ns1.example.com/192.0.2.1']
        self.mock_args.tld = 'cz'
        self.mock_args.no_ipv6_discovery = False
        
        self.mock_client.call.return_value = {
            'response': {
                'code': '1000',
                'data': {'nsset': 'NS-EXAMPLE'}
            }
        }
        
        result = cmd_nsset_create(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)

    @patch('wapi.commands.nsset.format_output')
    @patch('wapi.commands.nsset.get_logger')
    def test_nsset_create_check_nsset_created_function_code_not_1000(self, mock_get_logger, mock_format):
        """Test cmd_nsset_create check_nsset_created function with code not 1000 (lines 98-100)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        self.mock_args.name = 'NS-EXAMPLE'
        self.mock_args.nameserver = ['ns1.example.com/192.0.2.1']
        self.mock_args.tld = 'cz'
        self.mock_args.no_ipv6_discovery = True
        self.mock_args.wait = True
        self.mock_args.format = 'table'
        self.mock_args.quiet = False
        
        # First call returns async
        self.mock_client.call.return_value = {
            'response': {
                'code': '1001',
                'data': {'result': 'async'}
            }
        }
        
        # Polling - simulate that is_complete is called with different results
        # The check_nsset_created function checks poll_code, so we need to simulate
        # that poll_until_complete calls is_complete with results that have different codes
        # First call to is_complete gets code 1001 (returns False), second gets 1000 (returns True)
        is_complete_call_count = [0]
        def mock_poll(*args, **kwargs):
            is_complete = kwargs.get('is_complete')
            if is_complete:
                is_complete_call_count[0] += 1
                # Simulate that is_complete is called multiple times by poll_until_complete
                # First time: code not 1000 -> is_complete returns False -> polling continues
                # Second time: code 1000 -> is_complete returns True -> polling stops
                if is_complete_call_count[0] == 1:
                    # First call to is_complete with code not 1000
                    # This covers lines 98-100: poll_response.get('response', {}), poll_code.get('code'), if poll_code not in ['1000', 1000]
                    result = {'response': {'code': '1001'}}
                    # is_complete will return False, so poll_until_complete will continue
                    # We need to make sure it eventually succeeds
                    return result
                else:
                    # Second call to is_complete with code 1000
                    # This covers line 101: return poll_code in ['1000', 1000]
                    return {
                        'response': {
                            'code': '1000',
                            'data': {
                                'nsset': {
                                    'name': 'NS-EXAMPLE'
                                }
                            }
                        }
                    }
            # Non-is_complete call (for the actual API call)
            return {'response': {'code': '1000'}}
        
        # Mock poll_until_complete to actually call is_complete multiple times
        def actual_mock_poll(*args, **kwargs):
            is_complete = kwargs.get('is_complete')
            if is_complete:
                # Simulate polling: first attempt fails, second succeeds
                attempt = [0]
                def check_func(result):
                    attempt[0] += 1
                    if attempt[0] == 1:
                        # First attempt: code not 1000 -> returns False
                        return False
                    else:
                        # Second attempt: code 1000 -> returns True
                        return True
                
                # Return results that will be passed to is_complete
                results = [
                    {'response': {'code': '1001'}},  # First: is_complete returns False
                    {'response': {'code': '1000', 'data': {'nsset': {'name': 'NS-EXAMPLE'}}}}  # Second: is_complete returns True
                ]
                
                # Simulate poll_until_complete behavior
                for result in results:
                    if is_complete(result):
                        return result
                # If we get here, return last result
                return results[-1]
            return {'response': {'code': '1000'}}
        
        self.mock_client.poll_until_complete.side_effect = actual_mock_poll
        
        with patch('wapi.commands.nsset.validate_nameserver', return_value=(True, {'name': 'ns1.example.com', 'addr_ipv4': '192.0.2.1'}, None)):
            result = cmd_nsset_create(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)


class TestNSSETInfoEdgeCases(unittest.TestCase):
    """Test cmd_nsset_info edge cases"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_client = Mock()
        self.mock_args = Mock()

    @patch('wapi.commands.nsset.format_output')
    @patch('wapi.commands.nsset.get_logger')
    def test_nsset_info_direct_success(self, mock_get_logger, mock_format):
        """Test cmd_nsset_info with direct nsset-info success"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        self.mock_args.nsset = 'NS-EXAMPLE'
        self.mock_args.format = 'table'
        
        self.mock_client.call.return_value = {
            'response': {
                'code': '1000',
                'data': {
                    'nsset': {
                        'name': 'NS-EXAMPLE',
                        'dns': {
                            'server': [
                                {'name': 'ns1.example.com', 'addr_ipv4': '192.0.2.1'}
                            ]
                        }
                    }
                }
            }
        }
        
        result = cmd_nsset_info(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)

    @patch('wapi.commands.nsset.format_output')
    @patch('wapi.commands.nsset.get_logger')
    def test_nsset_info_fallback_to_domain_info(self, mock_get_logger, mock_format):
        """Test cmd_nsset_info fallback to domain-info (lines 152-162)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        self.mock_args.name = 'NS-EXAMPLE'
        self.mock_args.nsset = 'NS-EXAMPLE'
        self.mock_args.domain = 'example.com'  # Important: set domain for fallback
        self.mock_args.format = 'table'
        
        # First call (nsset-info) fails
        self.mock_client.call.return_value = {
            'response': {
                'code': '2100',
                'result': 'NSSET not found'
            }
        }
        
        # domain-info succeeds with matching NSSET
        self.mock_client.domain_info.return_value = {
            'response': {
                'code': '1000',
                'data': {
                    'domain': {
                        'nsset': 'NS-EXAMPLE',
                        'dns': {
                            'server': [
                                {'name': 'ns1.example.com', 'addr_ipv4': '192.0.2.1'}
                            ]
                        }
                    }
                }
            }
        }
        
        result = cmd_nsset_info(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)

    @patch('wapi.commands.nsset.format_output')
    @patch('wapi.commands.nsset.get_logger')
    def test_nsset_info_error(self, mock_get_logger, mock_format):
        """Test cmd_nsset_info with error response (lines 177-203)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        self.mock_args.nsset = 'NS-EXAMPLE'
        self.mock_args.format = 'table'
        
        # Both calls fail
        self.mock_client.call.return_value = {
            'response': {
                'code': '2100',
                'result': 'NSSET not found'
            }
        }
        self.mock_client.domain_info.return_value = {
            'response': {
                'code': '2100',
                'result': 'Domain not found'
            }
        }
        
        with self.assertRaises(WAPIRequestError):
            cmd_nsset_info(self.mock_args, self.mock_client)

    @patch('wapi.commands.nsset.format_output')
    @patch('wapi.commands.nsset.get_logger')
    def test_nsset_create_async_with_wait(self, mock_get_logger, mock_format):
        """Test cmd_nsset_create with async and wait (lines 90-131)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        self.mock_args.name = 'NS-EXAMPLE'
        self.mock_args.nameserver = ['ns1.example.com/192.0.2.1']
        self.mock_args.tld = 'cz'
        self.mock_args.no_ipv6_discovery = True
        self.mock_args.wait = True
        self.mock_args.format = 'table'
        self.mock_args.quiet = False
        
        # First call returns async
        self.mock_client.call.return_value = {
            'response': {
                'code': '1001',
                'data': {'result': 'async'}
            }
        }
        
        # Polling returns success
        self.mock_client.poll_until_complete.return_value = {
            'response': {
                'code': '1000',
                'data': {
                    'nsset': {
                        'name': 'NS-EXAMPLE'
                    }
                }
            }
        }
        
        with patch('wapi.commands.nsset.validate_nameserver', return_value=(True, {'name': 'ns1.example.com', 'addr_ipv4': '192.0.2.1'}, None)):
            result = cmd_nsset_create(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)

    @patch('wapi.commands.nsset.format_output')
    @patch('wapi.commands.nsset.get_logger')
    def test_nsset_create_async_without_wait(self, mock_get_logger, mock_format):
        """Test cmd_nsset_create with async without wait (lines 132-134)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        self.mock_args.name = 'NS-EXAMPLE'
        self.mock_args.nameserver = ['ns1.example.com/192.0.2.1']
        self.mock_args.tld = 'cz'
        self.mock_args.no_ipv6_discovery = True
        self.mock_args.wait = False
        self.mock_args.format = 'table'
        
        self.mock_client.call.return_value = {
            'response': {
                'code': '1001',
                'data': {'result': 'async'}
            }
        }
        
        with patch('wapi.commands.nsset.validate_nameserver', return_value=(True, {'name': 'ns1.example.com', 'addr_ipv4': '192.0.2.1'}, None)):
            result = cmd_nsset_create(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)
        self.mock_client.poll_until_complete.assert_not_called()

    @patch('wapi.commands.nsset.format_output')
    @patch('wapi.commands.nsset.get_logger')
    def test_nsset_create_async_timeout(self, mock_get_logger, mock_format):
        """Test cmd_nsset_create with async timeout (lines 124-131)"""
        from wapi.exceptions import WAPITimeoutError
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        self.mock_args.name = 'NS-EXAMPLE'
        self.mock_args.nameserver = ['ns1.example.com/192.0.2.1']
        self.mock_args.tld = 'cz'
        self.mock_args.no_ipv6_discovery = True
        self.mock_args.wait = True
        self.mock_args.format = 'table'
        
        self.mock_client.call.return_value = {
            'response': {
                'code': '1001',
                'data': {'result': 'async'}
            }
        }
        
        # Polling returns timeout
        self.mock_client.poll_until_complete.return_value = {
            'response': {
                'code': '9998',
                'result': 'Timeout'
            }
        }
        
        with patch('wapi.commands.nsset.validate_nameserver', return_value=(True, {'name': 'ns1.example.com', 'addr_ipv4': '192.0.2.1'}, None)):
            with self.assertRaises(WAPITimeoutError):
                cmd_nsset_create(self.mock_args, self.mock_client)


    @patch('wapi.commands.nsset.format_output')
    @patch('wapi.commands.nsset.get_logger')
    def test_nsset_create_async_warning(self, mock_get_logger, mock_format):
        """Test cmd_nsset_create with async warning (lines 124-131)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        self.mock_args.name = 'NS-EXAMPLE'
        self.mock_args.nameserver = ['ns1.example.com/192.0.2.1']
        self.mock_args.tld = 'cz'
        self.mock_args.no_ipv6_discovery = True
        self.mock_args.wait = True
        self.mock_args.format = 'table'
        
        self.mock_client.call.return_value = {
            'response': {
                'code': '1001',
                'data': {'result': 'async'}
            }
        }
        
        # Polling returns warning (not timeout)
        self.mock_client.poll_until_complete.return_value = {
            'response': {
                'code': '1001',
                'result': 'Still processing'
            }
        }
        
        with patch('wapi.commands.nsset.validate_nameserver', return_value=(True, {'name': 'ns1.example.com', 'addr_ipv4': '192.0.2.1'}, None)):
            result = cmd_nsset_create(self.mock_args, self.mock_client)
        
        # Should return success despite warning
        self.assertEqual(result, EXIT_SUCCESS)

    @patch('wapi.commands.nsset.format_output')
    @patch('wapi.commands.nsset.get_logger')
    def test_nsset_create_error(self, mock_get_logger, mock_format):
        """Test cmd_nsset_create with error response (lines 135-139)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        self.mock_args.name = 'NS-EXAMPLE'
        self.mock_args.nameserver = ['ns1.example.com/192.0.2.1']
        self.mock_args.tld = 'cz'
        self.mock_args.no_ipv6_discovery = True
        self.mock_args.format = 'table'
        
        self.mock_client.call.return_value = {
            'response': {
                'code': '2100',
                'result': 'Error occurred'
            }
        }
        
        with patch('wapi.commands.nsset.validate_nameserver', return_value=(True, {'name': 'ns1.example.com', 'addr_ipv4': '192.0.2.1'}, None)):
            with self.assertRaises(WAPIRequestError):
                cmd_nsset_create(self.mock_args, self.mock_client)

    @patch('wapi.commands.nsset.format_output')
    @patch('wapi.commands.nsset.get_logger')
    def test_nsset_info_tld_com_detection(self, mock_get_logger, mock_format):
        """Test cmd_nsset_info TLD detection for COM (lines 161-162)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        class Args:
            name = 'NS-EXAMPLE-COM-123'
            nsset = 'NS-EXAMPLE-COM-123'
            format = 'table'
        
        args = Args()
        
        self.mock_client.call.return_value = {
            'response': {
                'code': '1000',
                'data': {
                    'nsset': {
                        'name': 'NS-EXAMPLE-COM-123'
                    }
                }
            }
        }
        
        result = cmd_nsset_info(args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)
        call_args = self.mock_client.call.call_args
        self.assertEqual(call_args[0][1]['tld'], 'com')

    @patch('wapi.commands.nsset.format_output')
    @patch('wapi.commands.nsset.get_logger')
    def test_nsset_info_error_with_domain_tip(self, mock_get_logger, mock_format):
        """Test cmd_nsset_info error with domain tip (lines 199-202)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        class Args:
            name = 'NS-EXAMPLE'
            nsset = 'NS-EXAMPLE'
            domain = 'example.com'
            format = 'table'
        
        args = Args()
        
        self.mock_client.call.return_value = {
            'response': {
                'code': '2100',
                'result': 'NSSET not found'
            }
        }
        self.mock_client.domain_info.return_value = {
            'response': {
                'code': '2100',
                'result': 'Domain not found'
            }
        }
        
        with self.assertRaises(WAPIRequestError):
            cmd_nsset_info(args, self.mock_client)

    @patch('wapi.commands.nsset.format_output')
    @patch('wapi.commands.nsset.get_logger')
    def test_nsset_info_error_without_domain_tip(self, mock_get_logger, mock_format):
        """Test cmd_nsset_info error without domain tip (lines 201-202)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        class Args:
            name = 'NS-EXAMPLE'
            nsset = 'NS-EXAMPLE'
            format = 'table'
            # No domain attribute
        
        args = Args()
        
        self.mock_client.call.return_value = {
            'response': {
                'code': '2100',
                'result': 'NSSET not found'
            }
        }
        
        with self.assertRaises(WAPIRequestError):
            cmd_nsset_info(args, self.mock_client)

    @patch('wapi.commands.nsset.format_output')
    @patch('wapi.commands.nsset.get_logger')
    def test_nsset_info_tld_detection_from_name(self, mock_get_logger, mock_format):
        """Test cmd_nsset_info TLD detection from name (lines 158-163)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        # Create args object without tld and domain attributes
        class Args:
            name = 'NS-EXAMPLE-CZ-123'
            nsset = 'NS-EXAMPLE-CZ-123'
            format = 'table'
        
        args = Args()
        
        self.mock_client.call.return_value = {
            'response': {
                'code': '1000',
                'data': {
                    'nsset': {
                        'name': 'NS-EXAMPLE-CZ-123'
                    }
                }
            }
        }
        
        result = cmd_nsset_info(args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)
        # Verify TLD was detected from name (contains -CZ-)
        call_args = self.mock_client.call.call_args
        self.assertEqual(call_args[0][1]['tld'], 'cz')

    @patch('wapi.commands.nsset.format_output')
    @patch('wapi.commands.nsset.get_logger')
    def test_nsset_info_tld_from_domain(self, mock_get_logger, mock_format):
        """Test cmd_nsset_info TLD detection from domain (lines 152-156)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        # Create args object with domain but no tld
        class Args:
            name = 'NS-EXAMPLE'
            nsset = 'NS-EXAMPLE'
            domain = 'example.com'
            format = 'table'
        
        args = Args()
        
        self.mock_client.call.return_value = {
            'response': {
                'code': '1000',
                'data': {
                    'nsset': {
                        'name': 'NS-EXAMPLE'
                    }
                }
            }
        }
        
        result = cmd_nsset_info(args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)
        # Verify TLD was extracted from domain
        call_args = self.mock_client.call.call_args
        self.assertEqual(call_args[0][1]['tld'], 'com')

    @patch('wapi.commands.nsset.format_output')
    @patch('wapi.commands.nsset.get_logger')
    def test_nsset_info_tld_from_arg(self, mock_get_logger, mock_format):
        """Test cmd_nsset_info TLD from argument (lines 150-151)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        # Create args object with tld
        class Args:
            name = 'NS-EXAMPLE'
            nsset = 'NS-EXAMPLE'
            tld = 'sk'
            format = 'table'
        
        args = Args()
        
        self.mock_client.call.return_value = {
            'response': {
                'code': '1000',
                'data': {
                    'nsset': {
                        'name': 'NS-EXAMPLE'
                    }
                }
            }
        }
        
        result = cmd_nsset_info(args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)
        # Verify TLD was used from argument
        call_args = self.mock_client.call.call_args
        self.assertEqual(call_args[0][1]['tld'], 'sk')


if __name__ == '__main__':
    unittest.main()
