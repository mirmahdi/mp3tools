from pydub import AudioSegment
import os

def convert_to_mp3(input_file, output_file):
    try:
        audio = AudioSegment.from_file(input_file)
        audio.export(output_file, format="mp3", bitrate="192k")
        print(f"✅ Successfully converted '{input_file}' → '{output_file}'")
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
