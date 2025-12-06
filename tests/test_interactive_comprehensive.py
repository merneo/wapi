"""
Comprehensive tests for wapi/utils/interactive.py
"""
import pytest
from unittest.mock import MagicMock, patch, call, PropertyMock
from io import StringIO
import sys

from wapi.utils.interactive import WAPIInteractiveShell, start_interactive_mode

# Custom exception that inherits from BaseException so it's not caught by 'except Exception'
class TestAbort(BaseException):
    pass

# Helper to ensure unmocked input calls cause a test failure (crash, don't hang)
def _fail_on_unmocked_input(prompt):
    # We raise TestAbort because 'except Exception' in WAPIInteractiveShell.run
    # catches AssertionError, causing an infinite loop if input is called unexpectedly.
    # TestAbort (BaseException) bypasses it.
    raise TestAbort(f"Unexpected call to input() with prompt: {prompt}")

@pytest.fixture
def mock_client():
    return MagicMock()

@pytest.fixture
def shell(mock_client):
    return WAPIInteractiveShell(mock_client)

class TestWAPIInteractiveShell:
    
    def test_init(self, mock_client):
        shell = WAPIInteractiveShell(mock_client)
        assert shell.client == mock_client
        assert shell.running is True
        assert shell.command_history == []

@pytest.fixture
def setup_input_mock():
    # Patch builtins.input globally for these tests to catch unexpected calls
    with patch('builtins.input', side_effect=lambda x: _fail_on_unmocked_input(x)) as mock_input:
        yield mock_input

