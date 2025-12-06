"""
Tests to achieve 100% coverage for formatters module

Tests for remaining uncovered lines (14-15, 20, 42, 50-62, 97, 116, 150-155).
"""

import unittest
from unittest.mock import patch, Mock
import sys

from wapi.utils.formatters import format_output, format_table, format_xml, format_yaml


class TestFormatters100(unittest.TestCase):
    """Tests for 100% formatters coverage"""

    @patch('wapi.utils.formatters.YAML_AVAILABLE', False)
    def test_format_yaml_fallback_to_json(self):
        """Test format_yaml fallback to JSON when yaml not available (line 116)"""
        data = {'name': 'test'}
        result = format_yaml(data)
        # Should return JSON format
        import json
        parsed = json.loads(result)
        self.assertEqual(parsed['name'], 'test')

    @patch('wapi.utils.formatters.TABULATE_AVAILABLE', False)
    def test_format_table_fallback_no_headers_from_data(self):
        """Test format_table fallback extracts headers from data (line 42)"""
        data = [{'name': 'test1', 'value': 'val1'}]
        result = format_table(data)
        # Should extract headers from first dict
        self.assertIn('name', result)
        self.assertIn('value', result)

    @patch('wapi.utils.formatters.TABULATE_AVAILABLE', False)
    def test_format_table_fallback_list_non_dict(self):
        """Test format_table fallback with list of non-dict items"""
        data = ['item1', 'item2']
        result = format_table(data)
        # Should return str(data)
        self.assertIsInstance(result, str)

    def test_format_table_list_non_dict_items(self):
        """Test format_table with list of non-dict items (line 50-62)"""
        data = ['item1', 'item2', 'item3']
        result = format_table(data)
        # Should handle list of strings
        self.assertIsInstance(result, str)

    def test_format_table_list_empty(self):
        """Test format_table with empty list"""
        data = []
        result = format_table(data)
        # Should handle empty list
        self.assertIsInstance(result, str)

    def test_format_xml_dict_with_list_value(self):
        """Test format_xml with dict containing list value (line 97)"""
        data = {
            'name': 'test',
            'items': ['item1', 'item2']  # List value triggers line 97
        }
        result = format_xml(data)
        # Should show ... for list values
        self.assertIn('items', result)
        self.assertIn('...', result)

    def test_format_xml_dict_with_dict_value(self):
        """Test format_xml with dict containing nested dict value (line 97)"""
        data = {
            'name': 'test',
            'nested': {'key': 'value'}  # Nested dict triggers line 97
        }
        result = format_xml(data)
        # Should show ... for nested dict
        self.assertIn('nested', result)
        self.assertIn('...', result)

    def test_format_output_value_error(self):
        """Test format_output with ValueError (line 150-155)"""
        # Create data that causes ValueError in JSON
        class Unserializable:
            def __repr__(self):
                return "Unserializable()"
        
        data = {'key': Unserializable()}
        
        with self.assertRaises((ValueError, TypeError)):
            format_output(data, 'json')

    def test_format_output_type_error(self):
        """Test format_output with TypeError"""
        # Create data that causes TypeError
        data = object()
        
        with self.assertRaises((ValueError, TypeError)):
            format_output(data, 'json')

    def test_format_output_key_error(self):
        """Test format_output with KeyError (should not happen but test edge case)"""
        # Normal data should not raise KeyError
        data = [{'name': 'test'}]
        result = format_output(data, 'table', headers=['name', 'missing'])
        # Should handle missing keys gracefully
        self.assertIsInstance(result, str)

    def test_format_output_unexpected_exception(self):
        """Test format_output with unexpected Exception (line 150-155)"""
        # Mock formatter to raise unexpected exception
        with patch('wapi.utils.formatters.format_json', side_effect=Exception("Unexpected")):
            data = {'name': 'test'}
            with self.assertRaises(Exception):
                format_output(data, 'json')

    def test_format_table_dict_formatting(self):
        """Test format_table with dict (not list)"""
        data = {'name': 'test1', 'value': 'val1'}
        result = format_table(data)
        # Should format as Key-Value table
        self.assertIsInstance(result, str)
        self.assertIn('test1', result)

    def test_format_table_non_list_non_dict(self):
        """Test format_table with non-list, non-dict data"""
        data = "string data"
        result = format_table(data)
        # Should return str(data)
        self.assertEqual(result, "string data")


if __name__ == '__main__':
    unittest.main()
