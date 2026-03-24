"""Subtitle generation using faster-whisper for word-level timestamps."""

import os
import logging
from typing import List, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Lazy-loaded whisper model
_whisper_model = None


@dataclass
class WordTiming:
    word: str
    start: float
    end: float


@dataclass
class SubtitleSegment:
    """A group of words shown together as a subtitle line."""
    words: List[WordTiming]
    start: float
    end: float
    text: str


def _get_whisper_model():
    """Lazy-load the faster-whisper model."""
    global _whisper_model
    if _whisper_model is None:
        from faster_whisper import WhisperModel
        logger.info("Loading faster-whisper model (base)...")
        _whisper_model = WhisperModel("base", device="cpu", compute_type="int8")
        logger.info("Whisper model loaded successfully")
    return _whisper_model


def extract_word_timestamps(audio_path: str) -> List[WordTiming]:
    """
    Extract word-level timestamps from audio using faster-whisper.
    
    Returns list of WordTiming objects with word, start time, and end time.
    """
    model = _get_whisper_model()

    logger.info(f"Transcribing audio for word timestamps: {audio_path}")

    segments, info = model.transcribe(
        audio_path,
        word_timestamps=True,
        language="en",
        vad_filter=True,
        vad_parameters=dict(
            min_silence_duration_ms=200,
        ),
    )

    word_timings = []
    for segment in segments:
        if segment.words:
            for word_info in segment.words:
                word_timings.append(WordTiming(
                    word=word_info.word.strip(),
                    start=word_info.start,
                    end=word_info.end,
                ))

    logger.info(f"Extracted {len(word_timings)} word timestamps")
    return word_timings


def group_words_into_subtitles(
    word_timings: List[WordTiming],
    max_words_per_line: int = 6,
    max_lines: int = 2,
) -> List[SubtitleSegment]:
    """
    Group word timings into subtitle segments for display.
    Each segment shows max_lines lines of max_words_per_line words each.
    """
    if not word_timings:
        return []

    max_words = max_words_per_line * max_lines
    segments = []

    for i in range(0, len(word_timings), max_words):
        chunk = word_timings[i:i + max_words]
        if not chunk:
            continue

        text_parts = []
        line = []
        for j, wt in enumerate(chunk):
            line.append(wt.word)
            if len(line) >= max_words_per_line or j == len(chunk) - 1:
                text_parts.append(" ".join(line))
                line = []

        segments.append(SubtitleSegment(
            words=chunk,
            start=chunk[0].start,
            end=chunk[-1].end,
            text="\n".join(text_parts),
        ))

    return segments


def generate_subtitle_data(audio_path: str) -> Dict[str, Any]:
    """
    Full subtitle generation pipeline.
    
    Returns dict with:
        - word_timings: list of {word, start, end}
        - segments: grouped subtitle segments
        - duration: total audio duration
    """
    word_timings = extract_word_timestamps(audio_path)

    segments = group_words_into_subtitles(word_timings)

    duration = word_timings[-1].end if word_timings else 0.0

    return {
        "word_timings": [
            {"word": wt.word, "start": wt.start, "end": wt.end}
            for wt in word_timings
        ],
        "segments": [
            {
                "text": seg.text,
                "start": seg.start,
                "end": seg.end,
                "words": [
                    {"word": w.word, "start": w.start, "end": w.end}
                    for w in seg.words
                ],
            }
            for seg in segments
        ],
        "duration": duration,
    }
