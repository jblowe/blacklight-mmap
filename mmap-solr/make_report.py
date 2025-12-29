#!/usr/bin/env python3
# make_report.py — generates standalone HTML report for merged_sites.tsv

import csv
import sys
import html
from datetime import datetime
from typing import Dict, List, Tuple
from report_i18n import label_to_field, IMAGE_TYPES


URL_PREFIX = "https://mmap.org"   # set this as needed for your thumbnails


# (label_to_field and IMAGE_TYPES are imported from report_i18n.py)



from pathlib import Path
import re


def read_snippet(path: str) -> str:
    """
    Read an HTML snippet file and return its contents.
    If the snippet contains a <body> wrapper, return only the <body> contents.
    """
    txt = Path(path).read_text(encoding="utf-8")
    m = re.search(r"<body[^>]*>(.*)</body>", txt, flags=re.IGNORECASE | re.DOTALL)
    if m:
        txt = m.group(1)
    return txt.strip()


def make_site_anchor(row: dict) -> str:
    """
    Create a stable anchor id for a site.
    Prefer siteid_s if present; else site_name_s.
    """
    raw = (row.get("siteid_s") or row.get("site_name_s") or "site").strip().lower()
    raw = re.sub(r"\s+", "-", raw)
    raw = re.sub(r"[^a-z0-9_-]+", "", raw)
    return "site-" + (raw or "site")


