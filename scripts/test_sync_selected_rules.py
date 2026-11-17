import unittest
from sync_selected_rules import prepare, SPECS

class SelectedMirrors(unittest.TestCase):
    def fixture(self):
        return {spec["name"]: (spec["header"]+"\n"+"DOMAIN,ad.example\n"*max(1,spec["minimum"])).encode()
                for spec in SPECS}

    def test_all_six_are_preserved_unchanged(self):
        files = self.fixture()
        files["PayPal.list"] += b"USER-AGENT,PayPal*\n#DOMAIN,disabled.example\n"
        files["Proxy+.list"] += b"GEOIP,GOOGLE\n"
        files["Telegram.list"] += b"IP-CIDR6,2001:db8::/32,no-resolve\n"
        self.assertEqual(prepare(files), files)

    def test_missing_file_wrong_service_or_error_page_fails(self):
        files = self.fixture()
        del files["X.list"]
        with self.assertRaises(ValueError):
            prepare(files)
        for data in (b"# Wrong\nDOMAIN,example", b"<html>Unavailable</html>", b""):
            broken = self.fixture()
            broken["PayPal.list"] = data
            with self.assertRaises(ValueError):
                prepare(broken)

    def test_partial_or_unknown_rules_fail(self):
        files = self.fixture()
        files["Proxy.list"] = b"# Proxy\nDOMAIN,partial.example\n"
        with self.assertRaises(ValueError):
            prepare(files)
        for line in (b"NEW-RULE,example\n", b"IP-CIDR,invalid,no-resolve\n", b"IP-CIDR,2001:db8::/32,no-resolve\n"):
            files = self.fixture()
            files["Telegram.list"] += line
            with self.assertRaises(ValueError):
                prepare(files)

if __name__ == "__main__":
    unittest.main()
