import unittest
from sync_direct_plus import filter_rules

class DirectPlusFilter(unittest.TestCase):
    def setUp(self):
        self.before = "# Direct+\n" + "".join("DOMAIN,before%d.test\n" % i for i in range(10))
        self.excluded = "# ---(Alphabet)---\nDOMAIN-SUFFIX,blog.google\n# > Google Flights\nDOMAIN-SUFFIX,googletraveladservices.com\n"
        self.after = "# ------\n# > Tencent\nDOMAIN,keep.test\n"
        self.source = self.before + self.excluded + self.after

    def test_removes_only_target_block_and_preserves_everything_else(self):
        self.assertEqual(filter_rules(self.source), self.before + self.after)

    def test_future_rules_in_excluded_section_stay_excluded(self):
        source = self.source.replace("# > Google Flights", "DOMAIN,new-google.test\n# > Google Flights")
        self.assertEqual(filter_rules(source), self.before + self.after)

    def test_missing_duplicate_boundaries_and_error_pages_fail(self):
        for value in (
            self.source.replace("# ---(Alphabet)---", "# Renamed"),
            self.source.replace("# ------", "# Missing"),
            self.source + self.excluded,
            "<html>Error</html>",
        ):
            with self.assertRaises(ValueError):
                filter_rules(value)

    def test_new_other_upstream_rules_are_retained(self):
        source = self.source + "# > New Service\nDOMAIN,new-other.test\n"
        self.assertTrue(filter_rules(source).endswith("# > New Service\nDOMAIN,new-other.test\n"))

if __name__ == "__main__":
    unittest.main()
