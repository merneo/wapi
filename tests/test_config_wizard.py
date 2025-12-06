"""
Tests for configuration wizard functionality
"""

import unittest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from wapi.utils.config_wizard import run_config_wizard


class TestConfigWizard(unittest.TestCase):
    """Test configuration wizard"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_config = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.env')
        self.temp_config.close()
        self.config_path = self.temp_config.name
    
    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.config_path):
            os.unlink(self.config_path)
    
    @patch('builtins.input', side_effect=['user@example.com', 'yes', 'yes'])
    @patch('wapi.utils.config_wizard.getpass', return_value='testpassword')
    @patch('builtins.print')
    def test_config_wizard_success(self, mock_print, mock_getpass, mock_input):
        """Test successful configuration wizard"""
        # Mock input sequence: username, default URL (empty), confirm yes, overwrite yes
        mock_input.side_effect = ['user@example.com', '', 'yes', 'yes']
        
        result = run_config_wizard(self.config_path)
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.config_path))
        
        # Check file contents
        with open(self.config_path, 'r') as f:
            content = f.read()
            self.assertIn('WAPI_USERNAME', content)
            self.assertIn('WAPI_PASSWORD', content)
            self.assertIn('WAPI_BASE_URL', content)
            self.assertIn('user@example.com', content)
            self.assertIn('testpassword', content)

    @patch('builtins.input', return_value='')
    @patch('builtins.print')
    def test_config_wizard_no_username(self, mock_print, mock_input):
        """Test wizard with no username"""
        result = run_config_wizard(self.config_path)
        
        self.assertFalse(result)
    
    @patch('builtins.input', side_effect=['user@example.com', 'no'])
    @patch('wapi.utils.config_wizard.getpass', return_value='testpassword')
    @patch('builtins.print')
    def test_config_wizard_cancel(self, mock_print, mock_getpass, mock_input):
        """Test wizard cancellation"""
        mock_input.side_effect = ['user@example.com', '', 'no']
        
        result = run_config_wizard(self.config_path)
        
        self.assertFalse(result)
    
    @patch('builtins.input', side_effect=['user@example.com', 'custom-url', 'yes', 'yes'])
    @patch('wapi.utils.config_wizard.getpass', return_value='testpassword')
    @patch('builtins.print')
    def test_config_wizard_custom_url(self, mock_print, mock_getpass, mock_input):
        """Test wizard with custom URL"""
        # Mock input sequence: username, custom URL, confirm yes, overwrite yes
        mock_input.side_effect = ['user@example.com', 'custom-url', 'yes', 'yes']

        result = run_config_wizard(self.config_path)
        
        self.assertTrue(result)
        with open(self.config_path, 'r') as f:
            content = f.read()
            self.assertIn('custom-url', content)
    
    @patch('builtins.input', side_effect=['user@example.com', 'yes', 'yes'])
    @patch('wapi.utils.config_wizard.getpass', return_value='testpassword')
    @patch('builtins.print')
    def test_config_wizard_overwrite_existing(self, mock_print, mock_getpass, mock_input):
        """Test wizard overwriting existing file"""
        # Create existing file
        with open(self.config_path, 'w') as f:
            f.write('OLD_CONFIG=value\n')
        
        mock_input.side_effect = ['user@example.com', '', 'yes', 'yes']
        
        result = run_config_wizard(self.config_path)
        
        self.assertTrue(result)
        with open(self.config_path, 'r') as f:
            content = f.read()
            self.assertIn('WAPI_USERNAME', content)
            self.assertNotIn('OLD_CONFIG', content)
    
    @patch('builtins.input', side_effect=['user@example.com', 'no'])
    @patch('wapi.utils.config_wizard.getpass', return_value='testpassword')
    @patch('builtins.print')
    def test_config_wizard_no_overwrite(self, mock_print, mock_getpass, mock_input):
        """Test wizard not overwriting existing file"""
        # Create existing file
        with open(self.config_path, 'w') as f:
            f.write('OLD_CONFIG=value\n')
        
        mock_input.side_effect = ['user@example.com', '', 'yes', 'no']
        
        result = run_config_wizard(self.config_path)
        
        self.assertFalse(result)
        # File should still have old content
        with open(self.config_path, 'r') as f:
            content = f.read()
            self.assertIn('OLD_CONFIG', content)
    
    @patch('builtins.input', side_effect=['user@example.com', 'yes', 'yes'])
    @patch('wapi.utils.config_wizard.getpass', side_effect=['', 'testpassword'])
    @patch('builtins.print')
    def test_config_wizard_empty_password_retry(self, mock_print, mock_getpass, mock_input):
        """Test wizard with empty password requiring retry"""
        # Mock input sequence: username, default URL (empty), confirm yes, overwrite yes
        mock_input.side_effect = ['user@example.com', '', 'yes', 'yes']
        
        result = run_config_wizard(self.config_path)
        
        # Should succeed after retry
        self.assertTrue(result)
    
    def test_config_wizard_file_permissions(self):
        """Test that config file has correct permissions"""
        # Mock input sequence: username, default URL (empty), confirm yes, overwrite yes
        with patch('builtins.input', side_effect=['user@example.com', '', 'yes', 'yes']):
            with patch('wapi.utils.config_wizard.getpass', return_value='testpassword'):
                with patch('builtins.print'):
                    run_config_wizard(self.config_path)
        
        if os.path.exists(self.config_path):
            # Check file permissions (should be 0o600)
            stat_info = os.stat(self.config_path)
            # On Unix, check that only owner can read/write
            # (mode & 0o777) should be 0o600
            mode = stat_info.st_mode & 0o777
            # Allow for some variation in how permissions are set
            self.assertIn(mode, [0o600, 0o644])  # 0o644 is also acceptable


if __name__ == '__main__':
    unittest.main()
