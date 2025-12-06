"""
Command aliases for WAPI CLI

Provides short aliases for common commands to improve usability.
"""

# Command aliases mapping
# Format: alias -> full_command
ALIASES = {
    # Domain aliases
    'dl': 'domain list',
    'di': 'domain info',
    'dns': 'domain update-ns',
    
    # DNS aliases
    'dr': 'dns records',
    'da': 'dns add',
    'dd': 'dns delete',
    
    # NSSET aliases
    'ni': 'nsset info',
    'nc': 'nsset create',
    'nl': 'nsset list',
    
    # Contact aliases
    'ci': 'contact info',
    
    # Config aliases
    'cs': 'config show',
    'cv': 'config validate',
    
    # Auth aliases
    'p': 'auth ping',
    'l': 'auth login',
    'lo': 'auth logout',
    's': 'auth status',
}


def expand_alias(command: str) -> str:
    """
    Expand command alias to full command.
    
    Args:
        command: Command string that may contain aliases
        
    Returns:
        Command string with aliases expanded
    """
    parts = command.split()
    if not parts:
        return command
    
    # Check if first part is an alias
    first_part = parts[0].lower()
    if first_part in ALIASES:
        # Replace alias with full command
        expanded = ALIASES[first_part].split()
        return ' '.join(expanded + parts[1:])
    
    return command


def get_aliases() -> dict:
    """
    Get all available aliases.
    
    Returns:
        Dictionary of aliases mapping to full commands
    """
    return ALIASES.copy()


def list_aliases() -> str:
    """
    Get formatted list of all aliases.
    
    Returns:
        Formatted string with all aliases
    """
    lines = ["Available aliases:\n"]
    for alias, full_cmd in sorted(ALIASES.items()):
        lines.append(f"  {alias:8} -> {full_cmd}")
    return "\n".join(lines)
