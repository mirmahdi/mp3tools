import os
import re
import subprocess
from tqdm import tqdm

# Regex to match any contiguous run of Arabic‐script characters (e.g., Persian/Farsi)
arabic_re = re.compile(r'[\u0600-\u06FF]+')


def fix_rtl(text: str) -> str:
    """
    Reverse each contiguous run of Arabic‐script characters so that
    Farsi portions show “right” in a left‐to‐right console.
    """
    def _reverse_match(m):
        return m.group(0)[::-1]

    return arabic_re.sub(_reverse_match, text)


# 1. Find all .mp4 in the current folder
mp4_files = [f for f in os.listdir('.') if f.lower().endswith('.mp4')]

to_process = []
for fname in mp4_files:
    base, _ = os.path.splitext(fname)
    mp3_name = base + ".mp3"

    if os.path.exists(mp3_name):
        # Show the skip message, but reverse any Farsi runs so they render correctly
        display_fname = fix_rtl(fname)
        tqdm.write(f"Skipping {display_fname} (MP3 already exists)")
    else:
        to_process.append(fname)


# 2. Process only the files without existing MP3s, with a progress bar
for fname in tqdm(to_process, desc="Extracting audio", unit="file"):
    base, _ = os.path.splitext(fname)
    outfile = base + ".mp3"

    subprocess.run([
        "ffmpeg",
        "-hide_banner",
        "-loglevel", "error",
        "-i", fname,
        "-q:a", "0",
        "-map", "a",
        outfile
    ], check=True)
