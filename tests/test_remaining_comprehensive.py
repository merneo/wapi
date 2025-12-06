"""
Comprehensive tests for remaining modules
"""
import pytest
from unittest.mock import MagicMock, patch, mock_open, Mock
from argparse import Namespace
import sys

# Import commands
from wapi.commands.auth import cmd_auth_login, cmd_auth_logout, cmd_auth_status
from wapi.commands.config import cmd_config_show, cmd_config_validate, cmd_config_set
from wapi.commands.contact import cmd_contact_info, cmd_contact_list
from wapi.commands.nsset import cmd_nsset_create, cmd_nsset_info, cmd_nsset_list
from wapi.commands.search import cmd_search

# Import utils
from wapi.utils.aliases import expand_alias, list_aliases
from wapi.utils.config_wizard import run_config_wizard

@pytest.fixture
def mock_client():
    client = MagicMock()
    client.call.return_value = {"response": {"code": "1000", "result": "OK"}}
    # Ensure ping returns success for auth commands
    client.ping.return_value = {"response": {"code": "1000", "result": "OK"}}
    return client

@pytest.fixture
def base_args():
    return Namespace(format='table', verbose=False, quiet=False)

# --- Auth Commands ---
def test_auth_login(base_args):
    args = base_args
    args.username = "user@example.com"
    args.password = "p"
    args.config = "c.env"
    
    with patch('wapi.commands.auth.validate_credentials', return_value=(True, None)):
        with patch('builtins.open', mock_open()) as mock_file:
            with patch('wapi.commands.auth.os.chmod'):
                with patch('wapi.commands.auth.WedosAPIClient') as mock_cls:
                    mock_cls.return_value.ping.return_value = {"response": {"code": "1000"}}
                    # Patch Path to return a path that exists (for reading logic if any) or just works
                    with patch('wapi.commands.auth.Path') as mock_path:
                        mock_path.return_value.exists.return_value = False
                        ret = cmd_auth_login(args)
                        assert ret == 0
                        mock_file.assert_called()

def test_auth_logout(base_args):
    args = base_args
    args.config = "c.env"
    with patch('wapi.commands.auth.Path') as mock_path_cls:
        mock_path = Mock()
        mock_path.exists.return_value = True
        mock_path_cls.return_value = mock_path
        
        ret = cmd_auth_logout(args)
        assert ret == 0
        mock_path.unlink.assert_called()

def test_auth_status(mock_client, base_args):
    args = base_args
    args.config = "c.env"
    # We need to patch get_config to return username/password so it tries to authenticate
    def mock_get_config(key, **kwargs):
        if key in ['WAPI_USERNAME', 'WAPI_PASSWORD']:
            return 'val'
        elif key == 'WAPI_FORCE_IPV4':
            return None
        return None
    with patch('wapi.commands.auth.get_config', side_effect=mock_get_config):
        with patch('wapi.commands.auth.WedosAPIClient', return_value=mock_client):
            ret = cmd_auth_status(args)
            assert ret == 0

# --- Config Commands ---
def test_config_show(base_args):
    args = base_args
    args.config = "c.env"
    with patch('wapi.commands.config.load_config', return_value={"K": "V"}):
        ret = cmd_config_show(args)
        assert ret == 0

def test_config_validate(base_args):
    args = base_args
    args.config = "c.env"
    with patch('wapi.commands.config.validate_config', return_value=(True, None)):
        ret = cmd_config_validate(args)
        assert ret == 0

def test_config_set(base_args):
    args = base_args
    args.config = "c.env"
    args.key = "K"
    args.value = "V"
    with patch('wapi.commands.config.set_config_value', return_value=True):
        ret = cmd_config_set(args)
        assert ret == 0

# --- Contact Commands ---
def test_contact_info(mock_client, base_args):
    args = base_args
    args.handle = "C1"
    args.tld = "cz"
    mock_client.call.return_value = {"response": {"code": "1000", "data": {"contact": {}}}}
    ret = cmd_contact_info(args, mock_client)
    assert ret == 0

def test_contact_list(mock_client, base_args):
    mock_client.call.return_value = {"response": {"code": "1000", "data": {"contact": []}}}
    ret = cmd_contact_list(base_args, mock_client)
    assert ret == 0

# --- NSSET Commands ---
def test_nsset_create(mock_client, base_args):
    args = base_args
    args.name = "NS"
    args.nameserver = ["ns1:1.1.1.1"]
    args.tech_c = "T"
    args.tld = "cz"
    args.wait = False
    args.no_ipv6_discovery = True
    
    ret = cmd_nsset_create(args, mock_client)
    assert ret == 0
    mock_client.call.assert_called()

def test_nsset_info(mock_client, base_args):
    args = base_args
    args.name = "NS"
    args.tld = "cz"
    args.domain = None
    mock_client.call.return_value = {"response": {"code": "1000", "data": {"nsset": {}}}}
    ret = cmd_nsset_info(args, mock_client)
    assert ret == 0

def test_nsset_list(mock_client, base_args):
    mock_client.call.return_value = {"response": {"code": "1000", "data": {"nsset": []}}}
    ret = cmd_nsset_list(base_args, mock_client)
    assert ret == 0

# --- Search Command ---
def test_search(base_args):
    # This command uses socket directly usually, or calls utils
    args = base_args
    args.domain = "example.com"
    args.whois_server = None
    args.whois_timeout = 5
    
    # Mock WedosAPIClient if it uses it for availability
    client = MagicMock()
    client.domain_availability.return_value = {"response": {"code": "1000", "data": {"avail": 1}}}
    
    # We need to patch format_output to avoid printing
    with patch('wapi.commands.search.format_output'):
        # Mock whois socket
        with patch('socket.create_connection') as mock_conn:
            mock_conn.return_value.recv.return_value = b"WHOIS DATA"
            ret = cmd_search(args, client)
            assert ret == 0

# --- Utils: Aliases ---
def test_aliases():
    assert isinstance(list_aliases(), str)
    assert expand_alias('search') == 'search'

# --- Utils: Config Wizard ---
def test_wizard():
    with patch('builtins.input', side_effect=['u', 'p', 'y']):
        # Patch getpass to return password
        with patch('wapi.utils.config_wizard.getpass', return_value='p'):
            # Patch builtins.open for saving
            with patch('builtins.open', mock_open()):
                with patch('wapi.utils.config_wizard.os.chmod'):
                     with patch('wapi.utils.config_wizard.WedosAPIClient') as mock_cls:
                         with patch('wapi.utils.config_wizard.Path') as mock_path_cls:
                             mock_path = Mock()
                             mock_path.exists.return_value = False
                             mock_path_cls.return_value = mock_path
                             
                             mock_cls.return_value.ping.return_value = {"response": {"code": "1000"}}
                             with patch('builtins.print'):
                                 assert run_config_wizard("c.env") is True
