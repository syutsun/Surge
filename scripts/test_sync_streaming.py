import unittest
from sync_streaming import (
    add_spotify_rules, merge_rules, comment_youtube, section_span,
    build_outputs,
)

class SpotifyAdditions(unittest.TestCase):
    def setUp(self):
        self.personal = "# > Spotify\nDOMAIN-SUFFIX,spotifycdn.com\n"
        self.spotify = "# > Spotify\nDOMAIN-SUFFIX,spotify.com\nDOMAIN,old-upstream.test\n"
        self.before = "# Streaming Media\n# > Before\n" + "DOMAIN,keep.test\n"*100
        self.after = "# > TIDAL\nDOMAIN-SUFFIX,tidal.com\n# > YouTube\nDOMAIN-SUFFIX,youtube.com\n# > Future Provider\nDOMAIN,future.test\n"
        self.combined = self.before + self.spotify + self.after

    def test_preserves_only_the_configured_addition(self):
        self.assertEqual(add_spotify_rules(self.spotify,self.personal),
                         self.spotify+"DOMAIN-SUFFIX,spotifycdn.com\n")

    def test_other_spotify_rules_follow_upstream_changes_and_deletions(self):
        changed = "# > Spotify\nDOMAIN-SUFFIX,spotify.com\nDOMAIN,new-upstream.test\n"
        result = add_spotify_rules(changed,self.personal)
        self.assertIn("DOMAIN,new-upstream.test\n",result)
        self.assertNotIn("old-upstream.test",result)
        self.assertIn("DOMAIN-SUFFIX,spotifycdn.com\n",result)

    def test_no_duplicate_when_upstream_adds_the_same_rule(self):
        upstream = self.spotify+"DOMAIN-SUFFIX,spotifycdn.com\n"
        self.assertEqual(add_spotify_rules(upstream,self.personal),upstream)

    def test_combined_other_sections_are_unchanged(self):
        merged = merge_rules(self.combined,self.personal)
        self.assertEqual(merged,self.before+add_spotify_rules(self.spotify,self.personal)+self.after)

    def test_personal_file_cannot_override_other_sections(self):
        with self.assertRaises(ValueError):
            add_spotify_rules(self.spotify,self.personal+"# > Other\nDOMAIN,other.test\n")

    def test_missing_duplicate_headers_and_error_pages_fail(self):
        for source in ("<html>Error</html>","# > Renamed\nDOMAIN,bad.test\n",self.spotify+self.spotify):
            with self.assertRaises(ValueError):
                add_spotify_rules(source,self.personal)

    def test_all_outputs_use_correct_sources_and_keep_youtube_commented(self):
        standalone = "# > Spotify\nDOMAIN,standalone-upstream.test\n"
        outputs = build_outputs(self.combined,self.personal,standalone)
        self.assertEqual(len(outputs),2)
        self.assertEqual(outputs["Ruleset/Streaming/Spotify.list"],
                         add_spotify_rules(standalone,self.personal).encode())
        combined = outputs["Ruleset/Streaming/!CN.list"].decode()
        self.assertIn("DOMAIN,old-upstream.test\n",combined)
        self.assertNotIn("standalone-upstream.test",combined)
        start,end=section_span(combined,"YouTube")
        self.assertFalse(any(line.strip() and not line.startswith("#") for line in combined[start:end].splitlines()))

class YouTubePolicy(unittest.TestCase):
    def test_current_and_future_youtube_rules_are_commented_only_in_section(self):
        source="# > YouTube\nDOMAIN,youtube.com\n#DOMAIN,disabled.test\nDOMAIN,new.test\n# > Other\nDOMAIN,other.test\n"
        expected="# > YouTube\n# DOMAIN,youtube.com\n#DOMAIN,disabled.test\n# DOMAIN,new.test\n# > Other\nDOMAIN,other.test\n"
        self.assertEqual(comment_youtube(source),expected)
        self.assertEqual(comment_youtube(expected),expected)

    def test_crlf_and_category_boundary_are_preserved(self):
        source="# > YouTube\r\nDOMAIN,youtube.com\r\n# (Other)\r\nDOMAIN,other.test\r\n"
        self.assertEqual(comment_youtube(source),source.replace("\r\nDOMAIN,youtube.com","\r\n# DOMAIN,youtube.com"))

    def test_missing_or_duplicate_youtube_header_fails(self):
        for source in ("# > Renamed\nDOMAIN,test\n","# > YouTube\nDOMAIN,a\n# > YouTube\nDOMAIN,b\n"):
            with self.assertRaises(ValueError):
                comment_youtube(source)

if __name__ == "__main__":
    unittest.main()
