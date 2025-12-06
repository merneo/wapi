"""
Tests for interactive mode (REPL) functionality
"""

import unittest
from unittest.mock import Mock, patch, MagicMock

from wapi.utils.interactive import WAPIInteractiveShell, start_interactive_mode
from wapi.api.client import WedosAPIClient


class TestWAPIInteractiveShell(unittest.TestCase):
    """Test interactive shell functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_client = Mock(spec=WedosAPIClient)
        self.shell = WAPIInteractiveShell(self.mock_client)
    
    def test_shell_initialization(self):
        """Test shell initialization"""
        self.assertEqual(self.shell.client, self.mock_client)
        self.assertTrue(self.shell.running)
        self.assertEqual(self.shell.command_history, [])
    
    def test_exit_command(self):
        """Test exit command"""
        with patch('builtins.input', return_value='exit'):
            self.shell.running = True
            self.shell._execute_command('exit')
            self.assertFalse(self.shell.running)
    
    def test_quit_command(self):
        """Test quit command"""
        with patch('builtins.input', return_value='quit'):
            self.shell.running = True
            self.shell._execute_command('quit')
            self.assertFalse(self.shell.running)
    
    def test_help_command(self):
        """Test help command"""
        with patch('builtins.print') as mock_print:
            self.shell._execute_command('help')
            mock_print.assert_called()
    
    def test_history_command_empty(self):
        """Test history command with empty history"""
        with patch('builtins.print') as mock_print:
            self.shell.command_history = []
            self.shell._execute_command('history')
            mock_print.assert_called()
    
    def test_history_command_with_commands(self):
        """Test history command with commands"""
        with patch('builtins.print') as mock_print:
            self.shell.command_history = ['ping', 'help', 'exit']
            self.shell._execute_command('history')
            mock_print.assert_called()
    
    def test_ping_command_success(self):
        """Test ping command with success"""
        self.mock_client.ping.return_value = {
            'response': {'code': '1000', 'result': 'OK'}
        }
        with patch('builtins.print') as mock_print:
            self.shell._execute_command('ping')
            mock_print.assert_called()
            self.mock_client.ping.assert_called_once()
    
    def test_ping_command_failure(self):
        """Test ping command with failure"""
        self.mock_client.ping.return_value = {
            'response': {'code': '1001', 'result': 'Error'}
        }
        with patch('builtins.print') as mock_print:
            self.shell._execute_command('ping')
            mock_print.assert_called()
            self.mock_client.ping.assert_called_once()
    
    def test_unknown_command(self):
        """Test unknown command handling"""
        with patch('builtins.print') as mock_print:
            self.shell._execute_command('unknown_command')
            # Should print error message
            mock_print.assert_called()
    
    def test_empty_command(self):
        """Test empty command handling"""
        # Empty command should not cause errors
        self.shell._execute_command('')
        # Should not raise exception
    
    def test_domain_command(self):
        """Test domain command"""
        with patch('builtins.print') as mock_print:
            self.shell._execute_command('domain list')
            mock_print.assert_called()
    
    def test_dns_command(self):
        """Test DNS command"""
        with patch('builtins.print') as mock_print:
            self.shell._execute_command('dns records example.com')
            mock_print.assert_called()
    
    def test_nsset_command(self):
        """Test NSSET command"""
        with patch('builtins.print') as mock_print:
            self.shell._execute_command('nsset info NS-EXAMPLE')
            mock_print.assert_called()
    
    def test_contact_command(self):
        """Test contact command"""
        with patch('builtins.print') as mock_print:
            self.shell._execute_command('contact info CONTACT-123')
            mock_print.assert_called()
    
    def test_config_command(self):
        """Test config command"""
        with patch('builtins.print') as mock_print:
            self.shell._execute_command('config show')
            mock_print.assert_called()
    
    def test_command_history_tracking(self):
        """Test that commands are added to history"""
        with patch('builtins.input', side_effect=['help', 'exit']):
            with patch('builtins.print'):
                self.shell.run()
                
        self.assertIn('help', self.shell.command_history)
        self.assertEqual(len(self.shell.command_history), 2)


class TestStartInteractiveMode(unittest.TestCase):
    """Test start_interactive_mode function"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_client = Mock(spec=WedosAPIClient)
    
    @patch('wapi.utils.interactive.WAPIInteractiveShell')
    def test_start_interactive_mode(self, mock_shell_class):
        """Test starting interactive mode"""
        mock_shell = Mock()
        mock_shell.run.return_value = 0
        mock_shell_class.return_value = mock_shell
        
        result = start_interactive_mode(self.mock_client)
        
        mock_shell_class.assert_called_once_with(self.mock_client)
        mock_shell.run.assert_called_once()
        self.assertEqual(result, 0)
    
    @patch('wapi.utils.interactive.WAPIInteractiveShell')
    def test_start_interactive_mode_error(self, mock_shell_class):
        """Test interactive mode with error"""
        mock_shell = Mock()
        mock_shell.run.return_value = 1
        mock_shell_class.return_value = mock_shell
        
        result = start_interactive_mode(self.mock_client)
        
        self.assertEqual(result, 1)


if __name__ == '__main__':
    unittest.main()
