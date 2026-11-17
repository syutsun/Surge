import unittest
from sync_modules import convert, prepare

class NativeModules(unittest.TestCase):
    def setUp(self):
        self.spec = {"name":"Example.sgmodule","display_name":"Personal name","minimum_bytes":20,
                     "sections":["Script","MITM"]}
        self.source = b'#!name=Upstream name\r\n#!author=Original author\r\n#!arguments=option:true\r\n[Script]\r\nscript = type=http-response, script-path=https://example.com/script.js\r\n[MITM]\r\nhostname = %APPEND% example.com\r\n'

    def test_only_display_name_changes_and_all_other_bytes_are_preserved(self):
        result = convert(self.source,self.spec)
        self.assertEqual(result,self.source.replace(b"#!name=Upstream name",b"#!name=Personal name"))
        self.assertIn(b"#!author=Original author",result)
        self.assertIn(b"\r\n",result)

    def test_error_pages_missing_sections_or_duplicate_names_fail(self):
        for data in (b"<html>Unavailable</html>",self.source.replace(b"[MITM]",b"[Other]"),self.source+b"#!name=Duplicate\n"):
            with self.assertRaises(ValueError):
                convert(data,self.spec)

    def test_missing_module_or_unsafe_filename_fails(self):
        with self.assertRaises(ValueError):
            prepare([self.spec],{})
        unsafe = dict(self.spec,name="../escape.sgmodule")
        with self.assertRaises(ValueError):
            prepare([unsafe],{unsafe["name"]:self.source})

if __name__ == "__main__":
    unittest.main()
