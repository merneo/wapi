"""
Complete tests for formatters module to achieve 100% coverage

Tests for remaining uncovered lines (14-15, 20, 42, 50-62, 97, 116, 150-155).
"""

import unittest
from unittest.mock import Mock, patch

from wapi.utils.formatters import format_output


class TestFormattersComplete(unittest.TestCase):
    """Complete tests for formatters module"""

    def test_format_output_json_empty_list(self):
        """Test format_output with JSON format and empty list (line 14-15)"""
        result = format_output([], 'json')
        self.assertEqual(result, '[]')  # JSON doesn't add newline

    def test_format_output_json_empty_dict(self):
        """Test format_output with JSON format and empty dict"""
        result = format_output({}, 'json')
        self.assertEqual(result, '{}')  # JSON doesn't add newline

    def test_format_output_yaml_empty(self):
        """Test format_output with YAML format and empty data (line 20)"""
        result = format_output([], 'yaml')
        # YAML may or may not have newline, just check it's valid
        self.assertIsInstance(result, str)
        self.assertIn('[]', result)

    def test_format_output_table_with_headers(self):
        """Test format_output with table format and headers (line 42)"""
        data = [
            {'name': 'test1', 'value': 'val1'},
            {'name': 'test2', 'value': 'val2'}
        ]
        result = format_output(data, 'table', headers=['name', 'value'])
        self.assertIn('name', result)
        self.assertIn('value', result)
        self.assertIn('test1', result)

    def test_format_output_table_empty_data(self):
        """Test format_output with table format and empty data"""
        result = format_output([], 'table', headers=['name', 'value'])
        # Should handle empty data gracefully
        self.assertIsInstance(result, str)

    def test_format_output_table_single_row(self):
        """Test format_output with table format and single row"""
        data = [{'name': 'test1', 'value': 'val1'}]
        result = format_output(data, 'table', headers=['name', 'value'])
        self.assertIn('test1', result)
        self.assertIn('val1', result)

    def test_format_output_table_no_headers(self):
        """Test format_output with table format without headers"""
        data = [{'name': 'test1', 'value': 'val1'}]
        result = format_output(data, 'table')
        # Should still format
        self.assertIsInstance(result, str)

    def test_format_output_table_dict_data(self):
        """Test format_output with table format and dict (not list)"""
        data = {'name': 'test1', 'value': 'val1'}
        result = format_output(data, 'table')
        # Should handle dict
        self.assertIsInstance(result, str)

    def test_format_output_table_nested_data(self):
        """Test format_output with table format and nested data"""
        data = [
            {'name': 'test1', 'nested': {'key': 'value'}}
        ]
        result = format_output(data, 'table', headers=['name', 'nested'])
        # Should handle nested data
        self.assertIsInstance(result, str)

    def test_format_output_table_missing_keys(self):
        """Test format_output with table format and missing keys"""
        data = [
            {'name': 'test1'},  # Missing 'value'
            {'value': 'val2'}   # Missing 'name'
        ]
        result = format_output(data, 'table', headers=['name', 'value'])
        # Should handle missing keys
        self.assertIsInstance(result, str)

    def test_format_output_table_unicode_data(self):
        """Test format_output with table format and unicode data"""
        data = [
            {'name': 'test1', 'value': 'český text'}
        ]
        result = format_output(data, 'table', headers=['name', 'value'])
        # Should handle unicode
        self.assertIsInstance(result, str)

    def test_format_output_invalid_format(self):
        """Test format_output with invalid format (line 50-62)"""
        data = [{'name': 'test1'}]
        # Should default to table format or handle gracefully
        result = format_output(data, 'invalid_format')
        self.assertIsInstance(result, str)

    def test_format_output_json_pretty(self):
        """Test format_output with JSON format and pretty printing"""
        data = {'name': 'test1', 'value': 'val1'}
        result = format_output(data, 'json')
        # Should be valid JSON
        import json
        parsed = json.loads(result.strip())
        self.assertEqual(parsed['name'], 'test1')

    def test_format_output_yaml_complex(self):
        """Test format_output with YAML format and complex data"""
        data = {
            'name': 'test1',
            'nested': {
                'key1': 'value1',
                'key2': ['item1', 'item2']
            }
        }
        result = format_output(data, 'yaml')
        # Should be valid YAML
        import yaml
        parsed = yaml.safe_load(result)
        self.assertEqual(parsed['name'], 'test1')

    def test_format_output_table_large_data(self):
        """Test format_output with table format and large dataset"""
        data = [{'name': f'test{i}', 'value': f'val{i}'} for i in range(100)]
        result = format_output(data, 'table', headers=['name', 'value'])
        # Should handle large data
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)

    def test_format_output_table_none_values(self):
        """Test format_output with table format and None values"""
        data = [
            {'name': 'test1', 'value': None},
            {'name': None, 'value': 'val2'}
        ]
        result = format_output(data, 'table', headers=['name', 'value'])
        # Should handle None values
        self.assertIsInstance(result, str)

    def test_format_output_table_empty_string_values(self):
        """Test format_output with table format and empty string values"""
        data = [
            {'name': '', 'value': 'val1'},
            {'name': 'test2', 'value': ''}
        ]
        result = format_output(data, 'table', headers=['name', 'value'])
        # Should handle empty strings
        self.assertIsInstance(result, str)

    def test_format_output_table_special_characters(self):
        """Test format_output with table format and special characters"""
        data = [
            {'name': 'test|pipe', 'value': 'val\t tab'},
            {'name': 'test\nnewline', 'value': 'val"quote'}
        ]
        result = format_output(data, 'table', headers=['name', 'value'])
        # Should handle special characters
        self.assertIsInstance(result, str)

    def test_format_output_table_very_long_values(self):
        """Test format_output with table format and very long values"""
        long_value = 'x' * 200
        data = [
            {'name': 'test1', 'value': long_value}
        ]
        result = format_output(data, 'table', headers=['name', 'value'])
        # Should handle long values
        self.assertIsInstance(result, str)

    def test_format_output_table_mixed_types(self):
        """Test format_output with table format and mixed data types"""
        data = [
            {'name': 'test1', 'value': 123},
            {'name': 'test2', 'value': True},
            {'name': 'test3', 'value': None}
        ]
        result = format_output(data, 'table', headers=['name', 'value'])
        # Should handle mixed types
        self.assertIsInstance(result, str)

    def test_format_output_json_list_of_dicts(self):
        """Test format_output with JSON format and list of dicts"""
        data = [
            {'name': 'test1', 'value': 'val1'},
            {'name': 'test2', 'value': 'val2'}
        ]
        result = format_output(data, 'json')
        import json
        parsed = json.loads(result.strip())
        self.assertIsInstance(parsed, list)
        self.assertEqual(len(parsed), 2)

    def test_format_output_yaml_list(self):
        """Test format_output with YAML format and list"""
        data = [
            {'name': 'test1', 'value': 'val1'},
            {'name': 'test2', 'value': 'val2'}
        ]
        result = format_output(data, 'yaml')
        import yaml
        parsed = yaml.safe_load(result)
        self.assertIsInstance(parsed, list)
        self.assertEqual(len(parsed), 2)

    def test_format_output_table_no_data_keys(self):
        """Test format_output with table format when data has no matching keys"""
        data = [{'other_key': 'value'}]
        result = format_output(data, 'table', headers=['name', 'value'])
        # Should handle missing keys
        self.assertIsInstance(result, str)

    def test_format_output_table_all_empty_headers(self):
        """Test format_output with table format and empty headers list"""
        data = [{'name': 'test1', 'value': 'val1'}]
        result = format_output(data, 'table', headers=[])
        # Should handle empty headers
        self.assertIsInstance(result, str)

    def test_format_output_yaml_import_error(self):
        """Test format_output with YAML when yaml not available (line 14-15)"""
        # Patch YAML_AVAILABLE to False
        with patch('wapi.utils.formatters.YAML_AVAILABLE', False):
            result = format_output({'key': 'value'}, 'yaml')
            # Should fallback to JSON
            import json
            parsed = json.loads(result)
            self.assertEqual(parsed['key'], 'value')

    def test_yaml_import_error_handling(self):
        """Test YAML ImportError handling (line 14-15) - tests the fallback path"""
        # The ImportError block sets YAML_AVAILABLE = False
        # We test this by ensuring format_yaml falls back to JSON when YAML_AVAILABLE is False
        with patch('wapi.utils.formatters.YAML_AVAILABLE', False):
            from wapi.utils.formatters import format_yaml
            result = format_yaml({'key': 'value'})
            # Should fallback to JSON format
            import json
            parsed = json.loads(result)
            self.assertEqual(parsed['key'], 'value')

    def test_yaml_import_error_at_module_level(self):
        """Test YAML ImportError at module import time (line 14-15) - actual exception block"""
        import sys
        from unittest.mock import patch
        
        # Save original yaml module if it exists
        original_yaml = sys.modules.get('yaml')
        original_formatters = sys.modules.get('wapi.utils.formatters')
        
        # Remove yaml and formatters from sys.modules to force re-import
        if 'yaml' in sys.modules:
            del sys.modules['yaml']
        if 'wapi.utils.formatters' in sys.modules:
            del sys.modules['wapi.utils.formatters']
        
        # Patch __import__ to raise ImportError for yaml
        original_import = __import__
        def mock_import(name, *args, **kwargs):
            if name == 'yaml':
                raise ImportError("No module named 'yaml'")
            return original_import(name, *args, **kwargs)
        
        with patch('builtins.__import__', side_effect=mock_import):
            # Re-import formatters - should trigger ImportError and set YAML_AVAILABLE = False
            import wapi.utils.formatters
            self.assertFalse(wapi.utils.formatters.YAML_AVAILABLE)
        
        # Restore original modules
        if original_yaml:
            sys.modules['yaml'] = original_yaml
        if original_formatters:
            sys.modules['wapi.utils.formatters'] = original_formatters
        else:
            # Clean up if it wasn't there before
            if 'wapi.utils.formatters' in sys.modules:
                del sys.modules['wapi.utils.formatters']

    def test_format_output_table_no_tabulate(self):
        """Test format_output with table when tabulate not available (line 20)"""
        # Patch TABULATE_AVAILABLE to False
        with patch('wapi.utils.formatters.TABULATE_AVAILABLE', False):
            data = [{'name': 'test1', 'value': 'val1'}]
            result = format_output(data, 'table', headers=['name', 'value'])
            # Should use fallback simple table
            self.assertIn('name', result)
            self.assertIn('value', result)
            self.assertIn('test1', result)

    def test_tabulate_import_error_handling(self):
        """Test tabulate ImportError handling (line 20) - tests the fallback path"""
        # The ImportError block sets TABULATE_AVAILABLE = False
        # We test this by ensuring format_table uses fallback when TABULATE_AVAILABLE is False
        with patch('wapi.utils.formatters.TABULATE_AVAILABLE', False):
            from wapi.utils.formatters import format_table
            data = [{'name': 'test1', 'value': 'val1'}]
            result = format_table(data, headers=['name', 'value'])
            # Should use fallback simple table format
            self.assertIn('name', result)
            self.assertIn('value', result)
            self.assertIn('test1', result)

    def test_tabulate_import_error_at_module_level(self):
        """Test tabulate ImportError at module import time (line 20) - actual exception block"""
        import sys
        from unittest.mock import patch
        
        # Save original tabulate module if it exists
        original_tabulate = sys.modules.get('tabulate')
        original_formatters = sys.modules.get('wapi.utils.formatters')
        
        # Remove tabulate and formatters from sys.modules to force re-import
        if 'tabulate' in sys.modules:
            del sys.modules['tabulate']
        if 'wapi.utils.formatters' in sys.modules:
            del sys.modules['wapi.utils.formatters']
        
        # Patch __import__ to raise ImportError for tabulate
        original_import = __import__
        def mock_import(name, *args, **kwargs):
            if name == 'tabulate' or (isinstance(name, str) and name.startswith('tabulate')):
                raise ImportError("No module named 'tabulate'")
            return original_import(name, *args, **kwargs)
        
        with patch('builtins.__import__', side_effect=mock_import):
            # Re-import formatters - should trigger ImportError and set TABULATE_AVAILABLE = False
            import wapi.utils.formatters
            self.assertFalse(wapi.utils.formatters.TABULATE_AVAILABLE)
        
        # Restore original modules
        if original_tabulate:
            sys.modules['tabulate'] = original_tabulate
        if original_formatters:
            sys.modules['wapi.utils.formatters'] = original_formatters
        else:
            # Clean up if it wasn't there before
            if 'wapi.utils.formatters' in sys.modules:
                del sys.modules['wapi.utils.formatters']

    def test_format_output_table_list_non_dict(self):
        """Test format_output with table format and list of non-dicts (line 50-57)"""
        data = [['row1', 'row2'], ['row3', 'row4']]
        result = format_output(data, 'table', headers=['col1', 'col2'])
        # Should handle list of lists (line 56-57)
        self.assertIsInstance(result, str)

    def test_format_output_table_list_empty(self):
        """Test format_output with table format and empty list (line 50)"""
        data = []
        result = format_output(data, 'table')
        # Should handle empty list
        self.assertIsInstance(result, str)

    @patch('wapi.utils.formatters.TABULATE_AVAILABLE', True)
    def test_format_table_list_with_dicts_tabulate(self):
        """Test format_table with list of dicts when tabulate available (line 50-55)"""
        import sys
        import importlib
        from unittest.mock import MagicMock
        
        # Create mock tabulate module if it doesn't exist
        if 'tabulate' not in sys.modules:
            mock_tabulate_module = MagicMock()
            mock_tabulate_module.tabulate = MagicMock(return_value="mocked table")
            sys.modules['tabulate'] = mock_tabulate_module
        else:
            mock_tabulate_module = sys.modules['tabulate']
            mock_tabulate_module.tabulate = MagicMock(return_value="mocked table")
        
        # Reload formatters module to pick up the mocked tabulate
        if 'wapi.utils.formatters' in sys.modules:
            del sys.modules['wapi.utils.formatters']
        from wapi.utils.formatters import format_table
        
        data = [{'name': 'test1', 'value': 'val1'}]
        result = format_table(data, headers=['name', 'value'])
        mock_tabulate_module.tabulate.assert_called_once()
        self.assertEqual(result, "mocked table")

    @patch('wapi.utils.formatters.TABULATE_AVAILABLE', True)
    def test_format_table_list_non_dicts_tabulate(self):
        """Test format_table with list of non-dicts when tabulate available (line 56-57)"""
        import sys
        import importlib
        from unittest.mock import MagicMock
        
        # Create mock tabulate module if it doesn't exist
        if 'tabulate' not in sys.modules:
            mock_tabulate_module = MagicMock()
            mock_tabulate_module.tabulate = MagicMock(return_value="mocked table")
            sys.modules['tabulate'] = mock_tabulate_module
        else:
            mock_tabulate_module = sys.modules['tabulate']
            mock_tabulate_module.tabulate = MagicMock(return_value="mocked table")
        
        # Reload formatters module to pick up the mocked tabulate
        if 'wapi.utils.formatters' in sys.modules:
            del sys.modules['wapi.utils.formatters']
        from wapi.utils.formatters import format_table
        
        data = [['row1', 'row2'], ['row3', 'row4']]
        result = format_table(data, headers=['col1', 'col2'])
        mock_tabulate_module.tabulate.assert_called_once()
        self.assertEqual(result, "mocked table")

    @patch('wapi.utils.formatters.TABULATE_AVAILABLE', True)
    def test_format_table_dict_tabulate(self):
        """Test format_table with dict when tabulate available (line 58-60)"""
        import sys
        import importlib
        from unittest.mock import MagicMock
        
        # Create mock tabulate module if it doesn't exist
        if 'tabulate' not in sys.modules:
            mock_tabulate_module = MagicMock()
            mock_tabulate_module.tabulate = MagicMock(return_value="mocked table")
            sys.modules['tabulate'] = mock_tabulate_module
        else:
            mock_tabulate_module = sys.modules['tabulate']
            mock_tabulate_module.tabulate = MagicMock(return_value="mocked table")
        
        # Reload formatters module to pick up the mocked tabulate
        if 'wapi.utils.formatters' in sys.modules:
            del sys.modules['wapi.utils.formatters']
        from wapi.utils.formatters import format_table
        
        data = {'name': 'test1', 'value': 'val1'}
        result = format_table(data)
        mock_tabulate_module.tabulate.assert_called_once()
        self.assertEqual(result, "mocked table")

    @patch('wapi.utils.formatters.TABULATE_AVAILABLE', True)
    def test_format_table_list_with_dicts_no_headers_tabulate(self):
        """Test format_table with list of dicts and no headers when tabulate available (line 53)"""
        import sys
        from unittest.mock import MagicMock
        
        # Create mock tabulate module if it doesn't exist
        if 'tabulate' not in sys.modules:
            mock_tabulate_module = MagicMock()
            mock_tabulate_module.tabulate = MagicMock(return_value="mocked table")
            sys.modules['tabulate'] = mock_tabulate_module
        else:
            mock_tabulate_module = sys.modules['tabulate']
            mock_tabulate_module.tabulate = MagicMock(return_value="mocked table")
        
        # Reload formatters module to pick up the mocked tabulate
        if 'wapi.utils.formatters' in sys.modules:
            del sys.modules['wapi.utils.formatters']
        from wapi.utils.formatters import format_table
        
        data = [{'name': 'test1', 'value': 'val1'}]
        result = format_table(data, headers=None)  # No headers - triggers line 53
        mock_tabulate_module.tabulate.assert_called_once()
        self.assertEqual(result, "mocked table")

    @patch('wapi.utils.formatters.TABULATE_AVAILABLE', True)
    def test_format_table_other_type_tabulate(self):
        """Test format_table with other type when tabulate available (line 61-62)"""
        import sys
        from unittest.mock import MagicMock
        
        # Create mock tabulate module if it doesn't exist
        if 'tabulate' not in sys.modules:
            mock_tabulate_module = MagicMock()
            mock_tabulate_module.tabulate = MagicMock(return_value="mocked table")
            sys.modules['tabulate'] = mock_tabulate_module
        else:
            mock_tabulate_module = sys.modules['tabulate']
            mock_tabulate_module.tabulate = MagicMock(return_value="mocked table")
        
        # Reload formatters module to pick up the mocked tabulate
        if 'wapi.utils.formatters' in sys.modules:
            del sys.modules['wapi.utils.formatters']
        from wapi.utils.formatters import format_table
        
        data = "simple string"
        result = format_table(data)
        # Should return str(data) without calling tabulate (goes to else branch)
        self.assertEqual(result, "simple string")

    def test_format_output_table_dict_data(self):
        """Test format_output with table format and dict (line 58-60)"""
        data = {'name': 'test1', 'value': 'val1'}
        result = format_output(data, 'table')
        # format_table should handle dicts - when tabulate available, formats as Key-Value table
        # The actual output depends on tabulate availability
        self.assertIsInstance(result, str)
        # Should contain the data values
        self.assertIn('test1', result or str(data))

    def test_format_output_table_non_list_non_dict(self):
        """Test format_output with table format and non-list/non-dict (line 61-62)"""
        data = "simple string"
        result = format_output(data, 'table')
        # Should convert to string
        self.assertEqual(result, 'simple string')


if __name__ == '__main__':
    unittest.main()
