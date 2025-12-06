"""
Tests for remaining uncovered lines in domain commands

Tests to cover lines 162-164, 246-247, 278, 286, 290-305, 338-341.
"""

import unittest
from unittest.mock import Mock, patch

from wapi.commands.domain import (
    cmd_domain_update_ns,
    cmd_domain_create,
    cmd_domain_renew,
    cmd_domain_update,
)
from wapi.constants import EXIT_SUCCESS, API_SUCCESS, API_ASYNC
from wapi.exceptions import WAPIValidationError, WAPIRequestError


class TestDomainRemainingLines(unittest.TestCase):
    """Test remaining uncovered lines"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_client = Mock()
        self.mock_args = Mock()

    @patch('wapi.commands.domain.validate_domain')
    @patch('wapi.commands.domain.get_logger')
    def test_domain_update_ns_invalid_nameserver_format(self, mock_get_logger, mock_validate):
        """Test domain update-ns with invalid nameserver format (line 162-164)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.nsset = None
        self.mock_args.nameserver = ['invalid-nameserver']
        self.mock_args.source_domain = None
        self.mock_args.wait = False
        self.mock_args.no_ipv6_discovery = False
        self.mock_args.format = 'table'
        
        # validate_nameserver is imported inside the function, patch it where it's used
        with patch('wapi.utils.validators.validate_nameserver', return_value=(False, None, "Invalid format")):
            with self.assertRaises(WAPIValidationError):
                result = cmd_domain_update_ns(self.mock_args, self.mock_client)

    @patch('wapi.commands.domain.enhance_nameserver_with_ipv6')
    @patch('wapi.commands.domain.validate_domain')
    @patch('wapi.commands.domain.get_logger')
    def test_domain_update_ns_source_domain_ipv6_warning(self, mock_get_logger, mock_validate, mock_enhance):
        """Test domain update-ns source domain with IPv6 warning (line 246-247)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.nsset = None
        self.mock_args.nameserver = None
        self.mock_args.source_domain = 'source.com'
        self.mock_args.wait = False
        self.mock_args.no_ipv6_discovery = False
        self.mock_args.format = 'table'
        
        # Mock source domain info
        mock_source_response = {
            'response': {
                'code': API_SUCCESS,
                'data': {
                    'domain': {
                        'name': 'source.com',
                        'dns': {
                            'server': [
                                {'name': 'ns1.source.com', 'addr_ipv4': '192.0.2.1', 'addr_ipv6': ''}
                            ]
                        }
                    }
                }
            }
        }
        self.mock_client.domain_info.return_value = mock_source_response
        
        # Mock enhance_nameserver_with_ipv6 to return found=False with warning
        mock_enhance.return_value = ({
            'name': 'ns1.example.com', 'addr_ipv4': '192.0.2.1'
        }, False, "IPv6 address not found")
        
        mock_response = {
            'response': {
                'code': API_SUCCESS,
                'data': {'result': 'success'}
            }
        }
        self.mock_client.domain_update_ns.return_value = mock_response
        
        result = cmd_domain_update_ns(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)
        # Should call enhance_nameserver_with_ipv6 and log warning
        mock_enhance.assert_called_once()

    @patch('wapi.commands.domain.enhance_nameserver_with_ipv6')
    @patch('wapi.commands.domain.validate_domain')
    @patch('wapi.commands.domain.get_logger')
    def test_domain_update_ns_polling_code_not_1000(self, mock_get_logger, mock_validate, mock_enhance):
        """Test polling completion check when code is not 1000 (line 278)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.nsset = 'NSSET-EXAMPLE'
        self.mock_args.nameserver = None
        self.mock_args.source_domain = None
        self.mock_args.wait = True
        self.mock_args.format = 'table'
        
        # Mock async response
        mock_async_response = {
            'response': {
                'code': API_ASYNC,
                'data': {'result': 'async'}
            }
        }
        self.mock_client.domain_update_ns.return_value = mock_async_response
        
        # Mock poll_until_complete to call is_complete with non-1000 code
        def mock_poll(*args, **kwargs):
            is_complete = kwargs.get('is_complete')
            if is_complete:
                # Call is_complete with code not 1000
                poll_result = {
                    'response': {
                        'code': '2000',  # Not 1000
                        'data': {}
                    }
                }
                # is_complete should return False
                is_complete(poll_result)
                # Return final success
                return {
                    'response': {
                        'code': API_SUCCESS,
                        'data': {
                            'domain': {
                                'nsset': 'NSSET-EXAMPLE'
                            }
                        }
                    }
                }
            return {'response': {'code': API_SUCCESS, 'data': {}}}
        
        self.mock_client.poll_until_complete.side_effect = mock_poll
        
        result = cmd_domain_update_ns(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)

    @patch('wapi.commands.domain.enhance_nameserver_with_ipv6')
    @patch('wapi.commands.domain.validate_domain')
    @patch('wapi.commands.domain.get_logger')
    def test_domain_update_ns_polling_nsset_name_check(self, mock_get_logger, mock_validate, mock_enhance):
        """Test polling completion check for nsset_name match (line 286)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.nsset = 'NSSET-EXAMPLE'
        self.mock_args.nameserver = None
        self.mock_args.source_domain = None
        self.mock_args.wait = True
        self.mock_args.format = 'table'
        
        # Mock async response
        mock_async_response = {
            'response': {
                'code': API_ASYNC,
                'data': {'result': 'async'}
            }
        }
        self.mock_client.domain_update_ns.return_value = mock_async_response
        
        # Mock poll_until_complete to call is_complete with matching nsset
        def mock_poll(*args, **kwargs):
            is_complete = kwargs.get('is_complete')
            if is_complete:
                # Call is_complete with matching nsset
                poll_result = {
                    'response': {
                        'code': API_SUCCESS,
                        'data': {
                            'domain': {
                                'nsset': 'NSSET-EXAMPLE'  # Matches
                            }
                        }
                    }
                }
                # is_complete should return True
                result = is_complete(poll_result)
                if result:
                    return poll_result
            return {'response': {'code': API_SUCCESS, 'data': {}}}
        
        self.mock_client.poll_until_complete.side_effect = mock_poll
        
        result = cmd_domain_update_ns(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)

    @patch('wapi.commands.domain.enhance_nameserver_with_ipv6')
    @patch('wapi.commands.domain.validate_domain')
    @patch('wapi.commands.domain.get_logger')
    def test_domain_update_ns_polling_nameservers_check(self, mock_get_logger, mock_validate, mock_enhance):
        """Test polling completion check for nameservers (line 286-289)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.nsset = None
        self.mock_args.nameserver = ['ns1.example.com:192.0.2.1']
        self.mock_args.source_domain = None
        self.mock_args.wait = True
        self.mock_args.no_ipv6_discovery = False
        self.mock_args.format = 'table'
        
        mock_enhance.return_value = ({
            'name': 'ns1.example.com', 'addr_ipv4': '192.0.2.1'
        }, True, None)
        
        # Mock async response
        mock_async_response = {
            'response': {
                'code': API_ASYNC,
                'data': {'result': 'async'}
            }
        }
        self.mock_client.domain_update_ns.return_value = mock_async_response
        
        # Mock poll_until_complete to call is_complete with nsset assigned
        def mock_poll(*args, **kwargs):
            is_complete = kwargs.get('is_complete')
            if is_complete:
                # Call is_complete with nsset assigned (any nsset means success)
                poll_result = {
                    'response': {
                        'code': API_SUCCESS,
                        'data': {
                            'domain': {
                                'nsset': 'NSSET-NEW'  # Any nsset means nameservers were set
                            }
                        }
                    }
                }
                # is_complete should return True (bool(current_nsset) is True)
                result = is_complete(poll_result)
                if result:
                    return poll_result
            return {'response': {'code': API_SUCCESS, 'data': {}}}
        
        self.mock_client.poll_until_complete.side_effect = mock_poll
        
        with patch('wapi.utils.validators.validate_nameserver', return_value=(True, {'name': 'ns1.example.com', 'addr_ipv4': '192.0.2.1'}, None)):
            result = cmd_domain_update_ns(self.mock_args, self.mock_client)
            
            self.assertEqual(result, EXIT_SUCCESS)

    @patch('wapi.commands.domain.enhance_nameserver_with_ipv6')
    @patch('wapi.commands.domain.validate_domain')
    @patch('wapi.commands.domain.get_logger')
    def test_domain_update_ns_polling_source_domain_complete(self, mock_get_logger, mock_validate, mock_enhance):
        """Test polling completion check for source domain (lines 290-305)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.nsset = None
        self.mock_args.nameserver = None
        self.mock_args.source_domain = 'source.com'
        self.mock_args.wait = True
        self.mock_args.no_ipv6_discovery = False
        self.mock_args.format = 'table'
        
        # Mock source domain info (first call)
        mock_source_response = {
            'response': {
                'code': API_SUCCESS,
                'data': {
                    'domain': {
                        'name': 'source.com',
                        'dns': {
                            'server': [
                                {'name': 'ns1.source.com', 'addr_ipv4': '192.0.2.1'}
                            ]
                        }
                    }
                }
            }
        }
        
        mock_enhance.return_value = ({
            'name': 'ns1.example.com', 'addr_ipv4': '192.0.2.1'
        }, True, None)
        
        # Mock async response
        mock_async_response = {
            'response': {
                'code': API_ASYNC,
                'data': {'result': 'async'}
            }
        }
        self.mock_client.domain_update_ns.return_value = mock_async_response
        
        # Mock domain_info calls: first for source domain, then during polling
        def mock_domain_info(domain):
            if domain == 'source.com':
                return mock_source_response
            elif domain == 'example.com':
                # Polling result - nameservers match
                return {
                    'response': {
                        'code': API_SUCCESS,
                        'data': {
                            'domain': {
                                'name': 'example.com',
                                'dns': {
                                    'server': [
                                        {'name': 'ns1.example.com', 'addr_ipv4': '192.0.2.1'}
                                    ]
                                }
                            }
                        }
                    }
                }
        
        self.mock_client.domain_info.side_effect = mock_domain_info
        
        # Mock poll_until_complete
        def mock_poll(*args, **kwargs):
            is_complete = kwargs.get('is_complete')
            if is_complete:
                # Call is_complete - it will check source domain nameservers
                poll_result = {
                    'response': {
                        'code': API_SUCCESS,
                        'data': {
                            'domain': {
                                'name': 'example.com',
                                'dns': {
                                    'server': [
                                        {'name': 'ns1.example.com', 'addr_ipv4': '192.0.2.1'}
                                    ]
                                }
                            }
                        }
                    }
                }
                # is_complete should return True (nameservers match)
                result = is_complete(poll_result)
                if result:
                    return poll_result
            return {'response': {'code': API_SUCCESS, 'data': {}}}
        
        self.mock_client.poll_until_complete.side_effect = mock_poll
        
        result = cmd_domain_update_ns(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)


# --- Additional coverage for async branches in domain create/renew/update ---

    @patch('wapi.commands.domain.format_output')
    @patch('wapi.commands.domain.validate_domain')
    @patch('wapi.commands.domain.get_logger')
    def test_domain_create_async_wait(self, mock_get_logger, mock_validate, mock_format):
        mock_get_logger.return_value = Mock()
        mock_validate.return_value = (True, None)

        args = Mock()
        args.domain = 'example.com'
        args.period = 1
        args.owner_c = None
        args.admin_c = None
        args.nsset = None
        args.keyset = None
        args.auth_info = None
        args.wait = True
        args.format = 'table'
        args.quiet = False

        self.mock_client.domain_create.return_value = {
            'response': {'code': '1001', 'data': {}}
        }

        def fake_poll(cmd, params, is_complete, **kwargs):
            poll_res = {'response': {'code': '1000', 'data': {}}}
            # Execute completion check to cover lines 399-401
            self.assertTrue(is_complete(poll_res))
            return poll_res

        self.mock_client.poll_until_complete.side_effect = fake_poll

        result = cmd_domain_create(args, self.mock_client)
        self.assertEqual(result, EXIT_SUCCESS)
        self.mock_client.poll_until_complete.assert_called_once()

    @patch('wapi.commands.domain.format_output')
    @patch('wapi.commands.domain.validate_domain')
    @patch('wapi.commands.domain.get_logger')
    def test_domain_create_async_no_wait(self, mock_get_logger, mock_validate, mock_format):
        mock_get_logger.return_value = Mock()
        mock_validate.return_value = (True, None)

        args = Mock()
        args.domain = 'example.com'
        args.period = 1
        args.owner_c = None
        args.admin_c = None
        args.nsset = None
        args.keyset = None
        args.auth_info = None
        args.wait = False
        args.format = 'table'

        self.mock_client.domain_create.return_value = {
            'response': {'code': '1001', 'data': {'result': 'async'}}
        }

        result = cmd_domain_create(args, self.mock_client)
        self.assertEqual(result, EXIT_SUCCESS)
        mock_format.assert_called_once()

    @patch('wapi.commands.domain.format_output')
    @patch('wapi.commands.domain.validate_domain')
    @patch('wapi.commands.domain.get_logger')
    def test_domain_renew_async_wait(self, mock_get_logger, mock_validate, mock_format):
        mock_get_logger.return_value = Mock()
        mock_validate.return_value = (True, None)

        args = Mock()
        args.domain = 'example.com'
        args.period = 1
        args.wait = True
        args.format = 'table'
        args.quiet = False

        self.mock_client.domain_renew.return_value = {
            'response': {'code': '1001', 'data': {}}
        }

        def fake_poll(cmd, params, is_complete, **kwargs):
            poll_res = {'response': {'code': '1000', 'data': {}}}
            # Cover check_domain_renewed (lines 516-523)
            self.assertTrue(is_complete(poll_res))
            return poll_res

        self.mock_client.poll_until_complete.side_effect = fake_poll

        result = cmd_domain_renew(args, self.mock_client)
        self.assertEqual(result, EXIT_SUCCESS)
        self.mock_client.poll_until_complete.assert_called_once()

    @patch('wapi.commands.domain.format_output')
    @patch('wapi.commands.domain.validate_domain')
    @patch('wapi.commands.domain.get_logger')
    def test_domain_renew_async_no_wait(self, mock_get_logger, mock_validate, mock_format):
        mock_get_logger.return_value = Mock()
        mock_validate.return_value = (True, None)

        args = Mock()
        args.domain = 'example.com'
        args.period = 1
        args.wait = False
        args.format = 'table'

        self.mock_client.domain_renew.return_value = {
            'response': {'code': '1001', 'data': {'result': 'async'}}
        }

        result = cmd_domain_renew(args, self.mock_client)
        self.assertEqual(result, EXIT_SUCCESS)
        mock_format.assert_called_once()

    @patch('wapi.commands.domain.format_output')
    @patch('wapi.commands.domain.validate_domain')
    @patch('wapi.commands.domain.get_logger')
    def test_domain_update_async_wait(self, mock_get_logger, mock_validate, mock_format):
        mock_get_logger.return_value = Mock()
        mock_validate.return_value = (True, None)

        args = Mock()
        args.domain = 'example.com'
        args.owner_c = None
        args.admin_c = None
        args.tech_c = None
        args.nsset = None
        args.keyset = None
        args.wait = True
        args.format = 'table'
        args.quiet = False

        self.mock_client.domain_update.return_value = {
            'response': {'code': '1001', 'data': {}}
        }

        def fake_poll(cmd, params, is_complete, **kwargs):
            poll_res = {'response': {'code': '1000', 'data': {}}}
            # Cover check_domain_updated (lines 657-659)
            self.assertTrue(is_complete(poll_res))
            return poll_res

        self.mock_client.poll_until_complete.side_effect = fake_poll

        result = cmd_domain_update(args, self.mock_client)
        self.assertEqual(result, EXIT_SUCCESS)
        self.mock_client.poll_until_complete.assert_called_once()

    @patch('wapi.commands.domain.format_output')
    @patch('wapi.commands.domain.validate_domain')
    @patch('wapi.commands.domain.get_logger')
    def test_domain_update_async_no_wait(self, mock_get_logger, mock_validate, mock_format):
        mock_get_logger.return_value = Mock()
        mock_validate.return_value = (True, None)

        args = Mock()
        args.domain = 'example.com'
        args.owner_c = None
        args.admin_c = None
        args.tech_c = None
        args.nsset = None
        args.keyset = None
        args.wait = False
        args.format = 'table'

        self.mock_client.domain_update.return_value = {
            'response': {'code': '1001', 'data': {'result': 'async'}}
        }

        result = cmd_domain_update(args, self.mock_client)
        self.assertEqual(result, EXIT_SUCCESS)
        mock_format.assert_called_once()

    @patch('wapi.commands.domain.format_output')
    @patch('wapi.commands.domain.validate_domain')
    @patch('wapi.commands.domain.get_logger')
    def test_domain_create_async_wait_timeout(self, mock_get_logger, mock_validate, mock_format):
        from wapi.exceptions import WAPITimeoutError

        mock_get_logger.return_value = Mock()
        mock_validate.return_value = (True, None)

        args = Mock()
        args.domain = 'example.com'
        args.period = 1
        args.owner_c = None
        args.admin_c = None
        args.nsset = None
        args.keyset = None
        args.auth_info = None
        args.wait = True
        args.format = 'table'
        args.quiet = False

        self.mock_client.domain_create.return_value = {
            'response': {'code': '1001', 'data': {}}
        }

        # Simulate polling timeout (code 9998)
        self.mock_client.poll_until_complete.return_value = {
            'response': {'code': '9998', 'result': 'Timeout'}
        }

        with self.assertRaises(WAPITimeoutError):
            cmd_domain_create(args, self.mock_client)

    @patch('wapi.commands.domain.format_output')
    @patch('wapi.commands.domain.validate_domain')
    @patch('wapi.commands.domain.get_logger')
    def test_domain_create_async_wait_warning_non_timeout(self, mock_get_logger, mock_validate, mock_format):
        """Non-timeout warning path should return success (line 427)."""
        mock_get_logger.return_value = Mock()
        mock_validate.return_value = (True, None)

        args = Mock()
        args.domain = 'example.com'
        args.period = 1
        args.owner_c = None
        args.admin_c = None
        args.nsset = None
        args.keyset = None
        args.auth_info = None
        args.wait = True
        args.format = 'table'
        args.quiet = False

        self.mock_client.domain_create.return_value = {
            'response': {'code': '1001', 'data': {}}
        }

        # Poll returns warning but not timeout
        self.mock_client.poll_until_complete.return_value = {
            'response': {'code': '1001', 'result': 'Still processing'}
        }

        result = cmd_domain_create(args, self.mock_client)
        self.assertEqual(result, EXIT_SUCCESS)

    @patch('wapi.commands.domain.format_output')
    @patch('wapi.commands.domain.validate_domain')
    @patch('wapi.commands.domain.get_logger')
    def test_domain_renew_async_wait_intermediate_failure(self, mock_get_logger, mock_validate, mock_format):
        mock_get_logger.return_value = Mock()
        mock_validate.return_value = (True, None)

        args = Mock()
        args.domain = 'example.com'
        args.period = 1
        args.wait = True
        args.format = 'table'
        args.quiet = False

        self.mock_client.domain_renew.return_value = {
            'response': {'code': '1001', 'data': {}}
        }

        def fake_poll(cmd, params, is_complete, **kwargs):
            # First check returns False (code not 1000), then return success
            first = {'response': {'code': '2000', 'data': {}}}
            self.assertFalse(is_complete(first))  # covers line 519
            return {'response': {'code': '1000', 'data': {}}}

        self.mock_client.poll_until_complete.side_effect = fake_poll

        result = cmd_domain_renew(args, self.mock_client)
        self.assertEqual(result, EXIT_SUCCESS)

    @patch('wapi.commands.domain.format_output')
    @patch('wapi.commands.domain.validate_domain')
    @patch('wapi.commands.domain.get_logger')
    def test_domain_update_async_wait_warning_non_timeout(self, mock_get_logger, mock_validate, mock_format):
        mock_get_logger.return_value = Mock()
        mock_validate.return_value = (True, None)

        args = Mock()
        args.domain = 'example.com'
        args.owner_c = None
        args.admin_c = None
        args.tech_c = None
        args.nsset = None
        args.keyset = None
        args.wait = True
        args.format = 'table'
        args.quiet = False

        self.mock_client.domain_update.return_value = {
            'response': {'code': '1001', 'data': {}}
        }

        # Poll returns warning but not timeout to hit line 685
        self.mock_client.poll_until_complete.return_value = {
            'response': {'code': '1001', 'result': 'Still processing'}
        }

        result = cmd_domain_update(args, self.mock_client)
        self.assertEqual(result, EXIT_SUCCESS)

    @patch('wapi.commands.domain.validate_domain')
    @patch('wapi.commands.domain.get_logger')
    def test_domain_update_ns_api_error(self, mock_get_logger, mock_validate):
        """Test domain update-ns with API error (line 338-341)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.nsset = 'NSSET-EXAMPLE'
        self.mock_args.nameserver = None
        self.mock_args.source_domain = None
        self.mock_args.wait = False
        self.mock_args.format = 'table'
        
        # Mock failed API response
        mock_response = {
            'response': {
                'code': '2000',
                'result': 'API error'
            }
        }
        self.mock_client.domain_update_ns.return_value = mock_response
        
        with self.assertRaises(WAPIRequestError):
            result = cmd_domain_update_ns(self.mock_args, self.mock_client)


if __name__ == '__main__':
    unittest.main()
