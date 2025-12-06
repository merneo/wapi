"""
Tests for domain update-ns source domain completion check

Tests for the complex completion check logic when copying from source domain.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock

from wapi.commands.domain import cmd_domain_update_ns
from wapi.constants import EXIT_SUCCESS, API_SUCCESS, API_ASYNC
from wapi.exceptions import WAPIRequestError


class TestDomainUpdateNSSourceComplete(unittest.TestCase):
    """Test source domain completion check scenarios"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_client = Mock()
        self.mock_args = Mock()

    @patch('wapi.commands.domain.enhance_nameserver_with_ipv6')
    @patch('wapi.commands.domain.validate_domain')
    @patch('wapi.commands.domain.get_logger')
    def test_source_domain_complete_check_source_not_dict(self, mock_get_logger, mock_validate, mock_enhance):
        """Test completion check when source_dns is not a dict"""
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
        
        # Mock source domain info
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
        self.mock_client.domain_info.return_value = mock_source_response
        
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
        
        # Mock polling response where source_dns is not a dict (edge case)
        def mock_poll_side_effect(*args, **kwargs):
            # First call returns source domain
            if self.mock_client.domain_info.call_count == 1:
                return mock_source_response
            # Polling returns response where source_dns check fails
            return {
                'response': {
                    'code': API_SUCCESS,
                    'data': {
                        'domain': {
                            'name': 'example.com',
                            'dns': None  # Not a dict
                        }
                    }
                }
            }
        
        # Mock poll_until_complete to call is_complete function
        def mock_poll(*args, **kwargs):
            is_complete = kwargs.get('is_complete')
            if is_complete:
                # Call is_complete with a result where source_dns is not dict
                poll_result = {
                    'response': {
                        'code': API_SUCCESS,
                        'data': {
                            'domain': {
                                'name': 'example.com',
                                'dns': 'not-a-dict'  # Not a dict
                            }
                        }
                    }
                }
                # is_complete should return False
                result = is_complete(poll_result)
                if not result:
                    # Continue polling - return final result
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
            return {
                'response': {
                    'code': API_SUCCESS,
                    'data': {'domain': {}}
                }
            }
        
        self.mock_client.domain_info.side_effect = mock_poll_side_effect
        self.mock_client.poll_until_complete.side_effect = mock_poll
        
        result = cmd_domain_update_ns(self.mock_args, self.mock_client)
        
        # Should complete successfully
        self.assertEqual(result, EXIT_SUCCESS)

    @patch('wapi.commands.domain.enhance_nameserver_with_ipv6')
    @patch('wapi.commands.domain.validate_domain')
    @patch('wapi.commands.domain.get_logger')
    def test_source_domain_complete_check_servers_not_list(self, mock_get_logger, mock_validate, mock_enhance):
        """Test completion check when servers are not lists"""
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
        
        # Mock source domain info
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
        self.mock_client.domain_info.return_value = mock_source_response
        
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
        
        # Mock poll_until_complete to simulate servers not being lists
        def mock_poll(*args, **kwargs):
            is_complete = kwargs.get('is_complete')
            if is_complete:
                # Simulate case where servers are not lists
                poll_result = {
                    'response': {
                        'code': API_SUCCESS,
                        'data': {
                            'domain': {
                                'name': 'example.com',
                                'dns': {
                                    'server': 'not-a-list'  # Not a list
                                }
                            }
                        }
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
            return {'response': {'code': API_SUCCESS, 'data': {}}}
        
        self.mock_client.poll_until_complete.side_effect = mock_poll
        
        result = cmd_domain_update_ns(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)

    @patch('wapi.commands.domain.enhance_nameserver_with_ipv6')
    @patch('wapi.commands.domain.validate_domain')
    @patch('wapi.commands.domain.get_logger')
    def test_source_domain_complete_check_source_info_fails(self, mock_get_logger, mock_validate, mock_enhance):
        """Test completion check when source domain info fails during check"""
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
        
        # Mock source domain info (first call succeeds)
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
        
        # Second call (during completion check) fails
        mock_source_fail = {
            'response': {
                'code': '2000',
                'result': 'Error'
            }
        }
        
        self.mock_client.domain_info.side_effect = [mock_source_response, mock_source_fail]
        
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
        
        # Mock poll_until_complete
        def mock_poll(*args, **kwargs):
            is_complete = kwargs.get('is_complete')
            if is_complete:
                # Call is_complete - it will try to get source domain info again
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
                # is_complete will call domain_info for source, which will fail
                # So it should return False
                is_complete(poll_result)
                # Return final success anyway
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
            return {'response': {'code': API_SUCCESS, 'data': {}}}
        
        self.mock_client.poll_until_complete.side_effect = mock_poll
        
        result = cmd_domain_update_ns(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)


if __name__ == '__main__':
    unittest.main()
