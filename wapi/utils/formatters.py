"""
Output formatting utilities for WAPI CLI

Supports multiple output formats: table, JSON, XML, YAML
"""

import json
from typing import Any, Dict, List
try:
    from tabulate import tabulate
    TABULATE_AVAILABLE = True
except ImportError:
    TABULATE_AVAILABLE = False

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


def format_table(data: Any, headers: List[str] = None) -> str:
    """
    Format data as a table.
    
    Args:
        data: Data to format (list of dicts or dict)
        headers: Optional column headers
        
    Returns:
        Formatted table string
    """
    if not TABULATE_AVAILABLE:
        # Fallback simple table
        if isinstance(data, list) and data and isinstance(data[0], dict):
            if not headers:
                headers = list(data[0].keys())
            lines = [' | '.join(str(h) for h in headers)]
            lines.append(' | '.join('-' * len(str(h)) for h in headers))
            for row in data:
                lines.append(' | '.join(str(row.get(h, '')) for h in headers))
            return '\n'.join(lines)
        return str(data)
    
    if isinstance(data, list):
        if data and isinstance(data[0], dict):
            if not headers:
                headers = list(data[0].keys())
            rows = [[row.get(h, '') for h in headers] for row in data]
            return tabulate(rows, headers=headers, tablefmt="grid")
        else:
            return tabulate(data, headers=headers, tablefmt="grid")
    elif isinstance(data, dict):
        rows = [[k, v] for k, v in data.items()]
        return tabulate(rows, headers=["Key", "Value"], tablefmt="grid")
    else:
        return str(data)


def format_json(data: Any, indent: int = 2) -> str:
    """
    Format data as JSON.
    
    Args:
        data: Data to format
        indent: JSON indentation level
        
    Returns:
        Formatted JSON string
    """
    return json.dumps(data, indent=indent, ensure_ascii=False)


def format_xml(data: Any) -> str:
    """
    Format data as XML (simplified).
    
    Note: This is a basic formatter. For complex XML, use proper XML library.
    
    Args:
        data: Data to format
        
    Returns:
        Formatted XML string
    """
    # Simple XML formatting - for complex structures, use xml.etree.ElementTree
    if isinstance(data, dict):
        lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<response>']
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                # Recursive handling would be needed for complex structures
                lines.append(f'  <{key}>...</{key}>')
            else:
                lines.append(f'  <{key}>{value}</{key}>')
        lines.append('</response>')
        return '\n'.join(lines)
    return str(data)


def format_yaml(data: Any) -> str:
    """
    Format data as YAML.
    
    Args:
        data: Data to format
        
    Returns:
        Formatted YAML string
    """
    if not YAML_AVAILABLE:
        return format_json(data)  # Fallback to JSON
    
    return yaml.dump(data, default_flow_style=False, allow_unicode=True)


def format_output(data: Any, format_type: str = "table", headers: List[str] = None) -> str:
    """
    Format output based on format type.
    
    Args:
        data: Data to format
        format_type: Output format (table, json, xml, yaml)
        headers: Optional headers for table format
        
    Returns:
        Formatted string
    """
    format_type = format_type.lower()
    
    if format_type == "json":
        return format_json(data)
    elif format_type == "xml":
        return format_xml(data)
    elif format_type == "yaml":
        return format_yaml(data)
    else:  # default to table
        return format_table(data, headers)
