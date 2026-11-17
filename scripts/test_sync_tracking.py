import unittest
from sync_tracking import validate, comment_mi

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


class CommentMI(unittest.TestCase):
    def setUp(self):
        self.before = "# Privacy\n" + "DOMAIN,other.example\n"*60
        self.mi = "# > MI\nDOMAIN-SUFFIX,tracking.miui.com\n# DOMAIN,api.miwifi.com // original explanation\nDOMAIN,data.mistat.xiaomi.com\n"
        self.after = "# > Microsoft\nDOMAIN,c.bing.com\n"
        self.source = self.before + self.mi + self.after

    def test_only_mi_rules_are_commented_and_original_comments_preserved(self):
        expected = self.before + "# > MI\n# DOMAIN-SUFFIX,tracking.miui.com\n# DOMAIN,api.miwifi.com // original explanation\n# DOMAIN,data.mistat.xiaomi.com\n" + self.after
        result = comment_mi(self.source.encode())
        self.assertEqual(result.decode(), expected)
        self.assertEqual(comment_mi(result), result)

    def test_future_mi_rules_are_commented_and_other_services_retained(self):
        source = self.source.replace("DOMAIN,data.mistat.xiaomi.com", "DOMAIN,data.mistat.xiaomi.com\nDOMAIN,new-mi.example")
        result = comment_mi(source.encode()).decode()
        self.assertIn("# DOMAIN,new-mi.example\n", result)
        self.assertTrue(result.endswith(self.after))

    def test_missing_or_duplicate_mi_header_fails(self):
        for text in (self.source.replace("# > MI", "# > Renamed"), self.source+self.mi):
            with self.assertRaises(ValueError):
                comment_mi(text.encode())

    def test_crlf_and_mi_at_end_are_preserved(self):
        source = (self.before+self.mi).replace("\n", "\r\n")
        result = comment_mi(source.encode()).decode()
        self.assertTrue(result.startswith(self.before.replace("\n", "\r\n")))
        self.assertIn("# DOMAIN-SUFFIX,tracking.miui.com\r\n", result)

if __name__ == "__main__":
    unittest.main()
