#!/usr/bin/env python3
"""
transfer-mp3md.py – Export and import MP3 ID3 metadata to/from CSV, now including disc number
(with fallback from TXXX frames), and an in-place per-folder progress bar.

Usage:
    python transfer-mp3md.py export [--length-format {mm:ss,seconds}] <mp3_directory>... <output_csv>
    python transfer-mp3md.py import <input_csv> <mp3_directory>
"""

import os
import sys
import argparse
import json
import itertools

import pandas as pd
from pandas.errors import EmptyDataError
from mutagen.mp3 import MP3
from mutagen.id3 import (
    ID3, ID3NoHeaderError,
    TIT2, TPE1, TALB, TRCK, TPOS, TXXX, TCON, TDRC,
    TCOM, COMM, USLT, SYLT
)


def export_metadata(mp3_dirs, csv_path, length_format):
    """
    Export metadata from each mp3 directory with a per-folder progress bar.
    """
    records = []
    bar_width = 30

    for d in mp3_dirs:
        if not os.path.isdir(d):
            print(f"Warning: '{d}' is not a directory, skipping.", file=sys.stderr)
            continue

        # Gather MP3s in this directory
        dir_files = []
        for root, _, files in os.walk(d):
            for f in files:
                if f.lower().endswith('.mp3'):
                    dir_files.append(os.path.join(root, f))

        total = len(dir_files)
        if total == 0:
            print(f"No MP3s found in '{d}', skipping.")
            continue

        spinner = itertools.cycle("|/-\\")
        for idx, full_path in enumerate(dir_files, start=1):
            basename = os.path.basename(full_path)

            # read length & bitrate
            audio = MP3(full_path)
            secs = int(audio.info.length)
            if length_format == "seconds":
                length = str(secs)
            else:
                m, s = divmod(secs, 60)
                length = f"{m}:{s:02d}"
            bitrate_kbps = audio.info.bitrate // 1000

            # read ID3 tags
            try:
                id3 = ID3(full_path)
            except ID3NoHeaderError:
                id3 = ID3()

            def get_txt(frame):
                return id3.get(frame).text[0] if id3.get(frame) else ""

            # disc: TPOS or fallback to TXXX desc "disc"/"disk"
            disc = get_txt("TPOS")
            if not disc:
                for txxx in id3.getall("TXXX"):
                    if txxx.desc.strip().lower() in ("disc", "disk"):
                        disc = txxx.text[0]
                        break

            comms = id3.getall("COMM")
            rec = {
                "filename":    basename,
                "title":       get_txt("TIT2"),
                "artist":      get_txt("TPE1"),
                "album":       get_txt("TALB"),
                "tracknumber": get_txt("TRCK"),
                "disc":        disc,
                "genre":       get_txt("TCON"),
                "date":        get_txt("TDRC"),
                "composer":    get_txt("TCOM"),
                "comments":    (comms[0].text[0] if comms else ""),
                "length":      length,
                "bitrate":     bitrate_kbps
            }

            uslt = id3.getall("USLT")
            if uslt:
                text = uslt[0].text
                rec["lyrics"] = text if isinstance(text, str) else text[0]

            sync = id3.getall("SYLT")
            if sync:
                entries = []
                for f2 in sync:
                    for text2, ts in zip(f2.text, f2.time):
                        entries.append({"ts_ms": ts, "text": text2})
                rec["synced_lyrics"] = json.dumps(entries, ensure_ascii=False)

            records.append(rec)

            # update this folder's progress bar
            filled = int(idx / total * bar_width)
            bar = "=" * filled + " " * (bar_width - filled)
            spin = next(spinner)
            sys.stdout.write(f"\r[{bar}] {spin} {d}: {idx}/{total}")
            sys.stdout.flush()

        # once done with this folder, move to next line
        sys.stdout.write("\n")

    # write all records to CSV (appending if exists)
    df_new = pd.DataFrame(records)
    try:
        df_exist = pd.read_csv(csv_path, encoding="utf-8-sig", keep_default_na=False)
        has_data = not df_exist.empty
    except (FileNotFoundError, EmptyDataError):
        df_exist = None
        has_data = False

    if has_data:
        existing_cols = list(df_exist.columns)
        missing = [c for c in df_new.columns if c not in existing_cols]
        if missing:
            for c in missing:
                df_exist[c] = ""
            existing_cols += missing
            df_exist.to_csv(csv_path, index=False, columns=existing_cols,
                            encoding="utf-8-sig", na_rep="")
        df_new.to_csv(csv_path, mode="a", header=False,
                      index=False, columns=existing_cols,
                      encoding="utf-8-sig", na_rep="")
        print(f"Appended {len(df_new)} rows to {csv_path}")
    else:
        df_new.to_csv(csv_path, index=False, encoding="utf-8-sig", na_rep="")
        print(f"Exported {len(df_new)} records to new CSV at {csv_path}")


