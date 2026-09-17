#!/usr/bin/env python3
"""Unit tests for clip-enrich pure logic (no network, no Coffee calls)."""
import importlib.machinery
import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
loader = importlib.machinery.SourceFileLoader("clip_enrich", str(ROOT / "scripts" / "clip-enrich.py"))
spec = importlib.util.spec_from_loader("clip_enrich", loader)
assert spec is not None
ce = importlib.util.module_from_spec(spec)
sys.modules["clip_enrich"] = ce
loader.exec_module(ce)


class TestClipLinks(unittest.TestCase):
    def test_finds_hash(self):
        t = "Clip: https://techno.meetcoffee.ai/clip/6uddxzvnbvdzk884jvi7e1wx22y2db8 see recording"
        self.assertEqual(ce.extract_clip_links(t), ["6uddxzvnbvdzk884jvi7e1wx22y2db8"])

    def test_dedupes_and_ignores_others(self):
        t = ("https://techno.meetcoffee.ai/clip/aaaaaaaabbbbbbbbccccccccdddddddd "
             "https://techno.meetcoffee.ai/clip/aaaaaaaabbbbbbbbccccccccdddddddd "
             "https://techno.meetcoffee.ai/task?hash=lBKlrI8OfZILQkXxhFX5E2AK")
        self.assertEqual(len(ce.extract_clip_links(t)), 1)

    def test_none_safe(self):
        self.assertEqual(ce.extract_clip_links(None), [])


class TestEnriched(unittest.TestCase):
    def test_marker_in_comment(self):
        self.assertTrue(ce.is_enriched(["clip-enrich:v1 — digest appended"], "brief"))

    def test_analysis_block_in_brief(self):
        self.assertTrue(ce.is_enriched([], "CLIP ANALYSIS — agent's-eye view"))

    def test_not_enriched(self):
        self.assertFalse(ce.is_enriched(["nice clip!"], "Clip: https://x/clip/abc"))


class TestDigest(unittest.TestCase):
    def _digest(self, transcript, vnotes, verr):
        clip = {"title": "Video Test", "source": "screen", "duration_ms": 115000}
        return ce.build_digest(clip, "6uddxzvnbvdzk884jvi7e1wx22y2db8", transcript, vnotes, verr, 19, 115.0)

    def test_full(self):
        d = self._digest("[00:00 -> 00:01] hello", "- frame 1: calendar", None)
        for frag in ("CLIP ANALYSIS", "TRANSCRIPT", "[00:00 -> 00:01] hello", "VISUAL NOTES",
                     "6uddxzvnbvdzk884jvi7e1wx22y2db8", "reproducible"):
            self.assertIn(frag, d)

    def test_degraded(self):
        d = self._digest(None, None, "vision endpoint not configured (skipped)")
        self.assertIn("unavailable", d)
        self.assertIn("vision endpoint not configured", d)


class TestDocText(unittest.TestCase):
    def test_concatenates(self):
        blocks = [{"children": [{"text": "one "}, {"text": "two"}]}, {"children": [{"text": "three"}]}]
        self.assertEqual(ce.doc_text(blocks), "one two\nthree")

    def test_anchor_url_captured(self):
        # Real Coffee shape: anchor child carries url + nested children text.
        blocks = [{"type": "p", "children": [
            {"text": "Clip: "},
            {"type": "a", "url": "https://techno.meetcoffee.ai/clip/6uddxzvnbvdzk884jvi7e1wx22y2db8",
             "children": [{"text": "https://techno.meetcoffee.ai/clip/6uddxzvnbvdzk884jvi7e1wx22y2db8"}]},
        ]}]
        txt = ce.doc_text(blocks)
        self.assertIn("/clip/6uddxzvnbvdzk884jvi7e1wx22y2db8", txt)
        self.assertEqual(ce.extract_clip_links(txt), ["6uddxzvnbvdzk884jvi7e1wx22y2db8"])

    def test_empty(self):
        self.assertEqual(ce.doc_text([]), "")


class TestFileHash(unittest.TestCase):
    def test_underscore_hash(self):
        p = "/api/v1/file/clip-1789620496668.webm?file_hash=nccUpxetgXXfeCoxlIgZkHEFFS_nVAl&media_token=abc"
        self.assertEqual(ce._file_hash_from(p), "nccUpxetgXXfeCoxlIgZkHEFFS_nVAl")

    def test_no_hash(self):
        self.assertIsNone(ce._file_hash_from("/api/v1/file/x.webm?media_token=abc"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
