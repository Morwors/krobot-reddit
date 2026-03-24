"""Local TTS engine using Coqui TTS library."""

import os
import re
import uuid
import logging
from typing import List, Tuple, Optional

import numpy as np

from app.config import settings
from app.models import VoiceInfo

logger = logging.getLogger(__name__)

# Lazy-loaded TTS instance
_tts_instance = None
_tts_model_name = None

# Available voices (VCTK speakers with deep male characteristics)
AVAILABLE_VOICES = [
    VoiceInfo(id="p226", name="Male - Deep British", gender="male", description="Deep, authoritative British male voice"),
    VoiceInfo(id="p227", name="Male - British Narrator", gender="male", description="Clear British male narrator"),
    VoiceInfo(id="p228", name="Male - Deep Baritone", gender="male", description="Deep baritone male voice"),
    VoiceInfo(id="p232", name="Male - Warm British", gender="male", description="Warm, friendly British male"),
    VoiceInfo(id="p243", name="Male - Standard British", gender="male", description="Standard British male voice"),
    VoiceInfo(id="p245", name="Male - Young British", gender="male", description="Younger British male voice"),
    VoiceInfo(id="p246", name="Male - Deep Smooth", gender="male", description="Deep, smooth male voice"),
    VoiceInfo(id="p247", name="Male - Storyteller", gender="male", description="Engaging storyteller male voice"),
    VoiceInfo(id="p251", name="Male - Clear Narrator", gender="male", description="Clear, professional male narrator"),
    VoiceInfo(id="p252", name="Male - Authoritative", gender="male", description="Authoritative male voice"),
    VoiceInfo(id="p225", name="Female - British", gender="female", description="Clear British female voice"),
    VoiceInfo(id="p229", name="Female - Warm", gender="female", description="Warm female voice"),
    VoiceInfo(id="p236", name="Female - Narrator", gender="female", description="Professional female narrator"),
]


def _get_tts():
    """Lazy-load the TTS model."""
    global _tts_instance, _tts_model_name
    model_name = settings.TTS_MODEL

    if _tts_instance is None or _tts_model_name != model_name:
        from TTS.api import TTS
        logger.info(f"Loading TTS model: {model_name}")
        _tts_instance = TTS(model_name=model_name, progress_bar=False)
        _tts_model_name = model_name
        logger.info("TTS model loaded successfully")

    return _tts_instance


def _split_into_sentences(text: str) -> List[str]:
    """Split text into sentences for more natural TTS processing."""
    # Clean up the text
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)

    # Split on sentence boundaries
    sentences = re.split(r'(?<=[.!?])\s+', text)

    # Further split very long sentences at commas or semicolons
    result = []
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        if len(sentence) > 200:
            # Split at commas or semicolons
            parts = re.split(r'(?<=[,;])\s+', sentence)
            current = ""
            for part in parts:
                if len(current) + len(part) > 200 and current:
                    result.append(current.strip())
                    current = part
                else:
                    current = (current + " " + part).strip() if current else part
            if current:
                result.append(current.strip())
        else:
            result.append(sentence)

    return [s for s in result if s]


def generate_tts_audio(
    text: str,
    speaker: str = None,
    speed: float = 1.0,
    job_id: str = None,
) -> Tuple[str, float]:
    """
    Generate TTS audio from text.
    
    Returns: (output_file_path, duration_seconds)
    """
    if speaker is None:
        speaker = settings.TTS_DEFAULT_SPEAKER

    if job_id is None:
        job_id = str(uuid.uuid4())

    output_dir = os.path.join(settings.TEMP_PATH, job_id)
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, "narration.wav")

    tts = _get_tts()

    sentences = _split_into_sentences(text)
    logger.info(f"Generating TTS for {len(sentences)} sentences with speaker={speaker}")

    if len(sentences) <= 1:
        # Single sentence or short text
        tts.tts_to_file(
            text=text,
            file_path=output_path,
            speaker=speaker,
            speed=speed,
        )
    else:
        # Generate per sentence and concatenate
        import wave
        import struct

        sentence_files = []
        for i, sentence in enumerate(sentences):
            sentence_path = os.path.join(output_dir, f"sentence_{i:04d}.wav")
            try:
                tts.tts_to_file(
                    text=sentence,
                    file_path=sentence_path,
                    speaker=speaker,
                    speed=speed,
                )
                sentence_files.append(sentence_path)
            except Exception as e:
                logger.warning(f"Failed to generate TTS for sentence {i}: {e}")
                continue

        if not sentence_files:
            raise RuntimeError("Failed to generate any TTS audio")

        # Concatenate WAV files
        _concatenate_wav_files(sentence_files, output_path)

        # Clean up sentence files
        for f in sentence_files:
            try:
                os.remove(f)
            except OSError:
                pass

    # Calculate duration
    duration = _get_wav_duration(output_path)
    logger.info(f"Generated TTS audio: {duration:.2f}s at {output_path}")

    return output_path, duration


def _concatenate_wav_files(input_files: List[str], output_path: str):
    """Concatenate multiple WAV files into one."""
    import wave

    if not input_files:
        raise ValueError("No input files to concatenate")

    # Read first file to get parameters
    with wave.open(input_files[0], 'rb') as first:
        params = first.getparams()
        sample_rate = first.getframerate()
        sample_width = first.getsampwidth()
        n_channels = first.getnchannels()

    # Add a small silence gap between sentences (0.15 seconds)
    silence_frames = int(sample_rate * 0.15)
    silence_data = b'\x00' * (silence_frames * sample_width * n_channels)

    with wave.open(output_path, 'wb') as output:
        output.setparams(params)

        for i, filepath in enumerate(input_files):
            with wave.open(filepath, 'rb') as f:
                # Ensure compatible format
                if f.getframerate() != sample_rate:
                    logger.warning(f"Sample rate mismatch in {filepath}, skipping")
                    continue
                output.writeframes(f.readframes(f.getnframes()))

            # Add silence between sentences (not after the last one)
            if i < len(input_files) - 1:
                output.writeframes(silence_data)


def _get_wav_duration(filepath: str) -> float:
    """Get duration of a WAV file in seconds."""
    import wave
    with wave.open(filepath, 'rb') as f:
        frames = f.getnframes()
        rate = f.getframerate()
        return frames / float(rate)


def list_voices() -> List[VoiceInfo]:
    """Return list of available TTS voices."""
    return AVAILABLE_VOICES
