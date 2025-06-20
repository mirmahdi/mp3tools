#!/usr/bin/env python3
"""
md-csv2json.py

Convert one or more MP3 metadata CSV files (or directories of CSVs) into a single combined JSON index.

This script:
  - Accepts file and/or directory paths on the CLI.
  - If a path is a directory, it reads all `.csv` files inside.
  - If a path is a `.csv` file, it processes that single file.
  - Maps each row’s album or genre name (in Farsi) to a 3–4 letter English acronym.
  - Builds a composite key `<ACRONYM>|<filename>` for each track.
  - Assembles a metadata object for each track with fields:
      - file_id (None placeholder)
      - genre (original Farsi name)
      - title, artist, album, composer, poet
      - length (seconds), lyrics (optional), disc (from CSV), tags (empty list)
      - bitrate, sample_rate (None)
  - Writes the combined dictionary to `mp3-metadata.json` in the same folder as the first input path.

Usage:
    python md-csv2json.py <path_to_csv_or_directory> [<additional_paths>...]

Example:
    python md-csv2json.py ./metadata_csvs metadata.csv
"""
import os
import sys
import json
import pandas as pd

# Mapping from Farsi genre/album names to English acronyms
GENRE_ACRONYMS = {
    "دستگاه ماهور":        "MHUR",
    "دستگاه چهارگاه":      "CHGH",
    "دستگاه سه‌گاه":        "SGAH",
    "دستگاه همایون":       "HMYN",
    "آواز اصفهان":         "H-ESF",
    "دستگاه نوا":          "NAVA",
    "دستگاه راست‌پنجگاه":   "RSTP",
    "دستگاه شور":          "SHUR",
    "آواز ابوعطا":         "S-ABT",
    "آواز افشاری":         "S-AFS",
    "آواز بیات‌ترک":        "S-TRK",
    "آواز دشتی":           "S-DST",
}

def convert_csvs_to_json(inputs):
    """
    Process each input path (file or directory), read CSV(s), and build combined JSON.
    """
    combined = {}
    csv_files = []

    # === Collect all CSV files from inputs ===
    for p in inputs:
        if os.path.isdir(p):
            for fname in os.listdir(p):
                if fname.lower().endswith('.csv'):
                    csv_files.append(os.path.join(p, fname))
        elif os.path.isfile(p) and p.lower().endswith('.csv'):
            csv_files.append(p)
        else:
            print(f"Warning: '{p}' is not a CSV or directory, skipping.", file=sys.stderr)

    if not csv_files:
        sys.exit("❌ No CSV files found to process.")

    # === Read each CSV and merge records ===
    for csv_path in csv_files:
        df = pd.read_csv(csv_path, keep_default_na=False)

        for _, row in df.iterrows():
            # Determine Farsi genre/album name and map to acronym
            genre_name = row.get('album', '').strip() or row.get('genre', '').strip()
            acronym    = GENRE_ACRONYMS.get(genre_name)
            filename   = row.get('filename', '').strip()

            # Skip if missing essential data
            if not acronym or not filename:
                continue

            # key = f"{acronym}|{filename}"
            base_name = os.path.splitext(filename)[0]   # drops the “.mp3”
            key       = f"{acronym}|{base_name}"            

            # Parse fields, converting where necessary
            # Disc number
            disc_val = row.get('disc', '').strip()
            try:
                disc = int(disc_val) if disc_val else None
            except ValueError:
                disc = disc_val

            # Length in seconds
            length_val = row.get('length')
            length = int(length_val) if pd.notna(length_val) and length_val != '' else None

            # Bitrate in kbps
            bitrate_val = row.get('bitrate')
            bitrate = int(bitrate_val) if pd.notna(bitrate_val) and bitrate_val != '' else None

            combined[key] = {
                "filename":     filename,
                "title":        row.get('title', '').strip(),
                "artist":       row.get('artist', '').strip(),
                "genre":        row.get('album', '').strip(),
                "composer":     row.get('composer', '').strip(),
                "poet":         row.get('comments', '').strip(),
                "length":       length,
                "disc":         disc,
                "bitrate":      bitrate
            }

    # === Determine output directory (same as first input) ===
    first = inputs[0]
    out_dir = first if os.path.isdir(first) else os.path.dirname(first) or '.'
    output_path = os.path.join(out_dir, 'mp3-metadata.json')

    # === Write combined JSON ===
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(combined, f, ensure_ascii=False, indent=2)

    print(f"✅ JSON file created at: {output_path}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python md-csv2json.py <path_to_csv_or_directory> [...]")
        sys.exit(1)
    convert_csvs_to_json(sys.argv[1:])

if __name__ == '__main__':
    main()
