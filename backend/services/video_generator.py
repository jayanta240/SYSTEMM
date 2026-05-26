from PIL import Image

# Pillow compatibility fix for MoviePy
if not hasattr(Image, "ANTIALIAS"):
    Image.ANTIALIAS = Image.Resampling.LANCZOS
from PIL import Image, ImageDraw, ImageFont
import os
import uuid
import textwrap


from moviepy.editor import (
    ImageClip,
    AudioFileClip,
    CompositeVideoClip,
    concatenate_videoclips,
)

from gtts import gTTS

TEMP_DIR = "temp_videos"
os.makedirs(TEMP_DIR, exist_ok=True)


# ----------------------------------------
# CREATE MODERN EDUCATIONAL SLIDE
# ----------------------------------------
def create_slide(title, content, index):

    width = 1280
    height = 720

    # dark modern background
    img = Image.new("RGB", (width, height), (15, 23, 42))

    draw = ImageDraw.Draw(img)

    try:
        title_font = ImageFont.truetype("arial.ttf", 54)
        body_font = ImageFont.truetype("arial.ttf", 34)

    except:
        title_font = ImageFont.load_default()
        body_font = ImageFont.load_default()

    # ----------------------------------------
    # TITLE
    # ----------------------------------------
    wrapped_title = textwrap.wrap(title, width=28)

    y = 60

    for line in wrapped_title:

        draw.text(
            (70, y),
            line,
            fill=(255, 255, 255),
            font=title_font
        )

        y += 70

    # ----------------------------------------
    # ACCENT LINE
    # ----------------------------------------
    draw.rectangle(
        (70, y + 10, 500, y + 18),
        fill=(59, 130, 246)
    )

    # ----------------------------------------
    # CONTENT
    # ----------------------------------------
    wrapped_content = textwrap.wrap(content, width=50)

    y += 60

    for line in wrapped_content:

        draw.text(
            (80, y),
            line,
            fill=(220, 220, 220),
            font=body_font
        )

        y += 48

    # ----------------------------------------
    # FOOTER
    # ----------------------------------------
    draw.text(
        (70, 670),
        "AI Learning Assistant",
        fill=(120, 120, 120),
        font=body_font
    )

    slide_path = f"{TEMP_DIR}/slide_{index}.png"

    img.save(slide_path)

    return slide_path


# ----------------------------------------
# GENERATE VIDEO
# ----------------------------------------
def generate_video(scenes):

    print("🎬 Generating modern slide video...")

    clips = []

    for i, scene in enumerate(scenes):

        title = scene.get("scene_title", "")
        narration = scene.get("narration", "")

        if not narration.strip():
            continue

        # ----------------------------------------
        # CREATE SLIDE
        # ----------------------------------------
        slide_path = create_slide(
            title,
            narration,
            i
        )

        # ----------------------------------------
        # AUDIO
        # ----------------------------------------
        audio_path = f"{TEMP_DIR}/audio_{i}.mp3"

        tts = gTTS(narration)

        tts.save(audio_path)

        audio = AudioFileClip(audio_path)

        duration = audio.duration

        # ----------------------------------------
        # SLIDE CLIP
        # ----------------------------------------
        slide_clip = (
            ImageClip(slide_path)
            .set_duration(duration)
            .resize((1280, 720))
            .set_audio(audio)
        )

        # subtle cinematic zoom
        slide_clip = slide_clip.resize(
            lambda t: 1 + (0.02 * t / duration)
        )

        clips.append(slide_clip)

    # ----------------------------------------
    # FINAL VIDEO
    # ----------------------------------------
    final_video = concatenate_videoclips(
        clips,
        method="compose"
    )

    output_path = f"{TEMP_DIR}/{uuid.uuid4()}.mp4"

    final_video.write_videofile(
        output_path,
        fps=24
    )

    print("✅ Slide video ready:", output_path)

    return output_path