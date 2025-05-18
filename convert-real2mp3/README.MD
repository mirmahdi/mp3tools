# Real Audio to MP3 Converter

`convert_real_to_mp3.py` is a straightforward Python script designed to convert Real Audio files (`.ra`, `.rm`) into MP3 format efficiently.

---

## Features

* **Convert Real Audio files** (`.ra`, `.rm`) into MP3.
* Output MP3 files encoded at 192 kbps bitrate.
* Automatically processes all compatible files within the specified directory.

---

## Requirements

* Python 3.x
* pydub (`pip install pydub`)
* FFmpeg installed and accessible from the command line ([Download FFmpeg](https://ffmpeg.org/download.html))

---

## Installation

Install required Python packages:

```bash
pip install pydub
```

Ensure FFmpeg is installed and added to your system's PATH.

---

## Usage

Place your Real Audio files (`.ra`, `.rm`) into the directory:

```
./real_audio_files
```

Run the script:

```bash
python convert_real_to_mp3.py
```

Converted MP3 files will be saved to:

```
./mp3_files
```

---

## Directory Structure

Ensure the following directory structure is in place:

```
.
├── convert_real_to_mp3.py
├── real_audio_files/
│   ├── example.ra
│   └── example.rm
└── mp3_files/
```

---

## License

This tool is provided under the Creative Commons CC0 1.0 Universal (CC0 1.0) Public Domain Dedication. You may freely modify, distribute, and use this script without any restrictions.
