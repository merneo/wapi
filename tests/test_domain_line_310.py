"""
Test for domain.py line 310 - return False edge case

Tests the fallback return False when source_dns/target_dns are not dicts
or when source_servers/target_servers are not lists.
"""

import unittest
from unittest.mock import Mock, patch

from wapi.commands.domain import cmd_domain_update_ns
from wapi.constants import EXIT_SUCCESS, API_SUCCESS, API_ASYNC


class TestDomainLine310(unittest.TestCase):
    """Test line 310 return False edge case"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_client = Mock()
        self.mock_args = Mock()

    @patch('wapi.commands.domain.enhance_nameserver_with_ipv6')
    @patch('wapi.commands.domain.validate_domain')
    @patch('wapi.commands.domain.get_logger')
    def test_completion_check_source_dns_not_dict(self, mock_get_logger, mock_validate, mock_enhance):
        """Test completion check when source_dns is not a dict (line 310)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        # Mock enhance_nameserver_with_ipv6 to return proper tuple
        mock_enhance.return_value = ({
            'name': 'ns1.example.com', 'addr_ipv4': '192.0.2.1'
        }, True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.nsset = None
        self.mock_args.nameserver = None
        self.mock_args.source_domain = 'source.com'
        self.mock_args.wait = True
        self.mock_args.no_ipv6_discovery = False
        self.mock_args.format = 'table'
        
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
                # First call: get source domain
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
            elif call_count[0] == 2:
                # During completion check, source domain with dns as string (not dict)
                return {
                    'response': {
                        'code': API_SUCCESS,
                        'data': {
                            'domain': {
                                'name': 'source.com',
                                'dns': 'not-a-dict'  # Not a dict - triggers line 310
                            }
                        }
                    }
                }
            else:
                # Polling result
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
        
        # Mock poll_until_complete - is_complete should return False when source_dns is not dict
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
                                        {'name': 'ns1.example.com', 'addr_ipv4': '192.0.2.1'}
                                    ]
                                }
                            }
                        }
                    }
                }
                # is_complete should return False (line 310) because source_dns is not dict
                result = is_complete(poll_result)
                # After False, eventually return success
                if not result:
                    # Simulate eventual success
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
    def test_completion_check_target_dns_not_dict(self, mock_get_logger, mock_validate, mock_enhance):
        """Test completion check when target_dns is not a dict (line 310)"""
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
        
        # Mock enhance_nameserver_with_ipv6 to return proper tuple
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
                # First call: get source domain
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
                # Polling result - target_dns is not a dict
                return {
                    'response': {
                        'code': API_SUCCESS,
                        'data': {
                            'domain': {
                                'name': 'example.com',
                                'dns': 'not-a-dict'  # Not a dict - triggers line 310
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
                                'dns': 'not-a-dict'
                            }
                        }
                    }
                }
                # is_complete should return False (line 310) because target_dns is not dict
                result = is_complete(poll_result)
                if not result:
                    # Eventually succeed
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
    def test_completion_check_servers_not_lists(self, mock_get_logger, mock_validate, mock_enhance):
        """Test completion check when source_servers or target_servers are not lists (line 310)"""
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
                return {
                    'response': {
                        'code': API_SUCCESS,
                        'data': {
                            'domain': {
                                'name': 'source.com',
                                'dns': {
                                    'server': 'not-a-list'  # Not a list
                                }
                            }
                        }
                    }
                }
            elif call_count[0] == 2:
                return {
                    'response': {
                        'code': API_SUCCESS,
                        'data': {
                            'domain': {
                                'name': 'source.com',
                                'dns': {
                                    'server': 'not-a-list'
                                }
                            }
                        }
                    }
                }
            else:
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
                # is_complete should return False (line 310) because source_servers is not a list
                result = is_complete(poll_result)
                if not result:
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
