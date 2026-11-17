import unittest
from sync_streaming import merge_rules, spotify_span, build_outputs, MIRRORS

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


class StandaloneMirrors(unittest.TestCase):
    def setUp(self):
        self.upstream = "# Streaming Media\n" + "".join("DOMAIN,host%d.test\n" % i for i in range(100)) + "# > Spotify\nDOMAIN,upstream.test\n"
        self.personal = "# > Spotify\nDOMAIN,personal.test\n"
        self.mirrors = {name: (header + "\nDOMAIN,mirror.test\n#DOMAIN,disabled.test\n").encode()
                        for name, (_, header) in MIRRORS.items()}

    def test_all_eight_outputs_preserve_sources_and_personal_spotify(self):
        outputs = build_outputs(self.upstream, self.personal, self.mirrors)
        self.assertEqual(len(outputs), 8)
        self.assertEqual(outputs["Ruleset/Streaming/Spotify.list"], self.personal.encode())
        self.assertIn(self.personal.encode(), outputs["Ruleset/Streaming/!CN.list"])
        for name, data in self.mirrors.items():
            self.assertEqual(outputs["Ruleset/Streaming/" + name], data)
        self.assertEqual(MIRRORS["HBO.list"][0], "Max.list")

    def test_missing_file_or_wrong_service_fails(self):
        incomplete = dict(self.mirrors)
        incomplete.pop("Netflix.list")
        with self.assertRaises(ValueError):
            build_outputs(self.upstream, self.personal, incomplete)
        wrong = dict(self.mirrors)
        wrong["HBO.list"] = b"# > Wrong\nDOMAIN,wrong.test\n"
        with self.assertRaises(ValueError):
            build_outputs(self.upstream, self.personal, wrong)

    def test_download_error_content_fails(self):
        broken = dict(self.mirrors)
        broken["YouTube.list"] = b"<html>Unavailable</html>"
        with self.assertRaises(ValueError):
            build_outputs(self.upstream, self.personal, broken)

if __name__ == "__main__":
    unittest.main()
