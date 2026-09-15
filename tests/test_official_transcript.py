import unittest

from src.runtime.transcript_policy import (
    assess_official_transcript,
    merge_timed_segments,
)


def _segment(start_s, end_s, text="有效字幕内容" * 100):
    return {
        "start_ms": int(start_s * 1000),
        "end_ms": int(end_s * 1000),
        "text": text,
    }


class OfficialTranscriptAssessmentTests(unittest.TestCase):
    def test_complete_when_media_tail_is_covered(self):
        mode, gaps = assess_official_transcript(
            [_segment(0, 1800), _segment(1801, 5350)],
            duration_s=5400,
        )
        self.assertEqual(mode, "complete")
        self.assertEqual(gaps, [])

    def test_real_media_duration_catches_tail_missing_after_last_ppt(self):
        mode, gaps = assess_official_transcript(
            [_segment(0, 1800), _segment(1801, 3000)],
            duration_s=5400,
        )
        self.assertEqual(mode, "hybrid")
        self.assertEqual(gaps, [(3000.0, 5400.0)])

    def test_sparse_stub_uses_full_asr(self):
        mode, gaps = assess_official_transcript(
            [_segment(0, 10, text="只有一点")],
            duration_s=5400,
        )
        self.assertEqual(mode, "full_asr")
        self.assertEqual(gaps, [])

    def test_too_many_missing_minutes_use_full_asr(self):
        mode, gaps = assess_official_transcript(
            [_segment(3600, 5400)],
            duration_s=5400,
        )
        self.assertEqual(mode, "full_asr")
        self.assertEqual(gaps, [])

    def test_gap_asr_segments_merge_in_time_order(self):
        merged = merge_timed_segments(
            [_segment(0, 10, "official-a"), _segment(30, 40, "official-b")],
            [_segment(15, 20, "asr")],
        )
        self.assertEqual([s["text"] for s in merged], [
            "official-a", "asr", "official-b",
        ])
