#!/usr/bin/env python3
"""clip-transcribe — WAV -> transcript via faster-whisper (helper for clip-enrich).

Usage: <whisper-python> scripts/clip-transcribe.py <audio.wav>
Env:   CLIP_ENRICH_WHISPER_MODEL  (default 'small')
Prints timestamped lines on stdout; exits non-zero on failure.
"""
import os
import sys

from faster_whisper import WhisperModel

model = WhisperModel(os.environ.get("CLIP_ENRICH_WHISPER_MODEL", "small"), device="cpu", compute_type="int8")
segments, info = model.transcribe(sys.argv[1], vad_filter=True, language=None)
out = []
for s in segments:
    out.append(f"[{int(s.start // 60):02d}:{s.start % 60:05.2f} -> {int(s.end // 60):02d}:{s.end % 60:05.2f}] {s.text.strip()}")
print("\n".join(out))