def render_front_matter() -> str:
    title_html = read_snippet("title_page.html")
    intro_html = read_snippet("introduction.html")
    return "\n".join([
        title_html.format(DATE=datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        '<div class="page-break"></div>',
        intro_html,
        '<div class="page-break"></div>',
    ])


def render_index(rows: List[dict]) -> str:
    """
    Index keyed by Closest River (nrprimrv_s). Links to anchors on each site.
    """
    idx = {}
    for row in rows:
        river = (row.get("nrprimrv_s") or "").strip() or "Unknown"
        site = (row.get("site_name_s") or "").strip() or "(Unnamed site)"
        idx.setdefault(river, []).append((site, make_site_anchor(row)))

    for k in idx:
        idx[k].sort(key=lambda x: x[0].lower())
    keys = sorted(idx.keys(), key=lambda s: s.lower())

    parts = []
    parts.append('<div class="index-section">')
    parts.append('<h2 class="site-title">Index by Closest River</h2>')
    parts.append('<dl class="index-dl">')
    for river in keys:
        parts.append(f'<dt>{escape(river)}</dt>')
        links = [f'<a href="#{escape(anchor)}">{escape(site)}</a>' for site, anchor in idx[river]]
        parts.append(f'<dd>{" • ".join(links)}</dd>')
    parts.append('</dl>')
    parts.append('</div>')
    return "\n".join(parts)

def escape(s: str) -> str:
    return html.escape(s or "", quote=True)


def build_image_url(path: str) -> str:
    if not path:
        return ""
    return f"{URL_PREFIX}{path}"


def get_thumb_list(raw: str) -> List[str]:
    if not raw:
        return []
    images = sorted(raw.split("|"))
    hero = [p.strip() for p in images if p.strip() and 'hero' in p]
    rest = [p.strip() for p in images if p.strip() and not 'hero' in p]
    return hero + rest


def get_filename(path: str) -> str:
    if not path:
        return ""
    return path.replace("\\", "/").split("/")[-1]


def render_metadata_column(row: dict) -> str:
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
            map_raw = (row.get("Map_THUMBNAILS_ss") or "").strip()
            thumbs = get_thumb_list(map_raw)
            map_thumb = thumbs[0] if thumbs else ""
            map_url = build_image_url(map_thumb)
            map_title = get_filename(map_thumb)

            lat = (row.get("point_y_s") or "").strip()
            lon = (row.get("point_x_s") or "").strip()
            have_coords = bool(lat and lon)
            have_3rdcol = bool(map_thumb or have_coords)

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
            html_parts.append(
                "<td class='geo-meta-cell' colspan='2'>"
                "<table class='meta-table-inner'><tbody>"
                f"{meta_rows_str}"
                "</tbody></table>"
                "</td>"
            )

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


def render_images_column(row: dict) -> str:
    parts: List[str] = []
    for type_label, field_name in IMAGE_TYPES:
        raw = (row.get(field_name) or "").strip()
        thumbs = get_thumb_list(raw)
        if not thumbs:
            continue

        main = thumbs[0]
        extras = thumbs[1:4]
        main_url = build_image_url(main)
        main_title = get_filename(main)

        parts.append('<div class="img-type-block">')
        parts.append(f'<div class="img-type-heading">{escape(type_label)}</div>')
        parts.append(
            f'<img src="{escape(main_url)}" '
            f'title="{escape(main_title)}" '
            'class="img-main" />'
        )

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

        parts.append("</div>")
    return "\n".join(parts)


def render_site_div(row: dict) -> str:
    site_name = escape(row.get("site_name_s", ""))
    anchor = make_site_anchor(row)
    meta_html = render_metadata_column(row)
    img_html = render_images_column(row)
    return f'''
<div class="site-card" id="{anchor}">
  <h2 class="site-title">{site_name}</h2>
  <div class="row-flex">
    <div class="col-left">{meta_html}</div>
    <div class="col-right">{img_html}</div>
  </div>
</div>
'''.strip()


def main():

    if len(sys.argv) != 3:
        print("Usage: python make_report.py merged_sites.tsv <local|aws> > report.html", file = sys.stderr)
        sys.exit(1)

    global URL_PREFIX

    if 'local' in sys.argv[2].lower():
        URL_PREFIX = "http://localhost:3002/mmap-images/"  # for local infrared server
    elif 'aws' in sys.argv[2].lower():
        URL_PREFIX = "https://mmap-infrared.johnblowe.com/mmap-images/"  # for jbs aws instance
    else:
        print('second argument required: local or aws', file = sys.stderr)
        sys.exit(1)

    path = sys.argv[1]
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        rows = list(reader)

    print("<!DOCTYPE html><html><head><meta charset='utf-8'>")
    print("<title>Site Report</title>")
    print(r'''
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
    border: none;
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
    max-height: 500px;
    border: 1px solid #ccc;
    padding: 2px;
    border-radius: 2px;
    object-fit: contain;
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


/* ----- Page breaks + index ----- */
.page-break { height: 0; margin: 0; border: 0; }
.index-dl { columns: 3; column-gap: 24px; margin: 0; }
.index-dl dt { font-weight: 700; break-inside: avoid; page-break-inside: avoid; margin-top: 8px; }
.index-dl dd { margin: 0 0 8px 0; break-inside: avoid; page-break-inside: avoid; font-size: 0.95em; }

/* ----- Print / PDF optimization ----- */
@media print {
    /* Start each site on a new page */
    .site-card { break-before: page; page-break-before: always; }
    .site-card:first-child { break-before: auto; page-break-before: auto; }
    /* Explicit page-break markers for front/back matter */
    .page-break { break-after: page; page-break-after: always; }
    .index-section { break-before: page; page-break-before: always; }

    @page {
        size: letter;
        margin: 0.5in;
    }

    body {
        background: #ffffff;
        padding: 0;
        font-size: 11px;
    }

    .site-card {
        box-shadow: none;
        border: none;
        margin-bottom: 10px;
        page-break-inside: avoid;
    }

    .row-flex {
        flex-direction: row;
        gap: 6px;
    }

    .col-left,
    .col-right {
        width: 50%;
    }

    .site-title {
        font-size: 1.0rem;
        margin-bottom: 6px;
    }

    .sec-heading {
        font-size: 0.9rem;
        margin: 4px 0 2px 0;
        padding-bottom: 1px;
    }

    .meta-label,
    .meta-value {
        padding: 1px 2px;
        font-size: 0.85em;
    }

    .meta-table {
        margin-bottom: 3px;
    }

    .geo-map-thumb {
        max-width: 90px;
    }

    .geo-iframe {
        display: none !important;
    }

    .geo-link {
        display: block;
        font-size: 0.8rem;
        margin-top: 3px;
        text-decoration: underline;
    }

    .img-main {
        max-width: 100%;
        max-height: 5in;
        object-fit: contain;
    }

    .img-small-row {
        display: flex;
        gap: 3px;
    }

    .img-small {
        flex: 0 0 32%;
        max-width: 32%;
    }

    .img-type-block:nth-of-type(n+3) {
        display: none !important;
    }

    a {
        color: #000;
        text-decoration: underline;
    }
}
</style>
''')
    print("</head><body><div style='max-width:1200px; margin:0 auto;'>")
    # Front matter
    print(render_front_matter())
    for row in rows:
        print(render_site_div(row))
    # Back matter index
    print('<div class="page-break"></div>')
    print(render_index(rows))

    print("</div></body></html>")


if __name__ == "__main__":
    main()
