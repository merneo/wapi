"""                                                                                                         
Complete tests for CLI module to achieve 100% coverage                                                                         
                                                                                                                               
Tests for remaining uncovered lines (51-54, 70-90, 287, 294-297, 308-310, 320-322, 324-326, 328-330, 340-341).                 
"""                                                                                                                            
                                                                                                                               
import unittest                                                                                                                
from unittest.mock import Mock, patch, MagicMock                                                                               
import sys                                                                                                                     
                                                                                                                               
from wapi.cli import main                                                                                                      
from wapi.constants import EXIT_SUCCESS, EXIT_ERROR, EXIT_CONFIG_ERROR                                                         
from wapi.exceptions import WAPIConfigurationError, WAPIAuthenticationError                                                    
                                                                                                                               
                                                                                                                               
class TestCLIComplete(unittest.TestCase):                                                                                      
    """Complete tests for CLI module"""                                                                                        
                                                                                                                               
    def setUp(self):                                                                                                           
        """Set up test fixtures"""                                                                                             
        self.original_argv = sys.argv.copy()                                                                                   
                                                                                                                               
    def tearDown(self):                                                                                                        
        """Clean up"""                                                                                                         
        sys.argv = self.original_argv                                                                                          
                                                                                                                               
    @patch('wapi.cli.argparse.ArgumentParser')                                                                                 
    def test_main_parse_args_error(self, mock_parser_class):                                                                   
        """Test main with argument parsing error (line 51-54)"""                                                               
        mock_parser = Mock()                                                                                                   
        mock_parser.parse_args.side_effect = SystemExit(2)                                                                     
        mock_parser_class.return_value = mock_parser                                                                           
                                                                                                                               
        with self.assertRaises(SystemExit):                                                                                    
            main()                                                                                                             
                                                                                                                               
    @patch('wapi.cli.get_client')
    @patch('wapi.cli.argparse.ArgumentParser')
    @patch('wapi.cli.run_config_wizard')
    def test_main_config_error(self, mock_run_wizard, mock_parser_class, mock_get_client):
        """Test main with config error (line 70-90)"""
        mock_parser = Mock()
        mock_args = Mock()
        mock_args.func = Mock()
        mock_args.wizard = False
        mock_args.interactive = False
        mock_args.aliases = False
        mock_args.search_domain = None
        mock_parser.parse_args.return_value = mock_args
        mock_parser_class.return_value = mock_parser
        
        mock_run_wizard.return_value = False

        mock_get_client.side_effect = WAPIConfigurationError("Config error")

        result = main()

        self.assertEqual(result, EXIT_CONFIG_ERROR)

    @patch('wapi.cli.get_client')
    @patch('wapi.cli.argparse.ArgumentParser')
    @patch('wapi.cli.run_config_wizard')
    def test_main_auth_error(self, mock_run_wizard, mock_parser_class, mock_get_client):
        """Test main with authentication error"""
        mock_parser = Mock()
        mock_args = Mock()
        mock_func = Mock(side_effect=WAPIAuthenticationError("Auth error"))
        mock_args.func = mock_func
        mock_args.module = 'test'  # Ensure module is set
        mock_args.config = 'config.env'
        mock_args.wizard = False
        mock_args.interactive = False
        mock_args.aliases = False
        mock_args.search_domain = None
        mock_parser.parse_args.return_value = mock_args
        mock_parser_class.return_value = mock_parser
        
        mock_run_wizard.return_value = False

        mock_client = Mock()
        mock_get_client.return_value = mock_client

        result = main()

        from wapi.constants import EXIT_AUTH_ERROR
        self.assertEqual(result, EXIT_AUTH_ERROR)

    @patch('wapi.cli.get_client')
    @patch('wapi.cli.argparse.ArgumentParser')
    @patch('wapi.cli.run_config_wizard')
    def test_main_command_execution_success(self, mock_run_wizard, mock_parser_class, mock_get_client):
        """Test main with successful command execution"""
        mock_parser = Mock()
        mock_args = Mock()
        mock_func = Mock(return_value=EXIT_SUCCESS)
        mock_args.func = mock_func
        mock_args.wizard = False
        mock_args.interactive = False
        mock_args.aliases = False
        mock_args.search_domain = None
        mock_parser.parse_args.return_value = mock_args
        mock_parser_class.return_value = mock_parser

        mock_client = Mock()
        mock_get_client.return_value = mock_client
        
        result = main()

        self.assertEqual(result, EXIT_SUCCESS)
        mock_func.assert_called_once()

    @patch('wapi.cli.get_client')
    @patch('wapi.cli.argparse.ArgumentParser')
    @patch('wapi.cli.run_config_wizard')
    def test_main_command_execution_error(self, mock_run_wizard, mock_parser_class, mock_get_client):
        """Test main with command execution error"""
        mock_parser = Mock()
        mock_args = Mock()
        mock_func = Mock(return_value=EXIT_ERROR)
        mock_args.func = mock_func
        mock_args.wizard = False
        mock_args.interactive = False
        mock_args.aliases = False
        mock_args.search_domain = None
        mock_parser.parse_args.return_value = mock_args
        mock_parser_class.return_value = mock_parser

        mock_client = Mock()
        mock_get_client.return_value = mock_client
        
        result = main()

        self.assertEqual(result, EXIT_ERROR)

    @patch('wapi.cli.get_client')
    @patch('wapi.cli.argparse.ArgumentParser')
    @patch('wapi.cli.run_config_wizard')
    def test_main_keyboard_interrupt(self, mock_run_wizard, mock_parser_class, mock_get_client):
        """Test main with keyboard interrupt"""
        mock_parser = Mock()
        mock_args = Mock()
        mock_func = Mock(side_effect=KeyboardInterrupt())
        mock_args.func = mock_func
        mock_args.wizard = False
        mock_args.interactive = False
        mock_args.aliases = False
        mock_args.search_domain = None
        mock_parser.parse_args.return_value = mock_args
        mock_parser_class.return_value = mock_parser

        mock_client = Mock()
        mock_get_client.return_value = mock_client

        result = main()

        from wapi.constants import EXIT_ERROR
        self.assertEqual(result, EXIT_ERROR)

    @patch('wapi.cli.get_client')
    @patch('wapi.cli.argparse.ArgumentParser')
    @patch('wapi.cli.run_config_wizard')
    def test_main_generic_exception(self, mock_run_wizard, mock_parser_class, mock_get_client):
        """Test main with generic exception"""
        mock_parser = Mock()
        mock_args = Mock()
        mock_func = Mock(side_effect=Exception("Generic error"))
        mock_args.func = mock_func
        mock_args.wizard = False
        mock_args.interactive = False
        mock_args.aliases = False
        mock_args.search_domain = None
        mock_parser.parse_args.return_value = mock_args
        mock_parser_class.return_value = mock_parser

        mock_client = Mock()
        mock_get_client.return_value = mock_client

        result = main()

        self.assertEqual(result, EXIT_ERROR)

    @patch('wapi.cli.argparse.ArgumentParser')
    def test_main_config_command_no_client(self, mock_parser_class):
        """Test main with config command that doesn't need client"""
        from wapi.commands.config import cmd_config_show
        
        mock_parser = Mock()
        mock_args = Mock()
        mock_args.func = cmd_config_show
        mock_args.config = 'config.env'
        mock_args.format = 'table'
        mock_args.wizard = False
        mock_args.interactive = False
        mock_args.aliases = False
        mock_args.search_domain = None
        mock_parser.parse_args.return_value = mock_args
        mock_parser_class.return_value = mock_parser
        
        with patch('wapi.cli.load_config', return_value={'WAPI_USERNAME': 'test'}):
            with patch('wapi.cli.format_output'):
                result = main()
                self.assertEqual(result, EXIT_SUCCESS)
                                                                                                                               
    @patch('wapi.cli.validate_config')                                                                                         
    @patch('wapi.cli.get_config')                                                                                              
    @patch('wapi.cli.WedosAPIClient')                                                                                          
    def test_get_client_config_validation_exception(self, mock_client_class, mock_get_config, mock_validate_config):           
        """Test get_client with exception in validate_config (lines 51-54)"""                                                  
        from wapi.cli import get_client                                                                                        
                                                                                                                               
        mock_validate_config.side_effect = Exception("Validation error")                                                       
                                                                                                                               
        result = get_client('config.env')                                                                                      
                                                                                                                               
        self.assertIsNone(result)                                                                                              
                                                                                                                               
    @patch('wapi.cli.validate_config')                                                                                         
    @patch('wapi.cli.get_config')                                                                                              
    @patch('wapi.cli.WedosAPIClient')                                                                                          
    def test_get_client_config_validation_failed(self, mock_client_class, mock_get_config, mock_validate_config):              
        """Test get_client with failed validation (lines 48-50)"""                                                             
        from wapi.cli import get_client                                                                                        
                                                                                                                               
        mock_validate_config.return_value = (False, "Invalid config")                                                          
                                                                                                                               
        result = get_client('config.env')                                                                                      
                                                                                                                               
        self.assertIsNone(result)                                                                                              
                                                                                                                               
    @patch('wapi.cli.validate_config')                                                                                         
    @patch('wapi.cli.get_config')                                                                                              
    @patch('wapi.cli.WedosAPIClient')                                                                                          
    def test_get_client_missing_credentials(self, mock_client_class, mock_get_config, mock_validate_config):                   
        """Test get_client with missing credentials (lines 60-62)"""                                                           
        from wapi.cli import get_client                                                                                        
                                                                                                                               
        mock_validate_config.return_value = (True, None)
        def mock_get_config_func(key, **kwargs):
            if key == 'WAPI_USERNAME':
                return ''
            elif key == 'WAPI_PASSWORD':
                return ''
            elif key == 'WAPI_FORCE_IPV4':
                return None
            return None
        mock_get_config.side_effect = mock_get_config_func
        
        result = get_client('config.env')
                                                                                                                               
        self.assertIsNone(result)                                                                                              
                                                                                                                               
    @patch('wapi.cli.get_logger')                                                                                              
    @patch('wapi.cli.format_output')                                                                                           
    @patch('wapi.cli.WedosAPIClient')                                                                                          
    def test_cmd_ping_success(self, mock_client_class, mock_format_output, mock_get_logger):                                   
        """Test cmd_ping with successful response (lines 70-90)"""                                                             
        from wapi.cli import cmd_ping                                                                                          
        from wapi.constants import EXIT_SUCCESS                                                                                
                                                                                                                               
        mock_logger = Mock()                                                                                                   
        mock_get_logger.return_value = mock_logger                                                                             
                                                                                                                               
        mock_client = Mock()                                                                                                   
        mock_client.ping.return_value = {                                                                                      
            'response': {                                                                                                      
                'code': '1000',                                                                                                
                'result': 'OK'                                                                                                 
            }                                                                                                                  
        }                                                                                                                      
                                                                                                                               
        mock_args = Mock()                                                                                                     
        mock_args.format = 'table'                                                                                             
                                                                                                                               
        result = cmd_ping(mock_args, mock_client)                                                                              
                                                                                                                               
        self.assertEqual(result, EXIT_SUCCESS)                                                                                 
        mock_client.ping.assert_called_once()                                                                                  
        mock_format_output.assert_called_once()                                                                                
                                                                                                                               
    @patch('wapi.cli.get_logger')                                                                                              
    @patch('wapi.cli.format_output')                                                                                           
    @patch('wapi.cli.WedosAPIClient')                                                                                          
    def test_cmd_ping_failure(self, mock_client_class, mock_format_output, mock_get_logger):                                   
        """Test cmd_ping with failed response (lines 86-90)"""                                                                 
        from wapi.cli import cmd_ping                                                                                          
        from wapi.constants import EXIT_ERROR                                                                                  
                                                                                                                               
        mock_logger = Mock()                                                                                                   
        mock_get_logger.return_value = mock_logger                                                                             
                                                                                                                               
        mock_client = Mock()                                                                                                   
        mock_client.ping.return_value = {                                                                                      
            'response': {                                                                                                      
                'code': '2000',                                                                                                
                'result': 'Error'                                                                                              
            }                                                                                                                  
        }                                                                                                                      
                                                                                                                               
        mock_args = Mock()                                                                                                     
        mock_args.format = 'table'                                                                                             
                                                                                                                               
        result = cmd_ping(mock_args, mock_client)                                                                              
                                                                                                                               
        self.assertEqual(result, EXIT_ERROR)                                                                                   
        mock_client.ping.assert_called_once()                                                                                  
                                                                                                                               
    @patch('wapi.cli.get_client')                                                                                              
    @patch('wapi.cli.argparse.ArgumentParser')                                                                                 
    def test_main_args_format_not_set(self, mock_parser_class, mock_get_client):                                               
        """Test main when args.format is not set (line 287)"""                                                                 
        mock_parser = Mock()                                                                                                   
        mock_args = Mock()                                                                                                     
        mock_args.func = Mock(return_value=EXIT_SUCCESS)                                                                       
        mock_args.module = 'test'                                                                                              
        mock_args.wizard = False
        mock_args.interactive = False
        mock_args.aliases = False
        mock_args.search_domain = None
        # Don't set format attribute                                                                                           
        delattr(mock_args, 'format') if hasattr(mock_args, 'format') else None                                                 
        mock_parser.parse_args.return_value = mock_args                                                                        
        mock_parser_class.return_value = mock_parser                                                                           
                                                                                                                               
        mock_client = Mock()                                                                                                   
        mock_get_client.return_value = mock_client                                                                             
                                                                                                                               
        result = main()                                                                                                        
                                                                                                                               
        # Should set format to 'table' and succeed                                                                             
        self.assertEqual(result, EXIT_SUCCESS)                                                                                 
        self.assertEqual(mock_args.format, 'table')                                                                            
                                                                                                                               
    @patch('wapi.cli.get_client')                                                                                              
    @patch('wapi.cli.argparse.ArgumentParser')                                                                                 
    def test_main_config_error_in_command(self, mock_parser_class, mock_get_client):                                           
        """Test main with WAPIConfigurationError in command execution (lines 308-310)"""                                       
        from wapi.exceptions import WAPIConfigurationError                                                                     
                                                                                                                               
        mock_parser = Mock()                                                                                                   
        mock_args = Mock()                                                                                                     
        mock_args.func = Mock(side_effect=WAPIConfigurationError("Config error"))                                              
        mock_args.module = 'test'                                                                                              
        mock_args.wizard = False
        mock_args.interactive = False
        mock_args.aliases = False
        mock_args.search_domain = None
        mock_parser.parse_args.return_value = mock_args                                                                        
        mock_parser_class.return_value = mock_parser                                                                           
                                                                                                                               
        mock_client = Mock()                                                                                                   
        mock_get_client.return_value = mock_client                                                                             
                                                                                                                               
        result = main()                                                                                                        
                                                                                                                               
        self.assertEqual(result, EXIT_CONFIG_ERROR)                                                                            
                                                                                                                               
    @patch('wapi.cli.get_client')                                                                                              
    @patch('wapi.cli.argparse.ArgumentParser')                                                                                 
    def test_main_timeout_error(self, mock_parser_class, mock_get_client):                                                     
        """Test main with WAPITimeoutError (lines 320-322)"""                                                                  
        from wapi.exceptions import WAPITimeoutError                                                                           
        from wapi.constants import EXIT_TIMEOUT_ERROR                                                                          
                                                                                                                               
        mock_parser = Mock()                                                                                                   
        mock_args = Mock()                                                                                                     
        mock_args.func = Mock(side_effect=WAPITimeoutError("Timeout"))                                                         
        mock_args.module = 'test'                                                                                              
        mock_args.wizard = False
        mock_args.interactive = False
        mock_args.aliases = False
        mock_args.search_domain = None
        mock_parser.parse_args.return_value = mock_args                                                                        
        mock_parser_class.return_value = mock_parser                                                                           
                                                                                                                               
        mock_client = Mock()                                                                                                   
        mock_get_client.return_value = mock_client                                                                             
                                                                                                                               
        result = main()                                                                                                        
                                                                                                                               
        self.assertEqual(result, EXIT_TIMEOUT_ERROR)                                                                           
                                                                                                                               
    @patch('wapi.cli.get_client')                                                                                              
    @patch('wapi.cli.argparse.ArgumentParser')                                                                                 
    def test_main_request_error(self, mock_parser_class, mock_get_client):                                                     
        """Test main with WAPIRequestError (lines 324-326)"""                                                                  
        from wapi.exceptions import WAPIRequestError                                                                           
                                                                                                                               
        mock_parser = Mock()                                                                                                   
        mock_args = Mock()                                                                                                     
        mock_args.func = Mock(side_effect=WAPIRequestError("Request error"))                                                   
        mock_args.module = 'test'                                                                                              
        mock_args.wizard = False
        mock_args.interactive = False
        mock_args.aliases = False
        mock_args.search_domain = None
        mock_parser.parse_args.return_value = mock_args                                                                        
        mock_parser_class.return_value = mock_parser                                                                           
                                                                                                                               
        mock_client = Mock()                                                                                                   
        mock_get_client.return_value = mock_client                                                                             
                                                                                                                               
        result = main()                                                                                                        
                                                                                                                               
        self.assertEqual(result, EXIT_ERROR)                                                                                   
                                                                                                                               
    @patch('wapi.cli.get_client')                                                                                              
    @patch('wapi.cli.argparse.ArgumentParser')                                                                                 
    def test_main_wapi_error(self, mock_parser_class, mock_get_client):                                                        
        """Test main with WAPIError (lines 328-330)"""                                                                         
        from wapi.exceptions import WAPIError                                                                                  
                                                                                                                               
        mock_parser = Mock()                                                                                                   
        mock_args = Mock()                                                                                                     
        mock_args.func = Mock(side_effect=WAPIError("WAPI error"))                                                             
        mock_args.module = 'test'                                                                                              
        mock_args.wizard = False
        mock_args.interactive = False
        mock_args.aliases = False
        mock_args.search_domain = None
        mock_parser.parse_args.return_value = mock_args                                                                        
        mock_parser_class.return_value = mock_parser                                                                           
                                                                                                                               
        mock_client = Mock()                                                                                                   
        mock_get_client.return_value = mock_client                                                                             
                                                                                                                               
        result = main()                                                                                                        
                                                                                                                               
        self.assertEqual(result, EXIT_ERROR)                                                                                   
                                                                                                                               
    @patch('wapi.cli.get_client')                                                                                              
    @patch('wapi.cli.argparse.ArgumentParser')                                                                                 
    def test_main_no_func(self, mock_parser_class, mock_get_client):                                                           
        """Test main when args.func is not set (lines 340-341)"""                                                              
        mock_parser = Mock()                                                                                                   
        mock_args = Mock()                                                                                                     
        # Don't set func attribute                                                                                             
        if hasattr(mock_args, 'func'):                                                                                         
            delattr(mock_args, 'func')                                                                                         
        mock_args.module = 'test'                                                                                              
        mock_args.wizard = False
        mock_args.interactive = False
        mock_args.aliases = False
        mock_args.search_domain = None
        mock_parser.parse_args.return_value = mock_args                                                                        
        mock_parser_class.return_value = mock_parser                                                                           
                                                                                                                               
        mock_client = Mock()                                                                                                   
        mock_get_client.return_value = mock_client                                                                             
                                                                                                                               
        result = main()                                                                                                        
                                                                                                                               
        self.assertEqual(result, EXIT_ERROR)                                                                                   
                                                                                                                               
    @patch('wapi.cli.argparse.ArgumentParser')                                                                                 
    def test_main_no_module(self, mock_parser_class):                                                                          
        """Test main when no module is specified (lines 282-283)"""                                                            
        mock_parser = Mock()                                                                                                   
        mock_args = Mock()                                                                                                     
        mock_args.module = None  # No module                                                                                   
        mock_args.wizard = False
        mock_args.interactive = False
        mock_args.aliases = False
        mock_args.search_domain = None
        mock_parser.parse_args.return_value = mock_args                                                                        
        mock_parser_class.return_value = mock_parser                                                                           
                                                                                                                               
        result = main()                                                                                                        
                                                                                                                               
        self.assertEqual(result, EXIT_ERROR)                                                                                   
        mock_parser.print_help.assert_called_once()                                                                            
                                                                                                                               
    @patch('wapi.cli.get_client')                                                                                              
    @patch('wapi.cli.argparse.ArgumentParser')                                                                                 
    def test_main_get_client_returns_none(self, mock_parser_class, mock_get_client):                                           
        """Test main when get_client returns None (line 293)"""                                                                
        mock_parser = Mock()                                                                                                   
        mock_args = Mock()                                                                                                     
        mock_args.func = Mock(return_value=EXIT_SUCCESS)                                                                       
        mock_args.module = 'test'                                                                                              
        mock_args.wizard = False
        mock_args.interactive = False
        mock_args.aliases = False
        mock_args.search_domain = None
        mock_parser.parse_args.return_value = mock_args                                                                        
        mock_parser_class.return_value = mock_parser                                                                           
                                                                                                                               
        mock_get_client.return_value = None  # Client is None                                                                  
                                                                                                                               
        result = main()                                                                                                        
                                                                                                                               
        self.assertEqual(result, EXIT_CONFIG_ERROR)                                                                            
                                                                                                                               
    @patch('wapi.cli.get_client')                                                                                              
    @patch('wapi.cli.argparse.ArgumentParser')                                                                                 
    def test_main_connection_error(self, mock_parser_class, mock_get_client):                                                  
        """Test main with WAPIConnectionError (lines 316-318)"""                                                               
        from wapi.exceptions import WAPIConnectionError                                                                        
        from wapi.constants import EXIT_CONNECTION_ERROR                                                                       
                                                                                                                               
        mock_parser = Mock()                                                                                                   
        mock_args = Mock()                                                                                                     
        mock_args.func = Mock(side_effect=WAPIConnectionError("Connection error"))                                             
        mock_args.module = 'test'                                                                                              
        mock_args.wizard = False
        mock_args.interactive = False
        mock_args.aliases = False
        mock_args.search_domain = None
        mock_parser.parse_args.return_value = mock_args                                                                        
        mock_parser_class.return_value = mock_parser                                                                           
                                                                                                                               
        mock_client = Mock()                                                                                                   
        mock_get_client.return_value = mock_client                                                                             
                                                                                                                               
        result = main()                                                                                                        
                                                                                                                               
        self.assertEqual(result, EXIT_CONNECTION_ERROR)

    @patch('wapi.commands.search.perform_whois_lookup')
    @patch('wapi.cli.get_client')
    @patch('wapi.cli.argparse.ArgumentParser')
    def test_main_search_without_config(self, mock_parser_class, mock_get_client, mock_whois):
        """Test search command without config (should work with WHOIS only)"""
        from wapi.commands.search import cmd_search
        
        # Mock WHOIS to return available domain response
        mock_whois.return_value = "No match for DOMAIN"
        
        mock_parser = Mock()
        mock_args = Mock()
        mock_args.func = cmd_search
        mock_args.module = 'search'
        mock_args.domain = 'example.com'
        mock_args.wizard = False
        mock_args.interactive = False
        mock_args.aliases = False
        mock_args.search_domain = None
        mock_args.config = 'config.env'
        mock_args.format = 'table'
        # Set whois attributes properly
        type(mock_args).whois_server = None
        type(mock_args).whois_timeout = 10
        mock_parser.parse_args.return_value = mock_args
        mock_parser_class.return_value = mock_parser
        
        # get_client raises WAPIConfigurationError (no config)
        # This should be caught and client set to None
        mock_get_client.side_effect = WAPIConfigurationError("No config")
        
        result = main()
        
        # Should succeed even without config (uses WHOIS)
        self.assertEqual(result, EXIT_SUCCESS)
        # Verify WHOIS was called (search worked without API client)
        mock_whois.assert_called_once()

    @patch('wapi.commands.search.perform_whois_lookup')
    @patch('wapi.cli.get_client')
    @patch('wapi.cli.argparse.ArgumentParser')
    def test_main_search_with_config_error_handling(self, mock_parser_class, mock_get_client, mock_whois):
        """Test search command error handling"""
        from wapi.commands.search import cmd_search
        from wapi.exceptions import WAPIRequestError
        
        # Mock WHOIS to fail
        mock_whois.side_effect = Exception("WHOIS failed")
        
        mock_parser = Mock()
        mock_args = Mock()
        mock_args.func = cmd_search
        mock_args.module = 'search'
        mock_args.domain = 'example.com'
        mock_args.wizard = False
        mock_args.interactive = False
        mock_args.aliases = False
        mock_args.search_domain = None
        mock_args.config = 'config.env'
        mock_args.format = 'table'
        type(mock_args).whois_server = None
        type(mock_args).whois_timeout = 10
        mock_parser.parse_args.return_value = mock_args
        mock_parser_class.return_value = mock_parser
        
        mock_get_client.side_effect = WAPIConfigurationError("No config")
        
        result = main()
        
        self.assertEqual(result, EXIT_ERROR)

    @patch('wapi.cli.get_client')
    @patch('wapi.cli.argparse.ArgumentParser')
    def test_main_search_auth_error(self, mock_parser_class, mock_get_client):
        """Test search command with authentication error"""
        from wapi.commands.search import cmd_search
        from wapi.exceptions import WAPIAuthenticationError
        from wapi.constants import EXIT_AUTH_ERROR
        
        mock_parser = Mock()
        mock_args = Mock()
        # Create a mock function that raises the error
        def mock_search_func(*args, **kwargs):
            raise WAPIAuthenticationError("Auth failed")
        mock_args.func = mock_search_func
        mock_args.module = 'search'
        mock_args.domain = 'example.com'
        mock_args.wizard = False
        mock_args.interactive = False
        mock_args.aliases = False
        mock_args.search_domain = None
        mock_args.config = 'config.env'
        mock_args.format = 'table'
        type(mock_args).whois_server = None
        type(mock_args).whois_timeout = 10
        mock_parser.parse_args.return_value = mock_args
        mock_parser_class.return_value = mock_parser
        
        mock_get_client.return_value = Mock()
        
        result = main()
        self.assertEqual(result, EXIT_AUTH_ERROR)

    @patch('wapi.cli.get_client')
    @patch('wapi.cli.argparse.ArgumentParser')
    def test_main_search_connection_error(self, mock_parser_class, mock_get_client):
        """Test search command with connection error"""
        from wapi.commands.search import cmd_search
        from wapi.exceptions import WAPIConnectionError
        from wapi.constants import EXIT_CONNECTION_ERROR
        
        mock_parser = Mock()
        mock_args = Mock()
        # Create a mock function that raises the error
        def mock_search_func(*args, **kwargs):
            raise WAPIConnectionError("Connection failed")
        mock_args.func = mock_search_func
        mock_args.module = 'search'
        mock_args.domain = 'example.com'
        mock_args.wizard = False
        mock_args.interactive = False
        mock_args.aliases = False
        mock_args.search_domain = None
        mock_args.config = 'config.env'
        mock_args.format = 'table'
        type(mock_args).whois_server = None
        type(mock_args).whois_timeout = 10
        mock_parser.parse_args.return_value = mock_args
        mock_parser_class.return_value = mock_parser
        
        mock_get_client.return_value = Mock()
        
        result = main()
        self.assertEqual(result, EXIT_CONNECTION_ERROR)

    @patch('wapi.commands.search.perform_whois_lookup')
    @patch('wapi.cli.get_client')
    @patch('wapi.cli.argparse.ArgumentParser')
    def test_main_search_generic_exception_getting_client(self, mock_parser_class, mock_get_client, mock_whois):
        """Test search command with generic exception getting client (lines 408-411)"""
        from wapi.commands.search import cmd_search
        
        mock_whois.return_value = "No match"
        
        mock_parser = Mock()
        mock_args = Mock()
        mock_args.func = cmd_search
        mock_args.module = 'search'
        mock_args.domain = 'example.com'
        mock_args.wizard = False
        mock_args.interactive = False
        mock_args.aliases = False
        mock_args.search_domain = None
        mock_args.config = 'config.env'
        mock_args.format = 'table'
        type(mock_args).whois_server = None
        type(mock_args).whois_timeout = 10
        mock_parser.parse_args.return_value = mock_args
        mock_parser_class.return_value = mock_parser
        
        # get_client raises generic Exception (not WAPIConfigurationError)
        mock_get_client.side_effect = ValueError("Some other error")
        
        result = main()
        
        # Should succeed even with generic exception (uses WHOIS)
        self.assertEqual(result, EXIT_SUCCESS)
        mock_whois.assert_called_once()

    @patch('wapi.cli.get_client')
    @patch('wapi.cli.argparse.ArgumentParser')
    def test_main_search_config_error_in_handler(self, mock_parser_class, mock_get_client):
        """Test search command with WAPIConfigurationError in handler (lines 415-417)"""
        mock_parser = Mock()
        mock_args = Mock()
        def mock_search_func(*args, **kwargs):
            from wapi.exceptions import WAPIConfigurationError
            raise WAPIConfigurationError("Config error in search")
        mock_args.func = mock_search_func
        mock_args.module = 'search'
        mock_args.domain = 'example.com'
        mock_args.wizard = False
        mock_args.interactive = False
        mock_args.aliases = False
        mock_args.search_domain = None
        mock_args.config = 'config.env'
        mock_args.format = 'table'
        type(mock_args).whois_server = None
        type(mock_args).whois_timeout = 10
        mock_parser.parse_args.return_value = mock_args
        mock_parser_class.return_value = mock_parser
        
        mock_get_client.return_value = Mock()
        
        result = main()
        self.assertEqual(result, EXIT_CONFIG_ERROR)
                                                                                                                               
                                                                                                                               
if __name__ == '__main__':                                                                                                     
    unittest.main()