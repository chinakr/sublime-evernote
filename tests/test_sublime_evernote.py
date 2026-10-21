"""Unit tests for the pure logic of ``sublime_evernote.py``.

These tests run outside Sublime Text: the ``sublime`` API is stubbed
out (see ``stubs.py``) and only functions that do not require a live
editor are exercised.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import stubs

stubs.ensure_paths()
stubs.install()

import sublime_evernote  # noqa: E402
from evernote.edam.error.ttypes import EDAMErrorCode, EDAMUserException  # noqa: E402


class TestExtractTags(unittest.TestCase):

    def test_comma_separated(self):
        self.assertEqual(sublime_evernote.extractTags("a, b ,c"), ["a", "b", "c"])

    def test_json_list(self):
        self.assertEqual(
            sublime_evernote.extractTags('["x y", "z"]'), ["x y", "z"])

    def test_empty_string(self):
        self.assertEqual(sublime_evernote.extractTags(""), [])

    def test_strips_whitespace(self):
        self.assertEqual(
            sublime_evernote.extractTags("  tag1 \t,\ttag2  "), ["tag1", "tag2"])


class TestExtractMetadata(unittest.TestCase):

    def test_full_header(self):
        text = "---\ntitle: T\ntags: a, b\nnotebook: N\n---\n\nBody text"
        result = sublime_evernote.extract_metadata(text)
        self.assertEqual(
            result["metadata"],
            {"title": "T", "tags": ["a", "b"], "notebook": "N"})
        self.assertEqual(result["contents"], "Body text")

    def test_no_header(self):
        text = "just a body"
        result = sublime_evernote.extract_metadata(text)
        self.assertEqual(result["metadata"], {})
        self.assertEqual(result["contents"], "just a body")

    def test_json_tags_in_header(self):
        text = '---\ntags: ["x y", "z"]\n---\n\nbody'
        result = sublime_evernote.extract_metadata(text)
        self.assertEqual(result["metadata"]["tags"], ["x y", "z"])

    def test_value_may_contain_colon(self):
        text = "---\ntitle: A: B\n---\n\nbody"
        result = sublime_evernote.extract_metadata(text)
        self.assertEqual(result["metadata"]["title"], "A: B")

    def test_leading_newlines_of_body_are_stripped(self):
        text = "---\ntitle: T\n---\n\n\nbody"
        result = sublime_evernote.extract_metadata(text)
        self.assertEqual(result["contents"], "body")


class TestMetadataHeader(unittest.TestCase):

    def test_round_trip(self):
        header = sublime_evernote.metadata_header(
            title="My title", tags=["a", "b"], notebook="NB")
        result = sublime_evernote.extract_metadata(header + "body")
        self.assertEqual(result["metadata"]["title"], "My title")
        self.assertEqual(result["metadata"]["tags"], ["a", "b"])
        self.assertEqual(result["metadata"]["notebook"], "NB")
        self.assertEqual(result["contents"], "body")


class TestEvernoteLinkRegex(unittest.TestCase):

    # Real links are generated as
    # evernote:///view/{userid}/{shardid}/{noteguid}/{noteguid}/
    GUID = "deadbeef-1111-2222-3333-444455556666"
    LINK = "[My note](evernote:///view/12345/s12/%s/%s/)" % (GUID, GUID)

    def search(self, text):
        import re
        return re.search(
            sublime_evernote._EVERNOTE_LINK_REGEX, text, re.IGNORECASE)

    def test_matches_and_captures_guid(self):
        m = self.search(self.LINK)
        self.assertIsNotNone(m)
        self.assertEqual(m.group(2), self.GUID)

    def test_case_insensitive(self):
        m = self.search(self.LINK.replace("evernote://", "EVERNOTE://"))
        self.assertIsNotNone(m)

    def test_does_not_match_other_links(self):
        m = self.search("[link](http://example.com/page)")
        self.assertIsNone(m)


class TestErrorHelpers(unittest.TestCase):

    def test_errcode2name(self):
        err = EDAMUserException(errorCode=EDAMErrorCode.INVALID_AUTH)
        self.assertEqual(sublime_evernote.errcode2name(err), "Invalid auth")

    def test_err_reason_groups(self):
        cases = {
            EDAMErrorCode.INVALID_AUTH:
                "Authorisation error, consider re-configuring the plugin",
            EDAMErrorCode.ENML_VALIDATION: "Illegal note contents",
            EDAMErrorCode.INTERNAL_ERROR: "Internal server error",
            EDAMErrorCode.BAD_DATA_FORMAT:
                "User supplied data is invalid or conflicting",
            EDAMErrorCode.PERMISSION_DENIED:
                "Action not allowed, permission denied or limits exceeded",
        }
        for code, reason in cases.items():
            err = EDAMUserException(errorCode=code)
            self.assertEqual(sublime_evernote.err_reason(err), reason)

    def test_err_reason_unknown(self):
        err = EDAMUserException(errorCode=-1)
        self.assertEqual(sublime_evernote.err_reason(err), "Unknown reason")


if __name__ == "__main__":
    unittest.main()
