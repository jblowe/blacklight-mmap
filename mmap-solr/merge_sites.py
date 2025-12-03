#!/usr/bin/env python3
"""
merge_sites.py

Merge archaeological site records with per-site photo records, grouped by TYPE_s.

Inputs are *tab-separated* text files:

  1) mmap-dbsites.csv
       - One row per site (105 rows in our case)
       - Key column: site_name_s
       - All columns are carried through to the output.

  2) mmap-site-photos.csv
       - One row per photo (4,480 rows in our case)
       - Key column: SITE_s
       - Columns: THUMBNAIL_ss, DATE_s, SITE_s, TYPE_s, FILENAME_s

For each site and TYPE_s, the script concatenates values of:
    - FILENAME_s      -> into a column named "<TYPE_s>_FILENAME_ss"
    - THUMBNAIL_ss    -> into a column named "<TYPE_s>_THUMBNAILS_ss"

Concatenated values use "|" as a separator.
The output file is "|" separated as well.

Usage:
    python merge_sites.py mmap-dbsites.csv mmap-site-photos.csv merged_sites.csv
"""

import csv
import sys
from collections import defaultdict

IN_DELIM = "\t"   # input files are tab-separated
OUT_DELIM = "\t"   # output file uses tabs too
JOIN_DELIM = "|"  # concatenation delimiter for multi-values


def read_photo_data(photos_path):
    """
    Read mmap-site-photos.csv (tab-separated) and build:

      - type_order: list of TYPE_s values in order of first appearance
      - photos_by_site_type: dict[site_name][type] -> {
            "FILENAME_s": [ ... ],
            "THUMBNAIL_ss": [ ... ]
        }
    """
    type_order = []
    seen_types = set()

    # photos_by_site_type[SITE_s][TYPE_s] = {"FILENAME_s": [...], "THUMBNAIL_ss": [...]}
    photos_by_site_type = defaultdict(
        lambda: defaultdict(lambda: {"FILENAME_s": [], "THUMBNAIL_ss": []})
    )

    with open(photos_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=IN_DELIM)
        for row in reader:
            site = (row.get("SITE_s") or "").strip()
            t = (row.get("TYPE_s") or "").strip()

            # Track types in the order first seen
            if t and t not in seen_types:
                seen_types.add(t)
                type_order.append(t)

            # Append filenames and thumbnails
            if site and t:
                photos_by_site_type[site][t]["FILENAME_s"].append(
                    (row.get("FILENAME_s") or "").strip()
                )
                photos_by_site_type[site][t]["THUMBNAIL_ss"].append(
                    (row.get("THUMBNAIL_ss") or "").strip()
                )

    return type_order, photos_by_site_type


def merge_sites(sites_path, photos_path, out_path):
    # 1. Read photo data and aggregate by site and type
    type_order, photos_by_site_type = read_photo_data(photos_path)

    # 2. Read site table
    with open(sites_path, newline="", encoding="utf-8") as f:
        site_reader = csv.DictReader(f, delimiter=IN_DELIM)
        site_rows = list(site_reader)
        site_fieldnames = site_reader.fieldnames or []

    # 3. Build output header: original site columns + 2 columns per TYPE_s
    out_fieldnames = list(site_fieldnames)
    for t in type_order:
        out_fieldnames.append(f"{t}_FILENAME_ss")
        out_fieldnames.append(f"{t}_THUMBNAILS_ss")

    # 4. Merge photo info into site rows
    merged_rows = []

    main_site_names = set()
    for row in site_rows:
        main_site_names.add((row.get("site_name_s") or "").strip())

    photo_site_names = set(photos_by_site_type.keys())

    missing_in_photos = []
    for row in site_rows:
        site_name = (row.get("site_name_s") or "").strip()
        per_type = photos_by_site_type.get(site_name, {})

        # For each type, concatenate FILENAME_s and THUMBNAIL_ss with "|"
        for t in type_order:
            files = per_type.get(t, {}).get("FILENAME_s", [])
            thumbs = per_type.get(t, {}).get("THUMBNAIL_ss", [])

            row[f"{t}_FILENAME_ss"] = JOIN_DELIM.join(f for f in files if f)
            row[f"{t}_THUMBNAILS_ss"] = JOIN_DELIM.join(th for th in thumbs if th)

        if site_name not in photos_by_site_type:
            missing_in_photos.append(site_name)

        merged_rows.append(row)

    # 5. Write sorted output as pipe-separated
    merged_rows = sorted(merged_rows, key=lambda x: str(x['site_name_s']))
    with open(out_path, "w", newline="", encoding="utf-8") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=out_fieldnames, delimiter=OUT_DELIM)
        writer.writeheader()
        for row in merged_rows:
            writer.writerow(row)

    # 6. Report mismatches, including site names
    extra_sites_in_photos = sorted(photo_site_names - main_site_names)
    uncovered_sites_in_main = sorted(main_site_names - photo_site_names)

    sys.stderr.write(
        f"Read {len(site_rows)} site rows from {sites_path}\n"
        f"Read {sum(len(photos_by_site_type[s]) for s in photos_by_site_type)} "
        f"sites-with-photos entries from {photos_path}\n"
        f"Found TYPE_s values (in order): {', '.join(type_order)}\n"
        f"Sites with no photos (present in database only): {len(uncovered_sites_in_main)}\n"
    )
    if uncovered_sites_in_main:
        sys.stderr.write("  These sites are in mmap-dbsites.csv but not in mmap-site-photos.csv:\n")
        for s in uncovered_sites_in_main:
            sys.stderr.write(f"    {s}\n")

    sys.stderr.write(
        f"Sites present in photos but missing from database: {len(extra_sites_in_photos)}\n"
    )
    if extra_sites_in_photos:
        sys.stderr.write("  These sites are in mmap-site-photos.csv but not in mmap-dbsites.csv:\n")
        for s in extra_sites_in_photos:
            sys.stderr.write(f"    {s}\n")


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    if len(argv) != 3:
        sys.stderr.write(
            "Usage: python merge_sites.py "
            "mmap-dbsites.csv mmap-site-photos.csv merged_sites.csv\n"
        )
        sys.exit(1)

    sites_path, photos_path, out_path = argv
    merge_sites(sites_path, photos_path, out_path)


if __name__ == "__main__":
    main()
