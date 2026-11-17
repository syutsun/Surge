import unittest
from sync_streaming import merge_rules, spotify_span

class StreamingMerge(unittest.TestCase):
    def setUp(self):
        self.prefix = "# Streaming Media\n# (Music)\n# > Before\n" + "".join("DOMAIN,host%d.test\n" % i for i in range(100))
        self.spotify = "# > Spotify\nDOMAIN,upstream-spotify.test\n"
        self.suffix = "# > TIDAL\nDOMAIN-SUFFIX,tidal.com\n# (Video)\n# > Netflix\nGEOIP,NETFLIX,no-resolve\n"
        self.upstream = self.prefix + self.spotify + self.suffix
        self.personal = "# > Spotify\nDOMAIN-SUFFIX,personal-spotify.test\n#DOMAIN,disabled.test\n"

    def test_replaces_only_spotify(self):
        result = merge_rules(self.upstream, self.personal)
        self.assertEqual(result, self.prefix + self.personal + self.suffix)

    def test_new_upstream_services_stay_in_result(self):
        updated = self.upstream + "# > Future Service\nDOMAIN,new.test\n"
        self.assertTrue(merge_rules(updated, self.personal).endswith("# > Future Service\nDOMAIN,new.test\n"))

    def test_category_boundary_after_spotify_is_preserved(self):
        suffix = "# (Podcast)\n# > Future Podcast\nDOMAIN,podcast.test\n"
        result = merge_rules(self.prefix + self.spotify + suffix, self.personal)
        self.assertEqual(result, self.prefix + self.personal + suffix)

    def test_missing_or_duplicate_header_fails(self):
        for value in (self.upstream.replace("# > Spotify", "# > Renamed"), self.upstream + self.spotify):
            with self.assertRaises(ValueError):
                merge_rules(value, self.personal)

    def test_personal_file_cannot_override_other_services(self):
        with self.assertRaises(ValueError):
            merge_rules(self.upstream, self.personal + "# > Other\nDOMAIN,other.test\n")

    def test_partial_download_and_error_page_fail(self):
        for value in ("# > Spotify\nDOMAIN,short.test", "<html>Error</html>"):
            with self.assertRaises(ValueError):
                merge_rules(value, self.personal)

    def test_spotify_at_end_and_personal_edit(self):
        personal = self.personal.replace("personal-spotify.test", "edited.test")
        result = merge_rules(self.prefix + self.spotify, personal)
        start, end = spotify_span(result)
        self.assertEqual(result[start:end], personal)

if __name__ == "__main__":
    unittest.main()
