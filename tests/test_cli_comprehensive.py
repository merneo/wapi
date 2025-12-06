"""
Comprehensive tests for wapi/cli.py
"""
import pytest
import sys
from unittest.mock import MagicMock, patch
from argparse import Namespace

from wapi.cli import main, get_client, cmd_ping
from wapi.exceptions import WAPIConfigurationError, WAPIAuthenticationError

# --- Tests for get_client ---

def test_get_client_success():
    with patch('wapi.cli.validate_config', return_value=(True, None)):
        with patch('wapi.cli.get_config', side_effect=['user', 'pass']):
            client = get_client('config.env')
            assert client is not None
            assert client.username == 'user'

def test_get_client_invalid_config():
    with patch('wapi.cli.validate_config', return_value=(False, "Bad config")):
        client = get_client('config.env')
        assert client is None

def test_get_client_missing_creds():
    with patch('wapi.cli.validate_config', return_value=(True, None)):
        with patch('wapi.cli.get_config', side_effect=[None, None]):
            client = get_client('config.env')
            assert client is None

def test_get_client_exception():
    with patch('wapi.cli.validate_config', side_effect=Exception("Boom")):
        client = get_client('config.env')
        assert client is None


# --- Tests for cmd_ping ---

def test_cmd_ping_success():
    client = MagicMock()
    client.ping.return_value = {"response": {"code": "1000", "result": "OK"}}
    args = Namespace(format='table')
    
    with patch('builtins.print'):
        ret = cmd_ping(args, client)
    assert ret == 0

def test_cmd_ping_failure():
    client = MagicMock()
    client.ping.return_value = {"response": {"code": "2000", "result": "Fail"}}
    args = Namespace(format='table')
    
    with patch('sys.stderr'):
        ret = cmd_ping(args, client)
    assert ret == 1


# --- Tests for main ---

@pytest.fixture
def mock_setup_logging():
    with patch('wapi.cli.setup_logging') as mock:
        yield mock

@pytest.fixture
def mock_get_client():
    with patch('wapi.cli.get_client') as mock:
        client = MagicMock()
        mock.return_value = client
        yield mock

def test_main_no_args(mock_setup_logging):
    with patch('sys.argv', ['wapi']):
        with patch('sys.stderr'): # Argparse prints usage to stderr on error
            assert main() == 1

def test_main_help(mock_setup_logging):
    with patch('sys.argv', ['wapi', '--help']):
        with pytest.raises(SystemExit):
            main()

def test_main_wizard(mock_setup_logging):
    with patch('sys.argv', ['wapi', '--wizard']):
        with patch('wapi.cli.run_config_wizard', return_value=True) as mock_wiz:
            assert main() == 0
            mock_wiz.assert_called()

def test_main_aliases(mock_setup_logging):
    with patch('sys.argv', ['wapi', '--aliases']):
        with patch('wapi.cli.list_aliases', return_value="alias list") as mock_list:
            with patch('builtins.print'):
                assert main() == 0
                mock_list.assert_called()

def test_main_interactive(mock_setup_logging, mock_get_client):
    with patch('sys.argv', ['wapi', '--interactive']):
        with patch('wapi.cli.start_interactive_mode', return_value=0) as mock_repl:
            assert main() == 0
            mock_repl.assert_called()

def test_main_interactive_config_error(mock_setup_logging):
    with patch('sys.argv', ['wapi', '--interactive']):
        with patch('wapi.cli.get_client', return_value=None):
             assert main() == 2 # EXIT_CONFIG_ERROR

def test_main_search_alias(mock_setup_logging, mock_get_client):
    with patch('sys.argv', ['wapi', '--search', 'example.com']):
        with patch('wapi.cli.cmd_search', return_value=0) as mock_search:
            assert main() == 0
            # Check arguments passed to cmd_search
            args = mock_search.call_args[0][0]
            assert args.domain == 'example.com'
            assert args.module == 'search'

def test_main_command_dispatch(mock_setup_logging, mock_get_client):
    with patch('sys.argv', ['wapi', 'auth', 'ping']):
        # We need to mock cmd_ping inside the module usage in main or ensure it is called
        # main imports cmd_ping.
        # However, main sets func=cmd_ping in parse_args defaults.
        # We can mock the function execution by checking the side effect of the function call
        
        # Easier: Mock the function attached to args
        # But argparse sets the function.
        # Let's mock the return of the function
        pass # Difficult to patch local import reference in main(), but we can test logic flow

    # Real test:
    with patch('sys.argv', ['wapi', 'auth', 'ping']):
        # Client is already mocked by fixture
        mock_get_client.return_value.ping.return_value = {"response": {"code": "1000"}}
        with patch('builtins.print'):
            assert main() == 0

def test_main_exception_handling(mock_setup_logging, mock_get_client):
    with patch('sys.argv', ['wapi', 'auth', 'ping']):
        mock_get_client.return_value.ping.side_effect = Exception("Crash")
        with patch('sys.stderr'):
            assert main() == 1

def test_main_auth_error(mock_setup_logging, mock_get_client):
    with patch('sys.argv', ['wapi', 'auth', 'ping']):
        mock_get_client.return_value.ping.side_effect = WAPIAuthenticationError("Bad Auth")
        with patch('sys.stderr'):
            assert main() == 3 # EXIT_AUTH_ERROR

def test_main_config_command(mock_setup_logging):
    # Config commands don't use client
    with patch('sys.argv', ['wapi', 'config', 'show']):
        with patch('wapi.commands.config.cmd_config_show', return_value=0) as mock_show:
            assert main() == 0
            mock_show.assert_called()

def test_main_get_client_fail(mock_setup_logging):
    with patch('sys.argv', ['wapi', 'auth', 'ping']):
        with patch('wapi.cli.get_client', return_value=None):
            assert main() == 2 # EXIT_CONFIG_ERROR
