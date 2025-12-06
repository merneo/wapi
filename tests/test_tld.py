"""
Unit tests for WAPI TLD utilities

Tests TLD extraction, validation, and support checking.
"""

import unittest
from wapi.utils.tld import (
    extract_tld,
    is_tld_supported,
    validate_tld,
    get_supported_tlds,
    get_tld_category,
    PRIMARY_TLDS,
    COUNTRY_CODE_TLDS,
    SPECIAL_TLDS,
    MULTI_LEVEL_TLDS,
    ALL_SUPPORTED_TLDS,
)


class TestExtractTLD(unittest.TestCase):
    """Test TLD extraction from domain names"""
    
    def test_extract_single_level_tld(self):
        """Test extraction of single-level TLDs"""
        test_cases = [
            ('example.com', 'com'),
            ('test.cz', 'cz'),
            ('domain.sk', 'sk'),
            ('site.eu', 'eu'),
            ('subdomain.example.org', 'org'),
        ]
        
        for domain, expected_tld in test_cases:
            with self.subTest(domain=domain):
                result = extract_tld(domain)
                self.assertEqual(result, expected_tld, f"Failed for {domain}")
    
    def test_extract_multi_level_tld(self):
        """Test extraction of multi-level TLDs"""
        test_cases = [
            ('example.co.uk', 'co.uk'),
            ('test.org.uk', 'org.uk'),
            ('site.com.au', 'com.au'),
        ]
        
        for domain, expected_tld in test_cases:
            with self.subTest(domain=domain):
                result = extract_tld(domain)
                self.assertEqual(result, expected_tld, f"Failed for {domain}")
    
    def test_extract_tld_invalid_domains(self):
        """Test extraction with invalid domains"""
        invalid_domains = [
            '',
            'invalid',
            'nodot',
            None,
        ]
        
        for domain in invalid_domains:
            with self.subTest(domain=domain):
                result = extract_tld(domain)
                self.assertIsNone(result, f"Should return None for {domain}")
    
    def test_extract_tld_single_word_no_dot(self):
        """Test extraction with single word (no dot) - covers line 89"""
        # This specifically tests the len(parts) < 2 branch (line 88-89)
        test_cases = ['a', 'singleword', 'nodot', 'test']
        for domain in test_cases:
            with self.subTest(domain=domain):
                result = extract_tld(domain)
                self.assertIsNone(result, f"Should return None for single word: {domain}")
    
    def test_extract_tld_edge_cases(self):
        """Test edge cases for TLD extraction"""
        # Test domain with no TLD extraction possible
        result = extract_tld('example')
        self.assertIsNone(result)
        
        # Test domain where extract_tld returns None (line 144 coverage)
        # This tests the "if not tld:" branch in validate_tld
        from wapi.utils.tld import validate_tld
        is_valid, error = validate_tld('example', strict=True)
        self.assertFalse(is_valid)
        self.assertIn('Could not extract TLD', error)
        
        # Test domain with only one part (no dot) - line 88 coverage
        result = extract_tld('nodot')
        self.assertIsNone(result)
        
        # Test domain that splits to less than 2 parts - line 89 coverage
        # This should be covered by the 'nodot' test above, but let's be explicit
        parts_test = extract_tld('a')
        self.assertIsNone(parts_test)


class TestIsTLDSupported(unittest.TestCase):
    """Test TLD support checking"""
    
    def test_primary_tlds_supported(self):
        """Test that primary TLDs are supported"""
        for tld in PRIMARY_TLDS:
            with self.subTest(tld=tld):
                self.assertTrue(is_tld_supported(tld), f"{tld} should be supported")
    
    def test_country_code_tlds_supported(self):
        """Test that country code TLDs are supported"""
        for tld in COUNTRY_CODE_TLDS:
            with self.subTest(tld=tld):
                self.assertTrue(is_tld_supported(tld), f"{tld} should be supported")
    
    def test_special_tlds_supported(self):
        """Test that special TLDs are supported"""
        for tld in SPECIAL_TLDS:
            with self.subTest(tld=tld):
                self.assertTrue(is_tld_supported(tld), f"{tld} should be supported")
    
    def test_multi_level_tlds_supported(self):
        """Test that multi-level TLDs are supported"""
        for tld in MULTI_LEVEL_TLDS:
            with self.subTest(tld=tld):
                self.assertTrue(is_tld_supported(tld), f"{tld} should be supported")
    
    def test_invalid_tlds_not_supported(self):
        """Test that invalid TLDs are not supported"""
        invalid_tlds = [
            '',
            'invalid',
            'notsupported',
            'xyz123',
            None,
        ]
        
        for tld in invalid_tlds:
            with self.subTest(tld=tld):
                self.assertFalse(is_tld_supported(tld), f"{tld} should not be supported")
    
    def test_case_insensitive(self):
        """Test that TLD checking is case-insensitive"""
        self.assertTrue(is_tld_supported('COM'))
        self.assertTrue(is_tld_supported('Com'))
        self.assertTrue(is_tld_supported('com'))
        self.assertTrue(is_tld_supported('CZ'))
        self.assertTrue(is_tld_supported('Co.UK'))


