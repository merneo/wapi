"""
Tests for command aliases functionality
"""

import unittest

from wapi.utils.aliases import expand_alias, get_aliases, list_aliases


class TestAliases(unittest.TestCase):
    """Test alias functionality"""
    
    def test_expand_alias_domain_list(self):
        """Test expanding domain list alias"""
        result = expand_alias('dl')
        self.assertEqual(result, 'domain list')
    
    def test_expand_alias_domain_info(self):
        """Test expanding domain info alias"""
        result = expand_alias('di example.com')
        self.assertEqual(result, 'domain info example.com')
    
    def test_expand_alias_dns_records(self):
        """Test expanding DNS records alias"""
        result = expand_alias('dr example.com')
        self.assertEqual(result, 'dns records example.com')
    
    def test_expand_alias_nsset_info(self):
        """Test expanding NSSET info alias"""
        result = expand_alias('ni NS-EXAMPLE')
        self.assertEqual(result, 'nsset info NS-EXAMPLE')
    
    def test_expand_alias_auth_ping(self):
        """Test expanding auth ping alias"""
        result = expand_alias('p')
        self.assertEqual(result, 'auth ping')
    
    def test_expand_alias_auth_login(self):
        """Test expanding auth login alias"""
        result = expand_alias('l')
        self.assertEqual(result, 'auth login')
    
    def test_expand_alias_auth_logout(self):
        """Test expanding auth logout alias"""
        result = expand_alias('lo')
        self.assertEqual(result, 'auth logout')
    
    def test_expand_alias_config_show(self):
        """Test expanding config show alias"""
        result = expand_alias('cs')
        self.assertEqual(result, 'config show')
    
    def test_expand_alias_with_args(self):
        """Test expanding alias with arguments"""
        result = expand_alias('di example.com --format json')
        self.assertEqual(result, 'domain info example.com --format json')
    
    def test_expand_non_alias(self):
        """Test expanding non-alias command"""
        result = expand_alias('domain list')
        self.assertEqual(result, 'domain list')
    
    def test_expand_empty_string(self):
        """Test expanding empty string"""
        result = expand_alias('')
        self.assertEqual(result, '')
    
    def test_get_aliases(self):
        """Test getting all aliases"""
        aliases = get_aliases()
        self.assertIsInstance(aliases, dict)
        self.assertGreater(len(aliases), 0)
        self.assertIn('dl', aliases)
        self.assertIn('di', aliases)
        self.assertIn('p', aliases)
    
    def test_list_aliases(self):
        """Test listing aliases"""
        result = list_aliases()
        self.assertIsInstance(result, str)
        self.assertIn('dl', result)
        self.assertIn('domain list', result)
        self.assertIn('Available aliases', result)
    
    def test_all_aliases_expandable(self):
        """Test that all defined aliases can be expanded"""
        aliases = get_aliases()
        for alias in aliases.keys():
            result = expand_alias(alias)
            self.assertNotEqual(result, alias)  # Should be expanded
            self.assertIn(aliases[alias], result)  # Should contain full command


if __name__ == '__main__':
    unittest.main()
