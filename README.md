# 🎒 TinyTools

A collection of simple, standalone Python tools for audio processing and file management; lightweight, reusable, and public domain.

**TinyTools** is a growing collection of lightweight, single-purpose Python utilities designed to simplify tasks related to audio conversion, metadata management, and more. All tools are standalone, open source, and released under the CC0 public domain license — ready for use, modification, or integration into your own workflows.

## 📦 Available Tools

### 🔸 [mp3-metadata](./mp3-metadata)
Export and import MP3 ID3 metadata to/from a CSV file.

- Export tags (title, artist, album, genre, etc.) from a folder of `.mp3` files.
- Modify tags in CSV and re-import them to update the files.
- Perfect for batch editing or metadata backups.

### 🔸 [rm2-to-mp3](./rm2-to-mp3)
Convert RealAudio (`.ra`, `.rm`) files into standard `.mp3` format using `pydub` and FFmpeg.

- Auto-processes a folder of RealAudio files.
- Batch convert .ra and .rm files to .mp3
- Automatically detects and preserves the original bitrate (via ffprobe)
- Falls back to 192 kbps when bitrate is unavailable
- Skips files that fail to convert, with clear error messages
  
## 🔒 License

All tools in this repository are released under the [Creative Commons Zero (CC0) 1.0 License](https://creativecommons.org/publicdomain/zero/1.0/). 
You are free to use, modify, and distribute them without restriction.

## 🙌 Contributions

Got a tiny tool of your own? Feel free to open a pull request to contribute new scripts, improvements, or documentation!
