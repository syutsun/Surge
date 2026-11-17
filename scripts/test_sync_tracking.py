import unittest
from sync_tracking import validate

class ValidateMirror(unittest.TestCase):
    def fixture(self):
        return ("# Privacy\n" + "\n".join("DOMAIN,ad%d.example" % i for i in range(500))).encode()

    def test_accepts_rules_without_rewriting_original(self):
        data = self.fixture() + b"\nIP-CIDR,192.0.2.0/24,no-resolve\nDOMAIN-SUFFIX,ads.example\nDOMAIN,inline.example // upstream inline comment"
        before = bytes(data)
        self.assertEqual(validate(data), 503)
        self.assertEqual(data, before)

    def test_rejects_error_pages_and_partial_downloads(self):
        for data in (b"<html>Unavailable</html>", b"# Privacy\nDOMAIN,ads.example"):
            with self.assertRaises(ValueError):
                validate(data)

    def test_unknown_types_and_invalid_ip_fail(self):
        for suffix in (b"\nNEW-RULE,example", b"\nIP-CIDR,invalid,no-resolve"):
            with self.assertRaises(ValueError):
                validate(self.fixture() + suffix)

if __name__ == "__main__":
    unittest.main()
