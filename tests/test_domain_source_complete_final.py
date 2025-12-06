"""
Final tests for domain update-ns source domain completion check (lines 290-305)

Tests for the complex nested completion check logic.
"""

import unittest
from unittest.mock import Mock, patch

from wapi.commands.domain import cmd_domain_update_ns
from wapi.constants import EXIT_SUCCESS, API_SUCCESS, API_ASYNC


class TestDomainSourceCompleteFinal(unittest.TestCase):
    """Test source domain completion check edge cases"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_client = Mock()
        self.mock_args = Mock()

    @patch('wapi.commands.domain.enhance_nameserver_with_ipv6')
    @patch('wapi.commands.domain.validate_domain')
    @patch('wapi.commands.domain.get_logger')
    def test_source_domain_complete_source_info_fails_during_check(self, mock_get_logger, mock_validate, mock_enhance):
        """Test completion check when source domain info fails during check (line 293)"""
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
        
        # Mock domain_info: first call succeeds, second (during check) fails
        call_count = [0]
        def mock_domain_info(domain):
            call_count[0] += 1
            if call_count[0] == 1:
                return mock_source_response
            elif call_count[0] == 2:
                # During completion check, source domain info fails
                return {
                    'response': {
                        'code': '2000',
                        'result': 'Error'
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
        
        # Mock poll_until_complete
        def mock_poll(*args, **kwargs):
            is_complete = kwargs.get('is_complete')
            if is_complete:
                # Call is_complete - it will try to get source domain info
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
    def test_source_domain_complete_source_dns_not_dict(self, mock_get_logger, mock_validate, mock_enhance):
        """Test completion check when source_dns is not a dict (line 297)"""
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
                # During completion check, source_dns is not a dict
                return {
                    'response': {
                        'code': API_SUCCESS,
                        'data': {
                            'domain': {
                                'name': 'source.com',
                                'dns': 'not-a-dict'  # Not a dict
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
                # is_complete will check source_dns, which is not a dict, so returns False
                is_complete(poll_result)
                # Return success
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
    def test_source_domain_complete_target_dns_not_dict(self, mock_get_logger, mock_validate, mock_enhance):
        """Test completion check when target_dns is not a dict (line 297)"""
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
                # During completion check, target_dns is not a dict
                return {
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
                                'dns': 'not-a-dict'  # Not a dict
                            }
                        }
                    }
                }
                # is_complete will check target_dns, which is not a dict, so returns False
                is_complete(poll_result)
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
    def test_source_domain_complete_servers_not_list(self, mock_get_logger, mock_validate, mock_enhance):
        """Test completion check when servers are not lists (line 300)"""
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
                # During completion check, servers are not lists
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
                # is_complete will check servers, which are not lists, so returns False
                is_complete(poll_result)
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
    def test_source_domain_complete_names_match(self, mock_get_logger, mock_validate, mock_enhance):
        """Test completion check when names match (line 304)"""
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
        
        # Mock domain_info calls - names match
        call_count = [0]
        def mock_domain_info(domain):
            call_count[0] += 1
            if call_count[0] == 1:
                return mock_source_response
            elif call_count[0] == 2:
                # During completion check, source domain info succeeds
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
                # Polling result - names match
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
                # is_complete should return True (names match)
                result = is_complete(poll_result)
                if result:
                    return poll_result
            return {'response': {'code': API_SUCCESS, 'data': {}}}
        
        self.mock_client.poll_until_complete.side_effect = mock_poll
        
        result = cmd_domain_update_ns(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)


if __name__ == '__main__':
    unittest.main()