def import_metadata(csv_path, mp3_dir):
    """
    Import metadata from CSV to MP3 files with a simple progress counter.
    """
    try:
        df = pd.read_csv(csv_path, encoding="utf-8-sig", keep_default_na=False)
    except FileNotFoundError:
        print(f"Error: '{csv_path}' not found.", file=sys.stderr)
        return

    df.fillna("", inplace=True)
    df.rename(columns=lambda c: c.strip().lower(), inplace=True)

    if "filename" not in df.columns:
        print("Error: 'filename' column not found.", file=sys.stderr)
        return

    total = len(df)
    updated = 0

    for idx, row in df.iterrows():
        fn = row["filename"]
        full_path = os.path.join(mp3_dir, fn)
        if not os.path.isfile(full_path):
            continue

        sys.stdout.write(f"\rImporting {idx+1}/{total}: {fn}")
        sys.stdout.flush()

        try:
            tags = ID3(full_path)
        except ID3NoHeaderError:
            tags = ID3()

        for frame in ("TIT2","TPE1","TALB","TRCK","TPOS","TCON","TDRC",
                      "TCOM","COMM","USLT","SYLT","TXXX"):
            tags.delall(frame)

        if row.get("title"):
            tags.add(TIT2(encoding=3, text=[row["title"]]))
        if row.get("artist"):
            tags.add(TPE1(encoding=3, text=[row["artist"]]))
        if row.get("album"):
            tags.add(TALB(encoding=3, text=[row["album"]]))
        if row.get("tracknumber"):
            tags.add(TRCK(encoding=3, text=[str(row["tracknumber"])]))
        if row.get("disc"):
            tags.add(TPOS(encoding=3, text=[str(row["disc"])]))
        if row.get("genre"):
            tags.add(TCON(encoding=3, text=[row["genre"]]))
        if row.get("date"):
            tags.add(TDRC(encoding=3, text=[row["date"]]))
        if row.get("composer"):
            tags.add(TCOM(encoding=3, text=[row["composer"]]))
        if row.get("comments"):
            tags.add(COMM(encoding=3, desc="", lang="eng", text=[row["comments"]]))

        if "lyrics" in df.columns and row["lyrics"]:
            tags.add(USLT(encoding=3, desc="", lang="eng", text=[row["lyrics"]]))
        if "synced_lyrics" in df.columns and row["synced_lyrics"]:
            entries = json.loads(row["synced_lyrics"])
            texts = [e["text"] for e in entries]
            times = [e["ts_ms"] for e in entries]
            tags.add(SYLT(encoding=3, desc="", lang="eng", type=1,
                          text=texts, time=times))

        tags.save(full_path, v2_version=4)
        updated += 1

    sys.stdout.write("\n")
    print(f"Updated metadata for {updated}/{total} files from {csv_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Export/import MP3 metadata ↔ CSV (UTF-8), storing only filenames."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_exp = sub.add_parser("export", help="Export MP3 metadata to CSV")
    p_exp.add_argument("mp3_dirs", nargs="+", help="Directories to scan")
    p_exp.add_argument("csv_path", help="Output CSV path")
    p_exp.add_argument(
        "--length-format", choices=["mm:ss", "seconds"], default="mm:ss",
        help="Format for track length"
    )

    p_imp = sub.add_parser("import", help="Import metadata from CSV to MP3 files")
    p_imp.add_argument("csv_path", help="Input CSV path")
    p_imp.add_argument("mp3_dir", help="Directory of MP3s to update")

    args = parser.parse_args()
    if args.command == "export":
        export_metadata(args.mp3_dirs, args.csv_path, args.length_format)
    else:
        import_metadata(args.csv_path, args.mp3_dir)


if __name__ == "__main__":
    main()
