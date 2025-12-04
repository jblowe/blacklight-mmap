#!/usr/bin/env python3
"""
make_report.py — generates standalone HTML report for merged_sites.tsv

Features:
  - Clean left metadata column grouped by headings.
  - Geographic Info section:
      * Left: nested table with all geo metadata.
      * Right: map thumbnail + Google Map link (embed on screen only).
  - Right column: large main image + up to 3 small thumbnails below it.
  - Omit empty rows, omit empty sections, omit image types with no images.
  - All styling in a <style> block, including @media print for PDF-friendly output:
      * metadata + images remain side-by-side
      * Google Maps iframe hidden in print
"""

import csv
import sys
import html
from typing import Dict, List, Tuple


URL_PREFIX = "http://localhost:3002/mmap-images/"                 # for local infrared server
# URL_PREFIX = "https://mmap-infrared.johnblowe.com/mmap-images/"   # for jbs aws instance


# === LABEL → FIELD MAPPING ====================================================
label_to_field: Dict[str, str] = {
    # --- Site Info ---
    "Site Info": "heading",
    "Site:": "site_name_s",
    "Description:": "sitedesc_s",
    "Date Recorded:": "year_recorded_s",
    "Access:": "acces_s",
    "Nearest Village:": "vill_name_s",
    "Closest River:": "nrprimrv_s",
    "Closest Stream:": "nrsecrv_s",
    "Visit Comments:": "visit_comm_s",
    "Excavation Priority:": "exc_pri_s",

    # --- Geographic Info ---
    "Geographic Info": "heading",
    "Latitude:": "point_y_s",
    "Longitude:": "point_x_s",
    "Length:": "dimena_s",
    "Width:": "dimenb_s",
    "Min Depth:": "estdepth_s",
    "Max Depth:": "",
    "Time Spent:": "time_spent_s",

    # --- Site Characteristics ---
    "Site Characteristics": "heading",
    "Site Characteristics:": "site_characteristics_s",
    "Site Characteristics Comments:": "site_comm_s",

    # --- Site Conditions ---
    "Site Conditions": "heading",
    "Site Conditions Comments:": "condcomm_s",
    "Caves:": "cave_fl_s",

    # --- Recent Disturbance ---
    "Recent Disturbance": "heading",
    "Distubance:": "recent_disturbance_s",
    "Disturbance Comments:": "distcomm_s",

    # --- Past Site Functions ---
    "Past Site Functions": "heading",
    "Past Site Function:": "past_site_functions_s",
    "Past Functions Comments:": "pastfcomm_s",

    # --- Environmental Conditions ---
    "Environmental Conditions": "heading",
    "Environment:": "environment_s",
    "Environmental Comments:": "envcomm_s",
    "Vegetation:": "natveg_s",

    # --- Artifact Info ---
    "Artifact Info": "heading",
    "Artifacts Present:": "artifacts_present_s",
    "Artifacts:": "oth_art_s",
    "Artifact Comments:": "artcomm_s",
}


# Image types: Map handled separately in Geographic Info
IMAGE_TYPES: List[Tuple[str, str]] = [
    ("General view", "General_view_THUMBNAILS_ss"),
    ("Artifacts", "Artifacts_THUMBNAILS_ss"),
    ("Misc", "Misc_THUMBNAILS_ss"),
    ("People", "People_THUMBNAILS_ss"),
]


# === HELPERS ==================================================================

def escape(s: str) -> str:
    return html.escape(s or "", quote=True)


def build_image_url(path: str) -> str:
    if not path:
        return ""
    return f"{URL_PREFIX}{path}"


def get_thumb_list(raw: str) -> List[str]:
    if not raw:
        return []
    return [p.strip() for p in raw.split("|") if p.strip()]


def get_filename(path: str) -> str:
    if not path:
        return ""
    return path.replace("\\", "/").split("/")[-1]


# === METADATA COLUMN RENDERING ===============================================

