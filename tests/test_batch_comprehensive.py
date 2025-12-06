"""
Comprehensive tests for wapi/utils/batch.py
"""
import pytest
import sys
import tempfile
import os
import json
import yaml
import csv
from unittest.mock import MagicMock, patch, mock_open

from wapi.utils.batch import (
    batch_domain_operation,
    batch_dns_operation,
    read_domains_from_file,
    write_results_to_file
)

# Mock logger to avoid cluttering output
@pytest.fixture(autouse=True)
def mock_logger():
    with patch('wapi.utils.batch.get_logger') as mock:
        yield mock

class TestBatchDomainOperation:
    def test_success_all_domains(self):
        client = MagicMock()
        domains = ['example.com', 'test.com']
        operation = MagicMock(return_value="Done")
        
        results = batch_domain_operation(client, domains, operation, "test_op")
        
        assert results['total'] == 2
        assert len(results['success']) == 2
        assert len(results['failed']) == 0
        assert results['success'][0]['domain'] == 'example.com'
        assert results['success'][0]['result'] == 'Done'
        
        assert operation.call_count == 2
        operation.assert_any_call(client, 'example.com')
        operation.assert_any_call(client, 'test.com')

    def test_partial_failure(self):
        client = MagicMock()
        domains = ['good.com', 'bad.com']
        
        def side_effect(cli, domain, **kwargs):
            if domain == 'bad.com':
                raise ValueError("Oops")
            return "OK"
            
        operation = MagicMock(side_effect=side_effect)
        
        results = batch_domain_operation(client, domains, operation, "test_op")
        
        assert results['total'] == 2
        assert len(results['success']) == 1
        assert len(results['failed']) == 1
        
        assert results['success'][0]['domain'] == 'good.com'
        assert results['failed'][0]['domain'] == 'bad.com'
        assert results['failed'][0]['error'] == 'Oops'

    def test_kwargs_passing(self):
        client = MagicMock()
        domains = ['example.com']
        operation = MagicMock()
        
        batch_domain_operation(client, domains, operation, "test_op", extra_param=123)
        
        operation.assert_called_with(client, 'example.com', extra_param=123)

    def test_output_printing(self, capsys):
        client = MagicMock()
        domains = ['ok.com', 'fail.com']
        operation = MagicMock(side_effect=[True, Exception("Fail")])
        
        batch_domain_operation(client, domains, operation, "test_op")
        
        captured = capsys.readouterr()
        assert "✓ ok.com: Success" in captured.out
        assert "✗ fail.com: Fail" in captured.err


class TestBatchDNSOperation:
    def test_success_all_records(self):
        client = MagicMock()
        domain = "example.com"
        records = [{'id': 1, 'name': 'www', 'type': 'A'}]
        operation = MagicMock(return_value="Deleted")
        
        results = batch_dns_operation(client, domain, records, operation, "dns_op")
        
        assert results['total'] == 1
        assert len(results['success']) == 1
        assert results['success'][0]['result'] == 'Deleted'
        
        operation.assert_called_with(client, domain, records[0])

    def test_failure_handling(self):
        client = MagicMock()
        domain = "example.com"
        records = [{'name': 'www'}, {'name': 'mail'}]
        operation = MagicMock(side_effect=["OK", Exception("Error")])
        
        results = batch_dns_operation(client, domain, records, operation, "dns_op")
        
        assert len(results['success']) == 1
        assert len(results['failed']) == 1
        assert results['failed'][0]['error'] == 'Error'


class TestReadDomainsFromFile:
    def test_read_valid_file(self):
        content = "example.com\n  test.com  \n# comment\n\nsub.domain.org"
        with patch("builtins.open", mock_open(read_data=content)):
            domains = read_domains_from_file("dummy.txt")
            
        assert len(domains) == 3
        assert domains == ['example.com', 'test.com', 'sub.domain.org']

    def test_file_not_found(self):
        with patch("builtins.open", side_effect=FileNotFoundError):
            with pytest.raises(FileNotFoundError):
                read_domains_from_file("missing.txt")

    def test_read_error(self):
        with patch("builtins.open", side_effect=PermissionError("Denied")):
            with pytest.raises(PermissionError):
                read_domains_from_file("protected.txt")


class TestWriteResultsToFile:
    @pytest.fixture
    def sample_results(self):
        return {
            'success': [{'domain': 'ok.com', 'result': 'Done'}],
            'failed': [{'domain': 'bad.com', 'error': 'Failed'}],
            'total': 2
        }

    def test_write_json(self, sample_results, tmp_path):
        out_file = tmp_path / "out.json"
        write_results_to_file(sample_results, str(out_file), format='json')
        
        with open(out_file) as f:
            data = json.load(f)
        assert data == sample_results

    def test_write_yaml(self, sample_results, tmp_path):
        out_file = tmp_path / "out.yaml"
        write_results_to_file(sample_results, str(out_file), format='yaml')
        
        with open(out_file) as f:
            data = yaml.safe_load(f)
        assert data == sample_results

    def test_write_csv(self, sample_results, tmp_path):
        out_file = tmp_path / "out.csv"
        write_results_to_file(sample_results, str(out_file), format='csv')
        
        with open(out_file, newline='') as f:
            reader = csv.reader(f)
            rows = list(reader)
            
        assert rows[0] == ['Domain', 'Status', 'Result/Error']
        # Order depends on implementation, but we expect both
        assert ['ok.com', 'Success', 'Done'] in rows
        assert ['bad.com', 'Failed', 'Failed'] in rows

    def test_unsupported_format(self, sample_results):
        with pytest.raises(ValueError, match="Unsupported format"):
            write_results_to_file(sample_results, "out.xml", format='xml')

    def test_write_error(self, sample_results):
        with patch("builtins.open", side_effect=PermissionError):
            with pytest.raises(PermissionError):
                write_results_to_file(sample_results, "root.json", format='json')
