"""
Tests for domain update-ns completion check function (lines 290-305)

Tests for the is_complete function inside cmd_domain_update_ns.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock

from wapi.commands.domain import cmd_domain_update_ns
from wapi.constants import EXIT_SUCCESS, API_SUCCESS, API_ASYNC


class TestDomainCompletionCheck(unittest.TestCase):
    """Test completion check function logic"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_client = Mock()
        self.mock_args = Mock()

    @patch('wapi.commands.domain.enhance_nameserver_with_ipv6')
    @patch('wapi.commands.domain.validate_domain')
    @patch('wapi.commands.domain.get_logger')
    def test_completion_check_source_names_match(self, mock_get_logger, mock_validate, mock_enhance):
        """Test completion check when source and target names match (line 304)"""
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
                                {'name': 'ns1.source.com', 'addr_ipv4': '192.0.2.1'},
                                {'name': 'ns2.source.com', 'addr_ipv4': '192.0.2.2'}
                            ]
                        }
                    }
                }
            }
        }
        
        mock_enhance.side_effect = [
            ({'name': 'ns1.example.com', 'addr_ipv4': '192.0.2.1'}, True, None),
            ({'name': 'ns2.example.com', 'addr_ipv4': '192.0.2.2'}, True, None)
        ]
        
        # Mock async response
        mock_async_response = {
            'response': {
                'code': API_ASYNC,
                'data': {'result': 'async'}
            }
        }
        self.mock_client.domain_update_ns.return_value = mock_async_response
        
        # Mock domain_info calls - simulate completion check
        call_count = [0]
        def mock_domain_info(domain):
            call_count[0] += 1
            if call_count[0] == 1:
                # First call: get source domain
                return mock_source_response
            elif call_count[0] == 2:
                # Second call: during completion check, get source domain again
                return {
                    'response': {
                        'code': API_SUCCESS,
                        'data': {
                            'domain': {
                                'name': 'source.com',
                                'dns': {
                                    'server': [
                                        {'name': 'ns1.source.com', 'addr_ipv4': '192.0.2.1'},
                                        {'name': 'ns2.source.com', 'addr_ipv4': '192.0.2.2'}
                                    ]
                                }
                            }
                        }
                    }
                }
            else:
                # Polling result - target domain with matching names
                return {
                    'response': {
                        'code': API_SUCCESS,
                        'data': {
                            'domain': {
                                'name': 'example.com',
                                'dns': {
                                    'server': [
                                        {'name': 'ns1.example.com', 'addr_ipv4': '192.0.2.1'},
                                        {'name': 'ns2.example.com', 'addr_ipv4': '192.0.2.2'}
                                    ]
                                }
                            }
                        }
                    }
                }
        
        self.mock_client.domain_info.side_effect = mock_domain_info
        
        # Mock poll_until_complete to actually call is_complete
        def mock_poll(*args, **kwargs):
            is_complete = kwargs.get('is_complete')
            if is_complete:
                # Create poll result with target domain
                poll_result = {
                    'response': {
                        'code': API_SUCCESS,
                        'data': {
                            'domain': {
                                'name': 'example.com',
                                'dns': {
                                    'server': [
                                        {'name': 'ns1.example.com', 'addr_ipv4': '192.0.2.1'},
                                        {'name': 'ns2.example.com', 'addr_ipv4': '192.0.2.2'}
                                    ]
                                }
                            }
                        }
                    }
                }
                # Call is_complete - it should check source domain and compare names
                result = is_complete(poll_result)
                if result:
                    return poll_result
                # If not complete, continue
                return poll_result
            return {'response': {'code': API_SUCCESS, 'data': {}}}
        
        self.mock_client.poll_until_complete.side_effect = mock_poll
        
        with patch('wapi.utils.validators.validate_nameserver', side_effect=[
            (True, {'name': 'ns1.source.com', 'addr_ipv4': '192.0.2.1'}, None),
            (True, {'name': 'ns2.source.com', 'addr_ipv4': '192.0.2.2'}, None)
        ]):
            result = cmd_domain_update_ns(self.mock_args, self.mock_client)
            
            self.assertEqual(result, EXIT_SUCCESS)

    @patch('wapi.commands.domain.enhance_nameserver_with_ipv6')
    @patch('wapi.commands.domain.validate_domain')
    @patch('wapi.commands.domain.get_logger')
    def test_completion_check_source_names_dont_match(self, mock_get_logger, mock_validate, mock_enhance):
        """Test completion check when source and target names don't match"""
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
        
        # Mock domain_info calls
        call_count = [0]
        def mock_domain_info(domain):
            call_count[0] += 1
            if call_count[0] == 1:
                return mock_source_response
            elif call_count[0] == 2:
                # During completion check, source domain
                return {
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
            else:
                # Polling result - different names (not matching)
                return {
                    'response': {
                        'code': API_SUCCESS,
                        'data': {
                            'domain': {
                                'name': 'example.com',
                                'dns': {
                                    'server': [
                                        {'name': 'ns-different.example.com', 'addr_ipv4': '192.0.2.1'}  # Different name
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
                poll_result = {
                    'response': {
                        'code': API_SUCCESS,
                        'data': {
                            'domain': {
                                'name': 'example.com',
                                'dns': {
                                    'server': [
                                        {'name': 'ns-different.example.com', 'addr_ipv4': '192.0.2.1'}
                                    ]
                                }
                            }
                        }
                    }
                }
                # is_complete should return False (names don't match)
                result = is_complete(poll_result)
                # Continue polling until success
                if not result:
                    return {
                        'response': {
                            'code': API_SUCCESS,
                            'data': {
                                'domain': {
                                    'name': 'example.com',
                                    'dns': {
                                        'server': [
                                            {'name': 'ns1.example.com', 'addr_ipv4': '192.0.2.1'}  # Now matches
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
    def test_completion_check_server_not_dict(self, mock_get_logger, mock_validate, mock_enhance):
        """Test completion check when server entry is not a dict (line 302-303)"""
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
        
        # Mock domain_info calls
        call_count = [0]
        def mock_domain_info(domain):
            call_count[0] += 1
            if call_count[0] == 1:
                return mock_source_response
            elif call_count[0] == 2:
                return {
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
            else:
                # Polling result - server entry is not a dict
                return {
                    'response': {
                        'code': API_SUCCESS,
                        'data': {
                            'domain': {
                                'name': 'example.com',
                                'dns': {
                                    'server': [
                                        'not-a-dict',  # Not a dict
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
                poll_result = {
                    'response': {
                        'code': API_SUCCESS,
                        'data': {
                            'domain': {
                                'name': 'example.com',
                                'dns': {
                                    'server': [
                                        'not-a-dict',
                                        {'name': 'ns1.example.com', 'addr_ipv4': '192.0.2.1'}
                                    ]
                                }
                            }
                        }
                    }
                }
                # is_complete will filter out non-dict entries, so should still work
                result = is_complete(poll_result)
                if result:
                    return poll_result
                # Continue
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