def render_metadata_column(row: dict) -> str:
    """Build the entire metadata column including Geographic Info map block."""
    sections = []
    current_heading = None
    current_rows: List[Tuple[str, str]] = []

    def flush():
        nonlocal current_heading, current_rows, sections
        if current_heading and current_rows:
            sections.append({"heading": current_heading, "rows": current_rows})
        current_heading = None
        current_rows = []

    for label, field in label_to_field.items():
        if field == "heading":
            flush()
            current_heading = label
            current_rows = []
            continue

        if not field:
            continue
        v = (row.get(field) or "").strip()
        if not v:
            continue
        current_rows.append((label, v))

    flush()

    html_parts: List[str] = []

    for sec in sections:
        heading = sec["heading"]
        rows = sec["rows"]

        html_parts.append(f'<h3 class="sec-heading">{escape(heading)}</h3>')

        if heading == "Geographic Info":
            # Map thumbnail & coords
            map_raw = (row.get("Map_THUMBNAILS_ss") or "").strip()
            thumbs = get_thumb_list(map_raw)
            map_thumb = thumbs[0] if thumbs else ""
            map_url = build_image_url(map_thumb)
            map_title = get_filename(map_thumb)

            lat = (row.get("point_y_s") or "").strip()
            lon = (row.get("point_x_s") or "").strip()
            have_coords = bool(lat and lon)
            have_3rdcol = bool(map_thumb or have_coords)

            # Nested table for geo metadata
            meta_rows_html = []
            for label, value in rows:
                meta_rows_html.append(
                    "<tr>"
                    f"<th class='meta-label'>{escape(label)}</th>"
                    f"<td class='meta-value'>{escape(value)}</td>"
                    "</tr>"
                )
            meta_rows_str = "".join(meta_rows_html)

            html_parts.append('<table class="meta-table"><tbody><tr>')
            # Left side: nested table with geo metadata
            html_parts.append(
                "<td class='geo-meta-cell' colspan='2'>"
                "<table class='meta-table-inner'><tbody>"
                f"{meta_rows_str}"
                "</tbody></table>"
                "</td>"
            )

            # Right side: maps column (if anything to show)
            if have_3rdcol:
                html_parts.append("<td class='geo-extra'>")

                if map_thumb:
                    html_parts.append(
                        f'<img src="{escape(map_url)}" '
                        f'title="{escape(map_title)}" '
                        'class="geo-map-thumb" />'
                    )

                if have_coords:
                    emb = (
                        f"https://www.google.com/maps?q={escape(lat)},"
                        f"{escape(lon)}&z=14&output=embed"
                    )
                    link = (
                        f"https://www.google.com/maps?q={escape(lat)},"
                        f"{escape(lon)}&z=14"
                    )
                    html_parts.append(
                        f'<iframe src="{emb}" class="geo-iframe" '
                        'loading="lazy"></iframe>'
                    )
                    html_parts.append(
                        f'<div><a href="{link}" target="_blank" '
                        'class="geo-link">Open in Google Maps</a></div>'
                    )

                html_parts.append("</td>")

            html_parts.append("</tr></tbody></table>")

        else:
            # Normal section
            html_parts.append('<table class="meta-table"><tbody>')
            for label, value in rows:
                html_parts.append(
                    "<tr>"
                    f"<th class='meta-label'>{escape(label)}</th>"
                    f"<td class='meta-value'>{escape(value)}</td>"
                    "</tr>"
                )
            html_parts.append("</tbody></table>")

    return "\n".join(html_parts)


# === IMAGES COLUMN RENDERING ==================================================

def render_images_column(row: dict) -> str:
    parts: List[str] = []

    for type_label, field_name in IMAGE_TYPES:
        raw = (row.get(field_name) or "").strip()
        thumbs = get_thumb_list(raw)
        if not thumbs:
            continue

        main = thumbs[0]
        extras = thumbs[1:4]  # up to 3 more
        main_url = build_image_url(main)
        main_title = get_filename(main)

        parts.append('<div class="img-type-block">')
        parts.append(f'<div class="img-type-heading">{escape(type_label)}</div>')

        # Main image
        parts.append(
            f'<img src="{escape(main_url)}" '
            f'title="{escape(main_title)}" '
            'class="img-main" />'
        )

        # Extra thumbnails
        if extras:
            parts.append('<div class="img-small-row">')
            for t in extras:
                url = build_image_url(t)
                title = get_filename(t)
                parts.append(
                    f'<img src="{escape(url)}" '
                    f'title="{escape(title)}" '
                    'class="img-small" />'
                )
            parts.append("</div>")

        parts.append("</div>")  # end type block

    return "\n".join(parts)


# === MAIN SITE CARD RENDERING =================================================

def render_site_div(row: dict) -> str:
    site_name = escape(row.get("site_name_s", ""))

    meta_html = render_metadata_column(row)
    img_html = render_images_column(row)

    return f"""
<div class="site-card">
  <h2 class="site-title">{site_name}</h2>
  <div class="row-flex">
    <div class="col-left">{meta_html}</div>
    <div class="col-right">{img_html}</div>
  </div>
</div>
"""


# === MAIN =====================================================================

