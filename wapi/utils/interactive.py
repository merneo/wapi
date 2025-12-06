"""
Interactive mode (REPL) for WAPI CLI

Provides an interactive shell for running WAPI commands.
"""

import sys
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..api.client import WedosAPIClient

from ..utils.logger import get_logger


class WAPIInteractiveShell:
    """
    Interactive shell for WAPI CLI commands.
    
    Provides a REPL (Read-Eval-Print Loop) interface for running
    WAPI commands interactively.
    """
    
    def __init__(self, client: 'WedosAPIClient'):
        """
        Initialize interactive shell.
        
        Args:
            client: Configured WEDOS API client
        """
        self.client = client
        self.logger = get_logger('interactive')
        self.running = True
        self.command_history = []
        
    def run(self, _input_mock=None):
        """Start the interactive shell"""
        self.logger.info("Starting interactive mode")
        print("WAPI CLI Interactive Mode")
        print("Type 'help' for available commands, 'exit' or 'quit' to exit")
        print("=" * 60)
        
        # Use provided input mock or builtin input
        input_func = _input_mock if _input_mock is not None else input
        error_streak = 0  # protects against infinite loops when input keeps failing
        
        try:
            while self.running:
                try:
                    # Get user input
                    line = input_func("wapi> ")
                    error_streak = 0  # reset after a successful read
                    line = line.strip()

                    if not line:
                        continue
                    
                    # Add to history
                    self.command_history.append(line)
                    
                    # Parse and execute command
                    self._execute_command(line)
                    
                except KeyboardInterrupt:
                    print("\nUse 'exit' or 'quit' to exit interactive mode")
                except EOFError:
                    print("\nExiting...")
                    break
                except StopIteration:
                    # Common when a mocked input iterator is exhausted during tests
                    self.logger.error("Input stream exhausted, exiting interactive mode")
                    self.running = False
                    return 1
                except Exception as e:
                    error_streak += 1
                    self.logger.error(f"Error in interactive mode: {e}")
                    print(f"Error: {e}", file=sys.stderr)
                    
                    # If input keeps failing we can spin forever; bail out after a few errors
                    if error_streak >= 3:
                        self.logger.error("Too many consecutive errors, stopping interactive mode")
                        raise RuntimeError("Too many consecutive input errors")
                    
        except Exception as e:
            self.logger.error(f"Fatal error in interactive mode: {e}")
            print(f"Fatal error: {e}", file=sys.stderr)
            return 1
        
        return 0
    
    def _execute_command(self, line: str):
        """Execute a command line"""
        parts = line.split()
        if not parts:
            return
        
        command = parts[0].lower()
        args = parts[1:]
        
        if command in ('exit', 'quit', 'q'):
            self.running = False
            print("Goodbye!")
        elif command == 'help':
            self._show_help()
        elif command == 'history':
            self._show_history()
        elif command == 'clear':
            import os
            os.system('clear' if os.name != 'nt' else 'cls')
        elif command == 'ping':
            self._cmd_ping()
        elif command.startswith('domain'):
            self._cmd_domain(args)
        elif command.startswith('dns'):
            self._cmd_dns(args)
        elif command.startswith('nsset'):
            self._cmd_nsset(args)
        elif command.startswith('contact'):
            self._cmd_contact(args)
        elif command.startswith('config'):
            self._cmd_config(args)
        else:
            print(f"Unknown command: {command}")
            print("Type 'help' for available commands")
    
    def _show_help(self):
        """Show help information"""
        help_text = """
Available commands:

  General:
    help              - Show this help message
    exit, quit, q     - Exit interactive mode
    history           - Show command history
    clear             - Clear screen
    ping              - Test API connection

  Domain operations:
    domain list                    - List all domains
    domain info <domain>           - Get domain information
    domain update-ns <domain>      - Update domain nameservers

  DNS operations:
    dns records <domain>           - List DNS records
    dns add <domain>               - Add DNS record
    dns delete <domain>            - Delete DNS record

  NSSET operations:
    nsset info <name>              - Get NSSET information
    nsset create <name>            - Create NSSET

  Contact operations:
    contact info <handle>          - Get contact information

  Configuration:
    config show                    - Show configuration
    config validate                - Validate configuration

Note: Commands support the same options as the CLI.
Use '--help' after any command for detailed help.
        """
        print(help_text)
    
    def _show_history(self):
        """Show command history"""
        if not self.command_history:
            print("No commands in history")
            return
        
        print("Command history:")
        for i, cmd in enumerate(self.command_history[-20:], 1):
            print(f"  {i}. {cmd}")
    
    def _cmd_ping(self):
        """Execute ping command"""
        try:
            result = self.client.ping()
            response = result.get('response', {})
            code = response.get('code')
            
            if code == '1000' or code == 1000:
                print("✓ Connection successful")
            else:
                print(f"✗ Connection failed: {response.get('result', 'Unknown error')}")
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
    
    def _cmd_domain(self, args):
        """Execute domain command"""
        if not args:
            print("Usage: domain <list|info|update-ns> [arguments]")
            return
        
        subcommand = args[0].lower()
        print(f"Domain command: {subcommand} (not yet implemented in interactive mode)")
        print("Use 'wapi domain {subcommand}' from command line for full functionality")
    
    def _cmd_dns(self, args):
        """Execute DNS command"""
        if not args:
            print("Usage: dns <records|add|delete> [arguments]")
            return
        
        subcommand = args[0].lower()
        print(f"DNS command: {subcommand} (not yet implemented in interactive mode)")
        print("Use 'wapi dns {subcommand}' from command line for full functionality")
    
    def _cmd_nsset(self, args):
        """Execute NSSET command"""
        if not args:
            print("Usage: nsset <info|create> [arguments]")
            return
        
        subcommand = args[0].lower()
        print(f"NSSET command: {subcommand} (not yet implemented in interactive mode)")
        print("Use 'wapi nsset {subcommand}' from command line for full functionality")
    
    def _cmd_contact(self, args):
        """Execute contact command"""
        if not args:
            print("Usage: contact <info> [arguments]")
            return
        
        subcommand = args[0].lower()
        print(f"Contact command: {subcommand} (not yet implemented in interactive mode)")
        print("Use 'wapi contact {subcommand}' from command line for full functionality")
    
    def _cmd_config(self, args):
        """Execute config command"""
        if not args:
            print("Usage: config <show|validate|set> [arguments]")
            return
        
        subcommand = args[0].lower()
        print(f"Config command: {subcommand} (not yet implemented in interactive mode)")
        print("Use 'wapi config {subcommand}' from command line for full functionality")


def start_interactive_mode(client: 'WedosAPIClient', _input_mock=None) -> int:
    """
    Start interactive mode (REPL).
    
    Args:
        client: Configured WEDOS API client
        _input_mock: Optional mock for input function (for testing)
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    shell = WAPIInteractiveShell(client)
    return shell.run(_input_mock=_input_mock)
