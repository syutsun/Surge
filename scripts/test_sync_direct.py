import unittest
from sync_direct import filter_rules

class DirectFilter(unittest.TestCase):
    def setUp(self):
        self.before = "# Direct\n" + "DOMAIN,keep-before.test\n"*10
        self.excluded = "# > PayPal\nDOMAIN-SUFFIX,paypal.com\n# >> Note\nDOMAIN,paypal-extra.test\n"
        self.after = "# > Steam\n# >> Steam Connect Manager Servers\nDOMAIN-SUFFIX,cm.steampowered.com\n# > Tencent\nIP-CIDR,192.0.2.0/24,no-resolve\n"
        self.source = self.before + self.excluded + self.after

    def test_removes_only_paypal_and_preserves_steam_subheading_and_ip(self):
        self.assertEqual(filter_rules(self.source), self.before + self.after)

    def test_future_paypal_rules_removed_and_other_rules_retained(self):
        source = self.source.replace("# >> Note", "DOMAIN,new-paypal.test\n# >> Note") + "# > New Service\nDOMAIN,new-other.test\n"
        self.assertEqual(filter_rules(source), self.before + self.after + "# > New Service\nDOMAIN,new-other.test\n")

    def test_missing_duplicate_header_and_error_page_fail(self):
        for value in (self.source.replace("# > PayPal", "# Renamed"), self.source+self.excluded, "<html>Error</html>"):
            with self.assertRaises(ValueError):
                filter_rules(value)

    def test_paypal_at_end_is_removed(self):
        self.assertEqual(filter_rules(self.before+self.excluded), self.before)

if __name__ == "__main__":
    unittest.main()
