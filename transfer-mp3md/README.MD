# MP3 Metadata Transfer Tool

`transfer-mp3md.py` is a simple and convenient Python tool designed to export and import MP3 metadata (ID3 tags) to and from CSV files.

---

## Features

* **Export MP3 metadata** to a CSV file, capturing standard tags such as title, artist, album, track number, genre, date, composer, and comments.
* **Import metadata** from CSV back into your MP3 files, updating tags effortlessly.
* Supports UTF-8 encoded CSV files.
* Handles missing or empty metadata gracefully.

---

## Requirements

* Python 3.x
* Pandas (`pip install pandas`)
* Mutagen (`pip install mutagen`)

---

## Installation

Simply download the script and ensure dependencies are installed:

```bash
pip install pandas mutagen
```

---

## Usage

### Export Metadata

Export metadata from MP3 files to a CSV file:

```bash
python3 transfer-mp3md.py export <mp3_directory> <output_csv>
```

* If `<output_csv>` exists, metadata is appended based on matching filenames.
* If `<output_csv>` does not exist, a new file is created.

### Import Metadata

Import metadata from a CSV file into your MP3 files:

```bash
python3 transfer-mp3md.py import <input_csv> <mp3_directory>
```

The tool matches MP3 files with the filenames listed in the CSV and updates their metadata accordingly.

---

## CSV Format

The CSV file includes the following columns:

* `filename`
* `title`
* `artist`
* `album`
* `tracknumber`
* `genre`
* `date`
* `composer`
* `comments`

Empty fields are left blank in the CSV, not replaced with `nan`.

---

## License

This tool is provided under the Creative Commons CC0 1.0 Universal (CC0 1.0) Public Domain Dedication. You may freely modify, distribute, and use this script without any restrictions.