class TestValidateTLD(unittest.TestCase):
    """Test TLD validation"""
    
    def test_validate_supported_tld(self):
        """Test validation of supported TLDs"""
        test_domains = [
            'example.com',
            'test.cz',
            'domain.co.uk',
            'site.eu',
        ]
        
        for domain in test_domains:
            with self.subTest(domain=domain):
                is_valid, error = validate_tld(domain, strict=True)
                self.assertTrue(is_valid, f"{domain} should be valid: {error}")
                self.assertIsNone(error)
    
    def test_validate_unsupported_tld_strict(self):
        """Test validation of unsupported TLDs in strict mode"""
        test_domains = [
            'example.invalid',
            'test.notsupported',
            'domain.xyz123',
        ]
        
        for domain in test_domains:
            with self.subTest(domain=domain):
                is_valid, error = validate_tld(domain, strict=True)
                self.assertFalse(is_valid, f"{domain} should be invalid")
                self.assertIsNotNone(error)
                self.assertIn('not supported', error.lower())
    
    def test_validate_unsupported_tld_non_strict(self):
        """Test validation of unsupported TLDs in non-strict mode"""
        test_domains = [
            'example.invalid',
            'test.notsupported',
        ]
        
        for domain in test_domains:
            with self.subTest(domain=domain):
                is_valid, error = validate_tld(domain, strict=False)
                # Should pass format validation even if TLD is not supported
                self.assertTrue(is_valid, f"{domain} should be valid in non-strict mode: {error}")
    
    def test_validate_empty_domain(self):
        """Test validation of empty domain"""
        is_valid, error = validate_tld('', strict=True)
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)
        self.assertIn('empty', error.lower())


class TestGetSupportedTLDs(unittest.TestCase):
    """Test getting list of supported TLDs"""
    
    def test_get_supported_tlds_returns_list(self):
        """Test that get_supported_tlds returns a list"""
        tlds = get_supported_tlds()
        self.assertIsInstance(tlds, list)
        self.assertGreater(len(tlds), 0)
    
    def test_get_supported_tlds_sorted(self):
        """Test that get_supported_tlds returns sorted list"""
        tlds = get_supported_tlds()
        self.assertEqual(tlds, sorted(tlds), "TLDs should be sorted")
    
    def test_get_supported_tlds_contains_all(self):
        """Test that get_supported_tlds contains all expected TLDs"""
        tlds = get_supported_tlds()
        tlds_set = set(tlds)
        
        # Check that all category TLDs are included
        self.assertTrue(PRIMARY_TLDS.issubset(tlds_set))
        self.assertTrue(COUNTRY_CODE_TLDS.issubset(tlds_set))
        self.assertTrue(SPECIAL_TLDS.issubset(tlds_set))
        self.assertTrue(MULTI_LEVEL_TLDS.issubset(tlds_set))
        
        # Check that it matches ALL_SUPPORTED_TLDS
        self.assertEqual(tlds_set, ALL_SUPPORTED_TLDS)


class TestGetTLDCategory(unittest.TestCase):
    """Test TLD categorization"""
    
    def test_primary_tld_category(self):
        """Test categorization of primary TLDs"""
        for tld in PRIMARY_TLDS:
            with self.subTest(tld=tld):
                category = get_tld_category(tld)
                self.assertEqual(category, 'primary', f"{tld} should be primary")
    
    def test_country_tld_category(self):
        """Test categorization of country code TLDs"""
        for tld in COUNTRY_CODE_TLDS:
            with self.subTest(tld=tld):
                category = get_tld_category(tld)
                self.assertEqual(category, 'country', f"{tld} should be country")
    
    def test_special_tld_category(self):
        """Test categorization of special TLDs"""
        for tld in SPECIAL_TLDS:
            with self.subTest(tld=tld):
                category = get_tld_category(tld)
                self.assertEqual(category, 'special', f"{tld} should be special")
    
    def test_multi_level_tld_category(self):
        """Test categorization of multi-level TLDs"""
        for tld in MULTI_LEVEL_TLDS:
            with self.subTest(tld=tld):
                category = get_tld_category(tld)
                self.assertEqual(category, 'multi-level', f"{tld} should be multi-level")
    
    def test_invalid_tld_category(self):
        """Test categorization of invalid TLDs"""
        invalid_tlds = ['invalid', 'notsupported', 'xyz123', '']
        
        for tld in invalid_tlds:
            with self.subTest(tld=tld):
                category = get_tld_category(tld)
                self.assertIsNone(category, f"{tld} should have no category")
    
    def test_case_insensitive_category(self):
        """Test that categorization is case-insensitive"""
        self.assertEqual(get_tld_category('COM'), 'primary')
        self.assertEqual(get_tld_category('com'), 'primary')
        self.assertEqual(get_tld_category('CZ'), 'primary')
        self.assertEqual(get_tld_category('cz'), 'primary')


if __name__ == '__main__':
    unittest.main()
