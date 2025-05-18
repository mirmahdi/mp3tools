#!/usr/bin/env python3
"""
transfer-mp3md.py - Export and import MP3 ID3 metadata to/from CSV

Usage:
    python3 transfer-mp3md.py export <mp3_directory> <output_csv>
    python3 transfer-mp3md.py import <input_csv> <mp3_directory>

Commands:
    export  Scan the specified directory for .mp3 files, read ID3 tags, and export metadata to a CSV file.
    import  Read metadata from a CSV file and write the tags back into the corresponding MP3 files.

Notes:
    - The export operation will append records to an existing CSV file if it already contains data,
      matching on the 'filename' column, or create a new CSV otherwise.
    - CSV columns include: filename, title, artist, album, tracknumber, genre, date, composer, comments.
    - Empty fields are written as blank cells (no 'nan').
    - The import operation writes only columns present in the CSV back to the MP3 files.

Created: 2025-05-12
"""
import os
import sys
import argparse
import pandas as pd
from pandas.errors import EmptyDataError
from mutagen.id3 import ID3, ID3NoHeaderError
from mutagen.id3 import (
    TIT2, TPE1, TALB, TRCK, TCON, TDRC,
    TCOM, COMM
)


def export_metadata(mp3_dir: str, csv_path: str):
    """
    Export MP3 metadata from mp3_dir into csv_path.
    CSV columns: filename, title, artist, album, tracknumber,
                 genre, date, composer, comments.
    Empty metadata fields are exported as blank cells.
    """
    # Validate source directory
    if not os.path.isdir(mp3_dir):
        print(f"Error: '{mp3_dir}' is not a directory.", file=sys.stderr)
        sys.exit(1)

    records = []
    # Collect metadata for every .mp3 file
    for root, _, files in os.walk(mp3_dir):
        for fname in files:
            if not fname.lower().endswith('.mp3'):
                continue
            full_path = os.path.join(root, fname)
            basename = os.path.basename(full_path)

            # Load existing tags or initialize new
            try:
                id3 = ID3(full_path)
            except ID3NoHeaderError:
                id3 = ID3()

            # Helper: get first text of a frame or ''
            get_txt = lambda frame: id3.get(frame).text[0] if id3.get(frame) else ''
            comms = id3.getall('COMM')  # comment frames

            records.append({
                'filename':     basename,
                'title':        get_txt('TIT2'),
                'artist':       get_txt('TPE1'),
                'album':        get_txt('TALB'),
                'tracknumber':  get_txt('TRCK'),
                'genre':        get_txt('TCON'),
                'date':         get_txt('TDRC'),
                'composer':     get_txt('TCOM'),
                'comments':     comms[0].text[0] if comms else '',
            })

    df_new = pd.DataFrame(records)
    # Determine if existing CSV has data
    try:
        df_existing = pd.read_csv(csv_path, encoding='utf-8-sig')
        has_data = not df_existing.empty
    except (FileNotFoundError, EmptyDataError):
        has_data = False

    if has_data:
        # Match columns with existing CSV header order
        existing_cols = pd.read_csv(csv_path, nrows=0, encoding='utf-8-sig').columns.tolist()
        cols_to_write = ['filename'] + [c for c in existing_cols if c in df_new.columns and c != 'filename']
        if len(cols_to_write) == 1:
            print(f"Warning: no matching columns to append to {csv_path}", file=sys.stderr)
        else:
            # Append without header; blank values remain blank
            df_new.to_csv(
                csv_path,
                mode='a',
                index=False,
                header=False,
                columns=cols_to_write,
                encoding='utf-8-sig',
                na_rep=''  # ensure no 'nan' in output
            )
            print(f"Appended {len(df_new)} rows to {csv_path} (columns: {cols_to_write})")
    else:
        # Write full CSV; blank cells for missing data
        df_new.to_csv(
            csv_path,
            index=False,
            encoding='utf-8-sig',
            na_rep=''  # ensure no 'nan' in output
        )
        print(f"Exported {len(df_new)} records to new CSV at {csv_path}")


def import_metadata(csv_path: str, mp3_dir: str):
    """
    Read csv_path (with filename + metadata), rebuild full path, and write tags back.
    Empty fields in CSV should be left blank and not treated as NaN.
    """
    # Validate paths
    if not os.path.isdir(mp3_dir):
        print(f"Error: '{mp3_dir}' is not a directory.", file=sys.stderr)
        sys.exit(1)
    if not os.path.isfile(csv_path):
        print(f"Error: CSV file '{csv_path}' not found.", file=sys.stderr)
        sys.exit(1)

    # Read CSV, disable default NA parsing to keep blanks blank
    df = pd.read_csv(csv_path, encoding='utf-8-sig', keep_default_na=False)
    # Replace any NaN (if present) with empty string
    df.fillna('', inplace=True)

    # Normalize column names
    df.rename(columns=lambda c: c.strip().lower(), inplace=True)
    if 'filename' not in df.columns:
        print("Error: 'filename' column not found in CSV.", file=sys.stderr)
        sys.exit(1)

    updated = 0
    for idx, row in df.iterrows():
        fn = row['filename']
        if not fn:
            print(f"Warning: missing filename on row {idx}, skipping.", file=sys.stderr)
            continue
        full_path = os.path.join(mp3_dir, fn)
        if not os.path.isfile(full_path):
            print(f"Warning: '{full_path}' not found, skipping.", file=sys.stderr)
            continue

        try:
            tags = ID3(full_path)
        except ID3NoHeaderError:
            tags = ID3()

        # Clear existing standard frames
        for frame in ('TIT2','TPE1','TALB','TRCK','TCON','TDRC','TCOM','COMM'):
            tags.delall(frame)

        # Add back frames only if non-empty in CSV
        if row.get('title'):
            tags.add(TIT2(encoding=3, text=[row['title']]))
        if row.get('artist'):
            tags.add(TPE1(encoding=3, text=[row['artist']]))
        if row.get('album'):
            tags.add(TALB(encoding=3, text=[row['album']]))
        if row.get('tracknumber'):
            tags.add(TRCK(encoding=3, text=[str(row['tracknumber'])]))
        if row.get('genre'):
            tags.add(TCON(encoding=3, text=[row['genre']]))
        if row.get('date'):
            tags.add(TDRC(encoding=3, text=[row['date']]))
        if row.get('composer'):
            tags.add(TCOM(encoding=3, text=[row['composer']]))
        if row.get('comments'):
            tags.add(COMM(encoding=3, lang='eng', desc='', text=[row['comments']]))

        tags.save(full_path, v2_version=4)
        updated += 1

    print(f"Updated metadata for {updated} files from {csv_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Export/import MP3 metadata ↔ CSV (UTF-8), storing only filenames."
    )
    sub = parser.add_subparsers(dest='command', required=True)
    p_exp = sub.add_parser('export', help='Export MP3 metadata to CSV')
    p_exp.add_argument('mp3_dir',  help='Directory of MP3 files to export')
    p_exp.add_argument('csv_path', help='Output CSV file path')
    p_imp = sub.add_parser('import', help='Import metadata from CSV to MP3 files')
    p_imp.add_argument('csv_path', help='Input CSV file path')
    p_imp.add_argument('mp3_dir',  help='Directory of MP3 files to update')

    args = parser.parse_args()
    if args.command == 'export':
        export_metadata(args.mp3_dir, args.csv_path)
    else:
        import_metadata(args.csv_path, args.mp3_dir)


if __name__ == '__main__':
    main()
