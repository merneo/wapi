"""
Unit tests for WAPI formatters

Tests output formatting functions for table, JSON, XML, YAML formats.
"""

import unittest
import json
import yaml
from wapi.utils.formatters import format_output


class TestTableFormatter(unittest.TestCase):
    """Test table format output"""
    
    def test_simple_list(self):
        """Test formatting simple list"""
        data = [
            {'name': 'example.com', 'status': 'ok'},
            {'name': 'test.com', 'status': 'active'}
        ]
        result = format_output(data, 'table', headers=['name', 'status'])
        self.assertIn('example.com', result)
        self.assertIn('test.com', result)
        self.assertIn('ok', result)
    
    def test_simple_dict(self):
        """Test formatting simple dictionary"""
        data = {'name': 'example.com', 'status': 'ok'}
        result = format_output(data, 'table')
        self.assertIn('example.com', result)
        self.assertIn('ok', result)


class TestJSONFormatter(unittest.TestCase):
    """Test JSON format output"""
    
    def test_simple_list(self):
        """Test formatting simple list to JSON"""
        data = [
            {'name': 'example.com', 'status': 'ok'},
            {'name': 'test.com', 'status': 'active'}
        ]
        result = format_output(data, 'json')
        parsed = json.loads(result)
        self.assertEqual(len(parsed), 2)
        self.assertEqual(parsed[0]['name'], 'example.com')
    
    def test_simple_dict(self):
        """Test formatting simple dictionary to JSON"""
        data = {'name': 'example.com', 'status': 'ok'}
        result = format_output(data, 'json')
        parsed = json.loads(result)
        self.assertEqual(parsed['name'], 'example.com')
        self.assertEqual(parsed['status'], 'ok')


class TestYAMLFormatter(unittest.TestCase):
    """Test YAML format output"""
    
    def test_simple_list(self):
        """Test formatting simple list to YAML"""
        data = [
            {'name': 'example.com', 'status': 'ok'},
            {'name': 'test.com', 'status': 'active'}
        ]
        result = format_output(data, 'yaml')
        parsed = yaml.safe_load(result)
        self.assertEqual(len(parsed), 2)
        self.assertEqual(parsed[0]['name'], 'example.com')
    
    def test_simple_dict(self):
        """Test formatting simple dictionary to YAML"""
        data = {'name': 'example.com', 'status': 'ok'}
        result = format_output(data, 'yaml')
        parsed = yaml.safe_load(result)
        self.assertEqual(parsed['name'], 'example.com')
        self.assertEqual(parsed['status'], 'ok')


class TestXMLFormatter(unittest.TestCase):
    """Test XML format output"""
    
    def test_simple_list(self):
        """Test formatting simple list to XML"""
        data = [
            {'name': 'example.com', 'status': 'ok'},
            {'name': 'test.com', 'status': 'active'}
        ]
        result = format_output(data, 'xml')
        # XML formatter may format lists differently - just check it contains data
        self.assertIn('example.com', result)
        self.assertIn('test.com', result)
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)
    
    def test_simple_dict(self):
        """Test formatting simple dictionary to XML"""
        data = {'name': 'example.com', 'status': 'ok'}
        result = format_output(data, 'xml')
        self.assertIn('example.com', result)
        self.assertIn('ok', result)


if __name__ == '__main__':
    unittest.main()