def main():
    if len(sys.argv) != 2:
        print("Usage: python make_report.py merged_sites.tsv > report.html")
        sys.exit(1)

    path = sys.argv[1]
    delim = '\t'

    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter=delim)
        rows = list(reader)

    print("<!DOCTYPE html><html><head><meta charset='utf-8'>")
    print("<title>Site Report</title>")

    # ===================== CSS STYLESHEET =======================
    print(r"""
<style>
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto,
                 'Helvetica Neue', Arial, sans-serif;
    background: #f8f9fa;
    padding: 16px;
    font-size: 14px;
}

.site-card {
    background: #fff;
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 12px;
    margin-bottom: 20px;
    box-shadow: 0 1px 2px rgba(0,0,0,0.03);
}

.site-title {
    margin: 0 0 12px 0;
    font-size: 1.4rem;
}

.row-flex {
    display: flex;
    gap: 16px;
}

.col-left,
.col-right {
    width: 50%;
}

/* ----- Section Headings ----- */
.sec-heading {
    margin: 10px 0 4px 0;
    padding-bottom: 3px;
    border-bottom: 1px solid #ddd;
    font-size: 1.1rem;
}

/* ----- Metadata tables ----- */
.meta-table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 8px;
}

.meta-table-inner {
    width: 100%;
    border-collapse: collapse;
}

.meta-label {
    text-align: left;
    vertical-align: top;
    width: 40%;
    padding: 3px 4px;
    font-weight: 600;
}

.meta-value {
    vertical-align: top;
    padding: 3px 4px;
}

/* ----- Geo section extras ----- */
.geo-meta-cell {
    vertical-align: top;
    padding-right: 6px;
}

.geo-extra {
    vertical-align: top;
    width: 30%;
    padding-left: 6px;
}

.geo-map-thumb {
    max-width: 130px;
    border: 1px solid #ccc;
    border-radius: 2px;
    padding: 2px;
    margin-bottom: 6px;
}

.geo-iframe {
    width: 130px;
    height: 130px;
    border: 0;
    margin-bottom: 4px;
}

.geo-link {
    font-size: 0.85rem;
}

/* ----- Image column ----- */
.img-type-block {
    margin-bottom: 20px;
}

.img-type-heading {
    font-weight: bold;
    margin-bottom: 4px;
}

.img-main {
    max-width: 100%;
    height: auto;
    border: 1px solid #ccc;
    padding: 2px;
    border-radius: 2px;
}

.img-small-row {
    margin-top: 6px;
    display: flex;
    gap: 4px;
}

.img-small {
    flex: 0 0 32%;
    max-width: 32%;
    border: 1px solid #ccc;
    border-radius: 2px;
    height: auto;
    padding: 2px;
}

/* ----- Print / PDF optimization ----- */
@media print {
    @page {
        margin: 0.25in;
    }

    body {
        background: #ffffff;
        padding: 0;
        font-size: 11px;
    }

    .site-card {
        box-shadow: none;
        border: 1px solid #000;
        margin-bottom: 10px;
        page-break-inside: avoid;
    }

    /* Keep columns side-by-side on paper */
    .row-flex {
        flex-direction: row;
        gap: 8px;
    }

    .col-left,
    .col-right {
        width: 50%;
    }

    .site-title {
        font-size: 1.1rem;
        margin-bottom: 8px;
    }

    .sec-heading {
        font-size: 0.95rem;
        margin: 6px 0 3px 0;
        padding-bottom: 2px;
    }

    .meta-label,
    .meta-value {
        padding: 2px 3px;
        font-size: 0.9em;
    }

    .meta-table {
        margin-bottom: 4px;
    }

    .geo-map-thumb {
        max-width: 110px;
    }

    /* Hide Google Maps iframe in print (browsers won't render it anyway) */
    .geo-iframe {
        display: none !important;
    }

    .geo-link {
        display: block;
        font-size: 0.85rem;
        margin-top: 4px;
        text-decoration: underline;
    }

    /* Main images stay readable but not crazy huge */
    .img-main {
        max-width: 100%;
    }

    /* Small thumbs stay small even in print */
    .img-small-row {
        display: flex;
        gap: 3px;
    }

    .img-small {
        flex: 0 0 32%;
        max-width: 32%;
    }

    a {
        color: #000;
        text-decoration: underline;
    }
}
</style>
""")

    print("</head><body><div style='max-width:1200px; margin:0 auto;'>")

    for row in rows:
        print(render_site_div(row))

    print("</div></body></html>")


if __name__ == "__main__":
    main()
