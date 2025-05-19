# Real Audio to MP3 Converter

`convert_real_to_mp3.py` is a simple, efficient Python script that converts RealAudio files (`.ra`, `.rm`) into standard MP3 format while preserving their original bitrate. This avoids wasting space when converting low-quality source files.

---

## 🔧 Features

- Batch convert `.ra` and `.rm` files to `.mp3`
- Automatically detects and preserves the original bitrate (via `ffprobe`)
- Falls back to 192 kbps when bitrate is unavailable
- Skips files that fail to convert, with clear error messages

---

## 📦 Requirements

- Python 3.x
- [pydub](https://github.com/jiaaro/pydub)
- [FFmpeg](https://ffmpeg.org/) (must be installed and added to your system's PATH)

To install the required Python package:

```bash
pip install pydub
```

---

## 📁 Folder Structure

Make sure the following directories exist:

````markdown
.
├── convert_real_to_mp3.py
├── real_audio_files/
│   ├── file1.ra
│   └── file2.rm
└── mp3_files/
```

---

## 🚀 Usage

1. Place your `.ra` and `.rm` files inside the `real_audio_files/` directory.

2. Run the script:

```bash
python convert_real_to_mp3.py
```

3. Converted .mp3 files will be saved in the mp3_files/ directory, using the same base filename.

---

## ❗ Notes

- The script enforces a minimum MP3 bitrate of **32 kbps** for compatibility.
- If the source bitrate cannot be detected, it defaults to **192 kbps**.
- Bitrate is extracted using `ffprobe` (included with FFmpeg).

---

## 📜 License

This project is licensed under the [MIT License](./LICENSE).

You are free to use, modify, and distribute this script for personal or commercial purposes, provided that the original copyright
and license notice are included in all copies or substantial portions of the software.
