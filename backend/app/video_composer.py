"""Video composer using FFmpeg and Pillow for Reddit-style video generation."""

import os
import re
import subprocess
import uuid
import logging
import textwrap
import math
from typing import List, Dict, Any, Optional, Tuple

from PIL import Image, ImageDraw, ImageFont

from app.config import settings

logger = logging.getLogger(__name__)

# ── Font Loading ────────────────────────────────────────────────────

def _find_font(bold: bool = False, size: int = 48) -> ImageFont.FreeTypeFont:
    """Find a suitable font on the system."""
    font_candidates = []
    if bold:
        font_candidates = [
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/liberation-sans/LiberationSans-Bold.ttf",
            "/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-Bold.ttf",
        ]
    else:
        font_candidates = [
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/liberation-sans/LiberationSans-Regular.ttf",
            "/usr/share/fonts/dejavu-sans-fonts/DejaVuSans.ttf",
        ]

    for font_path in font_candidates:
        if os.path.exists(font_path):
            return ImageFont.truetype(font_path, size)

    # Fallback
    return ImageFont.load_default()


# ── Reddit Card Generation ──────────────────────────────────────────

def _chunk_text(text: str, words_per_chunk: int = 50) -> List[str]:
    """Split text into readable chunks of approximately words_per_chunk words."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), words_per_chunk):
        chunk = " ".join(words[i:i + words_per_chunk])
        chunks.append(chunk)
    return chunks


def create_reddit_card_image(
    title: str,
    body_chunk: str,
    subreddit: str = "",
    card_width: int = 920,
    card_max_height: int = 900,
) -> Image.Image:
    """
    Create a Reddit-style text card as a PIL Image with transparent background.
    White text on semi-transparent dark card with rounded corners.
    """
    padding = 40
    corner_radius = 24
    content_width = card_width - (padding * 2)

    # Fonts
    title_font = _find_font(bold=True, size=42)
    body_font = _find_font(bold=False, size=36)
    sub_font = _find_font(bold=True, size=28)

    # Measure text heights
    temp_img = Image.new("RGBA", (card_width, 2000), (0, 0, 0, 0))
    temp_draw = ImageDraw.Draw(temp_img)

    # Subreddit badge
    sub_text = f"r/{subreddit}" if subreddit else ""
    sub_height = 0
    if sub_text:
        sub_bbox = temp_draw.textbbox((0, 0), sub_text, font=sub_font)
        sub_height = sub_bbox[3] - sub_bbox[1] + 20

    # Title (wrapped)
    title_lines = textwrap.wrap(title, width=38)
    title_text = "\n".join(title_lines)
    title_bbox = temp_draw.multiline_textbbox((0, 0), title_text, font=title_font, spacing=8)
    title_height = title_bbox[3] - title_bbox[1] + 20

    # Body text (wrapped)
    body_lines = textwrap.wrap(body_chunk, width=45)
    body_text = "\n".join(body_lines)
    body_bbox = temp_draw.multiline_textbbox((0, 0), body_text, font=body_font, spacing=6)
    body_height = body_bbox[3] - body_bbox[1]

    # Calculate card height
    total_content = sub_height + title_height + body_height + padding
    card_height = min(padding * 2 + total_content, card_max_height)

    # Create card image
    card = Image.new("RGBA", (card_width, card_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(card)

    # Draw rounded rectangle background
    draw.rounded_rectangle(
        [(0, 0), (card_width - 1, card_height - 1)],
        radius=corner_radius,
        fill=(20, 20, 30, 210),
        outline=(80, 80, 120, 150),
        width=2,
    )

    y_pos = padding

    # Draw subreddit badge
    if sub_text:
        # Badge background
        badge_bbox = draw.textbbox((0, 0), sub_text, font=sub_font)
        badge_width = badge_bbox[2] - badge_bbox[0] + 20
        badge_height_px = badge_bbox[3] - badge_bbox[1] + 12
        draw.rounded_rectangle(
            [(padding, y_pos), (padding + badge_width, y_pos + badge_height_px)],
            radius=12,
            fill=(120, 80, 220, 200),
        )
        draw.text((padding + 10, y_pos + 4), sub_text, fill=(255, 255, 255, 255), font=sub_font)
        y_pos += badge_height_px + 16

    # Draw title
    draw.multiline_text(
        (padding, y_pos),
        title_text,
        fill=(255, 255, 255, 255),
        font=title_font,
        spacing=8,
    )
    y_pos += title_height

    # Draw separator line
    draw.line([(padding, y_pos), (card_width - padding, y_pos)], fill=(100, 100, 140, 100), width=1)
    y_pos += 16

    # Draw body text
    draw.multiline_text(
        (padding, y_pos),
        body_text,
        fill=(220, 220, 230, 255),
        font=body_font,
        spacing=6,
    )

    return card


# ── Subtitle Frames Generation ──────────────────────────────────────

def create_subtitle_frame(
    words: List[Dict[str, Any]],
    current_time: float,
    frame_width: int = 1080,
    frame_height: int = 200,
    font_size: int = 48,
    text_color: str = "#FFFFFF",
    highlight_color: str = "#FFFF00",
    bg_opacity: float = 0.7,
) -> Image.Image:
    """
    Create a single subtitle frame with karaoke-style word highlighting.
    The currently-spoken word is highlighted in yellow.
    """
    font = _find_font(bold=True, size=font_size)

    # Create frame with semi-transparent background
    bg_alpha = int(bg_opacity * 255)
    frame = Image.new("RGBA", (frame_width, frame_height), (0, 0, 0, bg_alpha))
    draw = ImageDraw.Draw(frame)

    # Split words into lines (max 2 lines)
    max_words_per_line = 6
    lines = []
    current_line = []
    for w in words:
        current_line.append(w)
        if len(current_line) >= max_words_per_line:
            lines.append(current_line)
            current_line = []
    if current_line:
        lines.append(current_line)
    lines = lines[:2]  # Max 2 lines

    # Calculate vertical positioning
    line_height = font_size + 12
    total_height = len(lines) * line_height
    y_start = (frame_height - total_height) // 2

    # Parse colors
    tc = tuple(int(text_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + (255,)
    hc = tuple(int(highlight_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + (255,)

    for line_idx, line_words in enumerate(lines):
        # Calculate line width for centering
        line_text = " ".join(w["word"] for w in line_words)
        line_bbox = draw.textbbox((0, 0), line_text, font=font)
        line_width = line_bbox[2] - line_bbox[0]
        x_start = (frame_width - line_width) // 2

        x_pos = x_start
        y_pos = y_start + line_idx * line_height

        for w in line_words:
            word_text = w["word"]
            # Determine if this word is currently being spoken
            is_active = w["start"] <= current_time <= w["end"]
            color = hc if is_active else tc

            draw.text((x_pos, y_pos), word_text, fill=color, font=font)

            # Advance x position
            word_bbox = draw.textbbox((0, 0), word_text + " ", font=font)
            x_pos += word_bbox[2] - word_bbox[0]

    return frame


# ── Video Assembly ──────────────────────────────────────────────────

def compose_video(
    audio_path: str,
    subtitle_data: Dict[str, Any],
    title: str,
    body: str,
    subreddit: str = "",
    background_path: Optional[str] = None,
    logo_path: Optional[str] = None,
    logo_position: str = "top-right",
    subtitle_settings: Optional[Dict] = None,
    job_id: str = None,
    progress_callback=None,
) -> str:
    """
    Compose the final video with all overlays.
    
    Returns: path to the output MP4 file.
    """
    if job_id is None:
        job_id = str(uuid.uuid4())

    temp_dir = os.path.join(settings.TEMP_PATH, job_id)
    os.makedirs(temp_dir, exist_ok=True)

    output_path = os.path.join(settings.OUTPUT_PATH, f"{job_id}.mp4")
    width = settings.VIDEO_WIDTH
    height = settings.VIDEO_HEIGHT
    fps = settings.VIDEO_FPS

    duration = subtitle_data.get("duration", 30.0)
    word_timings = subtitle_data.get("word_timings", [])
    segments = subtitle_data.get("segments", [])

    sub_settings = subtitle_settings or {}
    font_size = sub_settings.get("font_size", settings.SUBTITLE_FONT_SIZE)
    text_color = sub_settings.get("text_color", settings.SUBTITLE_COLOR)
    highlight_color = sub_settings.get("highlight_color", settings.SUBTITLE_HIGHLIGHT_COLOR)
    bg_opacity = sub_settings.get("bg_opacity", 0.7)

    if progress_callback:
        progress_callback(0.1, "Preparing background video...")

    # ── Step 1: Prepare background video ────────────────────────────
    bg_video_path = os.path.join(temp_dir, "background.mp4")
    _prepare_background(background_path, bg_video_path, width, height, duration, fps)

    if progress_callback:
        progress_callback(0.2, "Generating text cards...")

    # ── Step 2: Generate Reddit text card overlays ──────────────────
    body_chunks = _chunk_text(body, words_per_chunk=50)
    card_paths = []
    chunk_duration = duration / max(len(body_chunks), 1)

    for i, chunk in enumerate(body_chunks):
        card_img = create_reddit_card_image(
            title=title if i == 0 else "",
            body_chunk=chunk,
            subreddit=subreddit if i == 0 else "",
        )
        card_path = os.path.join(temp_dir, f"card_{i:04d}.png")
        card_img.save(card_path)
        card_paths.append({
            "path": card_path,
            "start": i * chunk_duration,
            "end": (i + 1) * chunk_duration,
            "width": card_img.width,
            "height": card_img.height,
        })

    if progress_callback:
        progress_callback(0.3, "Generating subtitle frames...")

    # ── Step 3: Generate subtitle overlay as video ──────────────────
    subtitle_video_path = os.path.join(temp_dir, "subtitles.mp4")
    _generate_subtitle_video(
        subtitle_data, subtitle_video_path,
        width, 200, fps, duration,
        font_size, text_color, highlight_color, bg_opacity,
    )

    if progress_callback:
        progress_callback(0.6, "Compositing final video...")

    # ── Step 4: Composite everything with FFmpeg ────────────────────
    _composite_final_video(
        bg_video_path=bg_video_path,
        audio_path=audio_path,
        card_paths=card_paths,
        subtitle_video_path=subtitle_video_path,
        logo_path=logo_path,
        logo_position=logo_position,
        output_path=output_path,
        width=width,
        height=height,
        duration=duration,
        temp_dir=temp_dir,
    )

    if progress_callback:
        progress_callback(0.95, "Cleaning up...")

    # Clean up temp files (keep output)
    import shutil
    try:
        shutil.rmtree(temp_dir, ignore_errors=True)
    except Exception:
        pass

    if progress_callback:
        progress_callback(1.0, "Done!")

    logger.info(f"Video composed successfully: {output_path}")
    return output_path


def _prepare_background(
    background_path: Optional[str],
    output_path: str,
    width: int,
    height: int,
    duration: float,
    fps: int,
):
    """Prepare background video: scale, loop, trim."""
    if background_path and os.path.exists(background_path):
        # Scale and loop the user's background video
        cmd = [
            "ffmpeg", "-y",
            "-stream_loop", "-1",
            "-i", background_path,
            "-t", str(duration + 1),
            "-vf", f"scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height},setsar=1",
            "-r", str(fps),
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "23",
            "-an",
            output_path,
        ]
    else:
        # Generate a dark gradient background
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", f"color=c=0x1a1a2e:s={width}x{height}:d={duration + 1}:r={fps}",
            "-vf", (
                f"drawbox=x=0:y=0:w={width}:h={height // 3}:color=0x16213e@0.8:t=fill,"
                f"drawbox=x=0:y={height * 2 // 3}:w={width}:h={height // 3}:color=0x0f3460@0.6:t=fill"
            ),
            "-t", str(duration + 1),
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "23",
            output_path,
        ]

    logger.info(f"Preparing background: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        logger.error(f"FFmpeg background error: {result.stderr}")
        raise RuntimeError(f"Failed to prepare background: {result.stderr[-500:]}")


def _generate_subtitle_video(
    subtitle_data: Dict[str, Any],
    output_path: str,
    width: int,
    height: int,
    fps: int,
    duration: float,
    font_size: int,
    text_color: str,
    highlight_color: str,
    bg_opacity: float,
):
    """Generate subtitle overlay as a video with transparent background using frame images."""
    segments = subtitle_data.get("segments", [])
    if not segments:
        # Create empty transparent video
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", f"color=c=black@0.0:s={width}x{height}:d={duration}:r={fps}",
            "-c:v", "png",  # Use png for alpha
            "-t", str(duration),
            output_path.replace('.mp4', '.mov'),
        ]
        subprocess.run(cmd, capture_output=True, timeout=60)
        return

    total_frames = int(duration * fps) + 1
    frames_dir = os.path.join(os.path.dirname(output_path), "sub_frames")
    os.makedirs(frames_dir, exist_ok=True)

    # Pre-compute which segment each frame belongs to
    logger.info(f"Generating {total_frames} subtitle frames...")

    for frame_idx in range(total_frames):
        current_time = frame_idx / fps

        # Find active segment
        active_segment = None
        for seg in segments:
            if seg["start"] <= current_time <= seg["end"]:
                active_segment = seg
                break

        if active_segment:
            frame = create_subtitle_frame(
                words=active_segment["words"],
                current_time=current_time,
                frame_width=width,
                frame_height=height,
                font_size=font_size,
                text_color=text_color,
                highlight_color=highlight_color,
                bg_opacity=bg_opacity,
            )
        else:
            # Empty transparent frame
            frame = Image.new("RGBA", (width, height), (0, 0, 0, 0))

        frame_path = os.path.join(frames_dir, f"frame_{frame_idx:06d}.png")
        frame.save(frame_path, "PNG")

    # Encode frames to video
    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(fps),
        "-i", os.path.join(frames_dir, "frame_%06d.png"),
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-pix_fmt", "yuva420p",
        "-t", str(duration),
        output_path,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
        # Fallback: try without alpha
        cmd[-4] = "yuv420p"
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode != 0:
            logger.error(f"Subtitle video error: {result.stderr}")

    # Clean up frames
    import shutil
    shutil.rmtree(frames_dir, ignore_errors=True)


def _composite_final_video(
    bg_video_path: str,
    audio_path: str,
    card_paths: List[Dict],
    subtitle_video_path: str,
    logo_path: Optional[str],
    logo_position: str,
    output_path: str,
    width: int,
    height: int,
    duration: float,
    temp_dir: str,
):
    """Composite all layers into final video using FFmpeg filter_complex."""
    inputs = ["-i", bg_video_path, "-i", audio_path]
    input_idx = 2
    filter_parts = []
    current_stream = "[0:v]"

    # Overlay Reddit text cards
    for i, card in enumerate(card_paths):
        inputs.extend(["-i", card["path"]])
        card_idx = input_idx
        input_idx += 1

        # Center card horizontally, place in middle 60% vertically
        x_pos = (width - card["width"]) // 2
        y_pos = int(height * 0.15)

        # Enable/disable based on time
        enable_expr = f"between(t,{card['start']:.3f},{card['end']:.3f})"
        filter_parts.append(
            f"{current_stream}[{card_idx}:v]overlay=x={x_pos}:y={y_pos}:enable='{enable_expr}'[card{i}]"
        )
        current_stream = f"[card{i}]"

    # Overlay subtitle video at bottom
    if os.path.exists(subtitle_video_path):
        inputs.extend(["-i", subtitle_video_path])
        sub_idx = input_idx
        input_idx += 1

        sub_y = height - 200  # Bottom of screen
        filter_parts.append(
            f"{current_stream}[{sub_idx}:v]overlay=x=0:y={sub_y}:shortest=1[withsubs]"
        )
        current_stream = "[withsubs]"

    # Overlay logo
    if logo_path and os.path.exists(logo_path):
        inputs.extend(["-i", logo_path])
        logo_idx = input_idx
        input_idx += 1

        # Scale logo
        logo_label = f"logo{logo_idx}"
        filter_parts.append(
            f"[{logo_idx}:v]scale=120:120[{logo_label}]"
        )

        # Position
        margin = 30
        if logo_position == "top-left":
            lx, ly = margin, margin
        elif logo_position == "top-right":
            lx, ly = f"{width - 120 - margin}", margin
        elif logo_position == "bottom-left":
            lx, ly = margin, f"{height - 120 - margin}"
        else:  # bottom-right
            lx, ly = f"{width - 120 - margin}", f"{height - 120 - margin}"

        filter_parts.append(
            f"{current_stream}[{logo_label}]overlay=x={lx}:y={ly}[withlogo]"
        )
        current_stream = "[withlogo]"

    # Build filter_complex
    if filter_parts:
        filter_complex = ";".join(filter_parts)
        cmd = [
            "ffmpeg", "-y",
            *inputs,
            "-filter_complex", filter_complex,
            "-map", current_stream,
            "-map", "1:a",
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "20",
            "-c:a", "aac",
            "-b:a", "192k",
            "-r", str(settings.VIDEO_FPS),
            "-t", str(duration),
            "-movflags", "+faststart",
            output_path,
        ]
    else:
        # Simple merge of background + audio
        cmd = [
            "ffmpeg", "-y",
            "-i", bg_video_path,
            "-i", audio_path,
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "20",
            "-c:a", "aac",
            "-b:a", "192k",
            "-r", str(settings.VIDEO_FPS),
            "-t", str(duration),
            "-shortest",
            "-movflags", "+faststart",
            output_path,
        ]

    logger.info(f"Compositing final video...")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if result.returncode != 0:
        logger.error(f"FFmpeg composite error: {result.stderr}")
        raise RuntimeError(f"Video composition failed: {result.stderr[-500:]}")

    if not os.path.exists(output_path):
        raise RuntimeError("Output video file was not created")

    logger.info(f"Final video created: {output_path}")