class TestWAPIInteractiveShell:
    
    def test_init(self, mock_client):
        shell = WAPIInteractiveShell(mock_client)
        assert shell.client == mock_client
        assert shell.running is True
        assert shell.command_history == []

    def test_run_exit_command(self, shell, setup_input_mock):
        setup_input_mock.side_effect = ['exit']
        with patch('sys.stdout', new=StringIO()) as fake_out:
            code = shell.run(_input_mock=setup_input_mock)
        
        assert code == 0
        assert shell.running is False
        assert "Goodbye!" in fake_out.getvalue()

    def test_run_quit_command(self, shell, setup_input_mock):
        setup_input_mock.side_effect = ['quit']
        with patch('sys.stdout', new=StringIO()) as fake_out:
            shell.run(_input_mock=setup_input_mock)
        assert shell.running is False

    def test_run_empty_input(self, shell, setup_input_mock):
        # First empty, then exit
        setup_input_mock.side_effect = ['', 'exit']
        with patch('sys.stdout', new=StringIO()):
            shell.run(_input_mock=setup_input_mock)
        assert len(shell.command_history) == 1 # Only 'exit' added
        assert shell.command_history[0] == 'exit'

    def test_keyboard_interrupt(self, shell, setup_input_mock):
        # Raise KeyboardInterrupt then exit
        setup_input_mock.side_effect = [KeyboardInterrupt, 'exit']
        with patch('sys.stdout', new=StringIO()) as fake_out:
            shell.run(_input_mock=setup_input_mock)
        assert "Use 'exit' or 'quit' to exit" in fake_out.getvalue()

    def test_eof_error(self, shell, setup_input_mock):
        setup_input_mock.side_effect = EOFError
        with patch('sys.stdout', new=StringIO()) as fake_out:
            code = shell.run(_input_mock=setup_input_mock)
        assert code == 0
        assert "Exiting..." in fake_out.getvalue()

    def test_general_exception_in_loop(self, shell, setup_input_mock):
        # First input causes error, second exits
        setup_input_mock.side_effect = [Exception("Random Error"), 'exit']
        with patch('sys.stderr', new=StringIO()) as fake_err:
             with patch('sys.stdout', new=StringIO()):
                shell.run(_input_mock=setup_input_mock)
        assert "Error: Random Error" in fake_err.getvalue()

    def test_fatal_error(self, mock_client, setup_input_mock):
        # Robust Subclass Approach:
        # Define a subclass that overrides 'running' property to raise the specific Exception.
        # This guarantees the outer 'try...except' block in run() is triggered.
        class BrokenShell(WAPIInteractiveShell):
            @property
            def running(self):
                raise Exception("Fatal System Failure")
            
            @running.setter
            def running(self, value):
                # Ignore assignment in __init__ so our property persists
                pass

        shell = BrokenShell(mock_client)
        
        with patch('sys.stderr', new=StringIO()) as fake_err:
            # Safety net: If the property mock somehow fails and we enter the loop,
            # raising TestAbort ensures we crash out of the test instead of hanging 
            # in an infinite loop (since EOFError is caught and just breaks the inner loop, not the outer while).
            setup_input_mock.side_effect = TestAbort("Safety Break - Test Failed to Trigger Fatal Error")
            
            try:
                code = shell.run(_input_mock=setup_input_mock)
            except TestAbort:
                # If we caught TestAbort, it means the fatal error logic failed to trigger.
                pytest.fail("Test entered input loop instead of raising Fatal Error")
            
        assert code == 1
        assert "Fatal error: Fatal System Failure" in fake_err.getvalue()


    def test_execute_unknown_command(self, shell):
        with patch('sys.stdout', new=StringIO()) as fake_out:
            shell._execute_command("unknown_cmd arg")
        assert "Unknown command: unknown_cmd" in fake_out.getvalue()

    def test_help_command(self, shell):
        with patch('sys.stdout', new=StringIO()) as fake_out:
            shell._execute_command("help")
        assert "Available commands:" in fake_out.getvalue()

    def test_history_command(self, shell):
        shell.command_history = ['cmd1', 'cmd2']
        with patch('sys.stdout', new=StringIO()) as fake_out:
            shell._execute_command("history")
        output = fake_out.getvalue()
        assert "1. cmd1" in output
        assert "2. cmd2" in output

    def test_history_empty(self, shell):
        with patch('sys.stdout', new=StringIO()) as fake_out:
            shell._execute_command("history")
        assert "No commands in history" in fake_out.getvalue()

    def test_clear_command(self, shell):
        with patch('os.system') as mock_system:
            shell._execute_command("clear")
        mock_system.assert_called()

    def test_ping_success(self, shell):
        shell.client.ping.return_value = {'response': {'code': '1000', 'result': 'OK'}}
        with patch('sys.stdout', new=StringIO()) as fake_out:
            shell._execute_command("ping")
        assert "✓ Connection successful" in fake_out.getvalue()

    def test_ping_failure(self, shell):
        shell.client.ping.return_value = {'response': {'code': '2000', 'result': 'Auth Error'}}
        with patch('sys.stdout', new=StringIO()) as fake_out:
            shell._execute_command("ping")
        assert "✗ Connection failed: Auth Error" in fake_out.getvalue()

    def test_ping_exception(self, shell):
        shell.client.ping.side_effect = Exception("Network Error")
        with patch('sys.stderr', new=StringIO()) as fake_err:
            shell._execute_command("ping")
        assert "Error: Network Error" in fake_err.getvalue()

    @pytest.mark.parametrize("cmd_prefix", ['domain', 'dns', 'nsset', 'contact', 'config'])
    def test_not_implemented_commands(self, shell, cmd_prefix):
        with patch('sys.stdout', new=StringIO()) as fake_out:
            shell._execute_command(f"{cmd_prefix} list")
        assert "not yet implemented in interactive mode" in fake_out.getvalue()

    @pytest.mark.parametrize("cmd_prefix", ['domain', 'dns', 'nsset', 'contact', 'config'])
    def test_missing_args(self, shell, cmd_prefix):
        with patch('sys.stdout', new=StringIO()) as fake_out:
            shell._execute_command(f"{cmd_prefix}")
        assert "Usage:" in fake_out.getvalue()

def test_start_interactive_mode(mock_client, setup_input_mock):
    with patch('wapi.utils.interactive.WAPIInteractiveShell') as MockShell:
        MockShell.return_value.run.return_value = 0
        # Pass the input mock to the function so it gets passed to run()
        ret = start_interactive_mode(mock_client, _input_mock=setup_input_mock)
        assert ret == 0
        MockShell.assert_called_with(mock_client)
        MockShell.return_value.run.assert_called_with(_input_mock=setup_input_mock)
