import os
import subprocess
from pydub import AudioSegment

def get_bitrate_kbps(filepath):
    try:
        # Use ffprobe to get the bitrate in bits per second
        cmd = [
            "ffprobe",
            "-v", "error",
            "-select_streams", "a:0",
            "-show_entries", "stream=bit_rate",
            "-of", "default=noprint_wrappers=1:nokey=1",
            filepath
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        bitrate_bps = int(result.stdout.strip())
        bitrate_kbps = max(32, bitrate_bps // 1000)  # minimum 32k to avoid encoding errors
        return f"{bitrate_kbps}k"
    except Exception as e:
        print(f"⚠️  Could not determine bitrate for '{filepath}', using default 192k: {e}")
        return "192k"

def convert_to_mp3(input_file, output_file):
    try:
        audio = AudioSegment.from_file(input_file)
        bitrate = get_bitrate_kbps(input_file)
        audio.export(output_file, format="mp3", bitrate=bitrate)
        print(f"✅ Successfully converted '{input_file}' → '{output_file}' @ {bitrate}")
    except Exception as e:
        print(f"❌ Error converting '{input_file}': {e}")

input_directory = r'.\real_audio_files'
output_directory = r'.\mp3_files'

os.makedirs(output_directory, exist_ok=True)

for filename in os.listdir(input_directory):
    if filename.lower().endswith(('.ra', '.rm')):
        input_path = os.path.join(input_directory, filename)
        output_path = os.path.join(output_directory, os.path.splitext(filename)[0] + '.mp3')
        convert_to_mp3(input_path, output_path)
