"""
Tests for batch operations functionality
"""

import unittest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from wapi.utils.batch import (
    batch_domain_operation,
    batch_dns_operation,
    read_domains_from_file,
    write_results_to_file,
)
from wapi.api.client import WedosAPIClient


class TestBatchDomainOperation(unittest.TestCase):
    """Test batch domain operations"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_client = Mock(spec=WedosAPIClient)
    
    def test_batch_domain_operation_success(self):
        """Test successful batch domain operation"""
        domains = ['example.com', 'example.org']
        
        def mock_operation(client, domain, **kwargs):
            return {'status': 'ok', 'domain': domain}
        
        results = batch_domain_operation(
            self.mock_client,
            domains,
            mock_operation,
            'test operation'
        )
        
        self.assertEqual(results['total'], 2)
        self.assertEqual(len(results['success']), 2)
        self.assertEqual(len(results['failed']), 0)
    
    def test_batch_domain_operation_with_failures(self):
        """Test batch operation with some failures"""
        domains = ['example.com', 'invalid.domain']
        
        def mock_operation(client, domain, **kwargs):
            if domain == 'invalid.domain':
                raise Exception("Domain not found")
            return {'status': 'ok', 'domain': domain}
        
        results = batch_domain_operation(
            self.mock_client,
            domains,
            mock_operation,
            'test operation'
        )
        
        self.assertEqual(results['total'], 2)
        self.assertEqual(len(results['success']), 1)
        self.assertEqual(len(results['failed']), 1)
    
    def test_batch_domain_operation_empty_list(self):
        """Test batch operation with empty domain list"""
        results = batch_domain_operation(
            self.mock_client,
            [],
            lambda c, d, **kw: {},
            'test operation'
        )
        
        self.assertEqual(results['total'], 0)
        self.assertEqual(len(results['success']), 0)
        self.assertEqual(len(results['failed']), 0)


class TestBatchDNSOperation(unittest.TestCase):
    """Test batch DNS operations"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_client = Mock(spec=WedosAPIClient)
    
    def test_batch_dns_operation_success(self):
        """Test successful batch DNS operation"""
        records = [
            {'name': '@', 'type': 'A', 'value': '192.0.2.1'},
            {'name': 'www', 'type': 'A', 'value': '192.0.2.2'},
        ]
        
        def mock_operation(client, domain, record, **kwargs):
            return {'status': 'ok', 'record': record}
        
        results = batch_dns_operation(
            self.mock_client,
            'example.com',
            records,
            mock_operation,
            'test operation'
        )
        
        self.assertEqual(results['total'], 2)
        self.assertEqual(len(results['success']), 2)
        self.assertEqual(len(results['failed']), 0)


class TestReadDomainsFromFile(unittest.TestCase):
    """Test reading domains from file"""
    
    def test_read_domains_from_file(self):
        """Test reading domains from file"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write('example.com\n')
            f.write('example.org\n')
            f.write('# This is a comment\n')
            f.write('test.example.com\n')
            f.write('\n')  # Empty line
            temp_file = f.name
        
        try:
            domains = read_domains_from_file(temp_file)
            self.assertEqual(len(domains), 3)
            self.assertIn('example.com', domains)
            self.assertIn('example.org', domains)
            self.assertIn('test.example.com', domains)
            self.assertNotIn('# This is a comment', domains)
        finally:
            os.unlink(temp_file)
    
    def test_read_domains_from_file_nonexistent(self):
        """Test reading from nonexistent file"""
        with self.assertRaises(Exception):
            read_domains_from_file('/nonexistent/file.txt')
    
    def test_read_domains_from_file_empty(self):
        """Test reading from empty file"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            temp_file = f.name
        
        try:
            domains = read_domains_from_file(temp_file)
            self.assertEqual(len(domains), 0)
        finally:
            os.unlink(temp_file)


class TestWriteResultsToFile(unittest.TestCase):
    """Test writing results to file"""
    
    def test_write_results_json(self):
        """Test writing results as JSON"""
        results = {
            'success': [{'domain': 'example.com', 'result': 'ok'}],
            'failed': [{'domain': 'invalid.com', 'error': 'not found'}],
            'total': 2
        }
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_file = f.name
        
        try:
            write_results_to_file(results, temp_file, format='json')
            self.assertTrue(os.path.exists(temp_file))
            self.assertGreater(os.path.getsize(temp_file), 0)
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_write_results_yaml(self):
        """Test writing results as YAML"""
        results = {
            'success': [{'domain': 'example.com', 'result': 'ok'}],
            'failed': [],
            'total': 1
        }
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml') as f:
            temp_file = f.name
        
        try:
            write_results_to_file(results, temp_file, format='yaml')
            self.assertTrue(os.path.exists(temp_file))
            self.assertGreater(os.path.getsize(temp_file), 0)
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_write_results_csv(self):
        """Test writing results as CSV"""
        results = {
            'success': [{'domain': 'example.com', 'result': 'ok'}],
            'failed': [{'domain': 'invalid.com', 'error': 'not found'}],
            'total': 2
        }
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            temp_file = f.name
        
        try:
            write_results_to_file(results, temp_file, format='csv')
            self.assertTrue(os.path.exists(temp_file))
            self.assertGreater(os.path.getsize(temp_file), 0)
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_write_results_invalid_format(self):
        """Test writing with invalid format"""
        results = {'success': [], 'failed': [], 'total': 0}
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            temp_file = f.name
        
        try:
            with self.assertRaises(ValueError):
                write_results_to_file(results, temp_file, format='invalid')
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)


if __name__ == '__main__':
    unittest.main()
