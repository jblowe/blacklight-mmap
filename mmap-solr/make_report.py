#!/usr/bin/env python3
# make_report.py — generates standalone HTML report for merged_sites.tsv

import csv
import sys
import html
import json
import base64
from datetime import datetime
from pathlib import Path
import re
from typing import Dict, List, Tuple


URL_PREFIX = "https://mmap.org"   # set this as needed for your thumbnails


# --- Front/back matter --------------------------------------------------------

def read_snippet(path: str) -> str:
    """
    Read an HTML snippet from disk.
    If it contains <body>...</body>, extract body contents.
    """
    txt = Path(path).read_text(encoding="utf-8")
    m = re.search(r"<body[^>]*>(.*)</body>", txt, flags=re.IGNORECASE | re.DOTALL)
    if m:
        txt = m.group(1)
    return txt.strip()


def make_site_anchor(row: dict) -> str:
    raw = (row.get("siteid_s") or row.get("site_name_s") or "site").strip().lower()
    raw = re.sub(r"\s+", "-", raw)
    raw = re.sub(r"[^a-z0-9_-]+", "", raw)
    return "site-" + (raw or "site")


def render_front_matter() -> str:
    # title page, then intro, each separated by an explicit page break
    title_html = read_snippet("title_page.html")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    title_html = title_html.replace("{DATE}", timestamp)
    intro_html = read_snippet("introduction.html")
    return "\n".join([
        '<div class="front-matter">', title_html, '</div>',
        '<div class="page-break"></div>',
        '<div class="front-matter">', intro_html, '</div>',
        '<div class="page-break"></div>',
    ])


def render_index(rows: List[dict]) -> str:
    """
    Index keyed by Closest River (nrprimrv_s), placed after the introduction.
    """
    idx = {}
    for row in rows:
        key = (row.get("nrprimrv_s") or "").strip() or "Unknown"
        site = (row.get("site_name_s") or "").strip() or "(Unnamed site)"
        anchor = make_site_anchor(row)
        idx.setdefault(key, []).append((site, anchor))

    for k in idx:
        idx[k].sort(key=lambda x: x[0].lower())
    keys = sorted(idx.keys(), key=lambda s: s.lower())

    parts = []
    parts.append('<div class="index-section">')
    parts.append('<h1 class="sec-heading">Sites by Closest River, in alphabetical order</h1>')
    parts.append('<dl class="index-dl">')
    for k in keys:
        parts.append(f'<dt>{escape(k)}</dt>')
        links = [f'<a href="#{escape(a)}">{escape(s)}</a>' for (s, a) in idx[k]]
        parts.append(f'<dd>{" • ".join(links)}</dd>')
    parts.append('</dl>')
    parts.append('</div>')
    return "\n".join(parts)


# --- Image popout overlay -----------------------------------------------------

IMG_POPUP_OVERLAY = """
<div id="imgPopup" class="img-popup-overlay" aria-hidden="true">
  <div class="img-popup-panel">
    <div class="img-popup-topbar">
      <div id="imgPopupTitle" style="font-weight:700;"></div>
      <div class="img-popup-close" onclick="hideImgPopup()">Close</div>
    </div>
    <div id="imgPopupGrid" class="img-popup-grid"></div>
  </div>
</div>
<script>
function hideImgPopup(){
  const o=document.getElementById("imgPopup");
  o.classList.remove("open");
  o.style.display="none";
  o.setAttribute("aria-hidden","true");
  document.getElementById("imgPopupGrid").innerHTML="";
}
function showImgPopupB64(title, itemsB64){
  const itemsJson = atob(itemsB64);
  const items = JSON.parse(itemsJson);

  const w = window.open("about:blank", "_blank");
  try { if(w) { w.opener = null; } } catch(e) {}
  if(!w){ return true; }

  const esc = (s)=>String(s||"").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");

  let h = "";
  h += "<!DOCTYPE html><html><head><meta charset='utf-8'><title>"+esc(title)+"</title>";
  h += "<style>";
  h += "body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif;margin:16px;}";
  h += "h1{font-size:18px;margin:0 0 12px 0;}";
  h += ".grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;}";
  h += "a{display:block;text-decoration:none;color:inherit;}";
  h += "img{width:100%;height:auto;border:1px solid #ccc;border-radius:2px;padding:2px;}";
    h += "</style></head><body>";
  h += "<h1>"+esc(title)+"</h1>";
  h += "<div class='grid'>";
  for(const it of items){
    const full = esc(it.full);
    const thumb = esc(it.thumb);
    const t = esc(it.title||"");
    h += "<a href='"+full+"' target='_blank'><img src='"+thumb+"' title='"+t+"'></a>";
  }
  h += "</div></body></html>";

  w.document.open();
  w.document.write(h);
  w.document.close();
  return false;
}
document.addEventListener("keydown", function(e){ if(e.key==="Escape") hideImgPopup(); });
/* Ensure overlay is attached directly to <body> so it truly overlays */
document.addEventListener("DOMContentLoaded", function(){
  const o = document.getElementById("imgPopup");
  if(o && o.parentElement && o.parentElement !== document.body){
    document.body.appendChild(o);
  }
});
document.getElementById("imgPopup").addEventListener("click", function(e){
  if(e.target && e.target.id==="imgPopup"){ hideImgPopup(); }
});
</script>
"""


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

# Image types (Map handled separately)
IMAGE_TYPES: List[Tuple[str, str]] = [
    ("General View", "General view_THUMBNAILS_ss"),
    ("Environment", "Environment_THUMBNAILS_ss"),
    ("Feature", "Feature_THUMBNAILS_ss"),
    ("Artifacts on site", "Artifacts_on_site_THUMBNAILS_ss"),
    ("Action-process", "Action_process_THUMBNAILS_ss"),
    ("Studio bag shot", "Studio_bag_shot_THUMBNAILS_ss"),
    ("Studio artifact shot", "Studio_artifact_shot_THUMBNAILS_ss"),
    ("Miscellaneous", "Miscellaneous_THUMBNAILS_ss"),
    ("Speleothem", "Speleothem_THUMBNAILS_ss"),
    ("Documents", "Documents_THUMBNAILS_ss"),
    ("Misc", "Misc_THUMBNAILS_ss"),
    ("Artifacts", "Artifacts_THUMBNAILS_ss"),
    ("People", "People_THUMBNAILS_ss"),
]


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

        # Build per-image thumb/full pairs for popup and linking
        filename_field = f"{type_label}_FILENAME_ss"
        files = get_thumb_list((row.get(filename_field) or "").strip())
        items = []
        for i, t in enumerate(thumbs):
            full_path = files[i] if i < len(files) and files[i] else t
            items.append({
                "thumb": build_image_url(t),
                "full": build_image_url(t),
                "title": get_filename(t)
            })
        items_b64 = base64.b64encode(json.dumps(items).encode("utf-8")).decode("ascii")
        n_images = len(items)

        main = thumbs[0]
        extras = thumbs[1:4]  # up to 3 more
        main_url = build_image_url(main)
        main_title = get_filename(main)
        main_full = main_url

        parts.append('<div class="img-type-block">')
        site_name = (row.get("site_name_s") or "").strip()
        popup_title = f"{site_name}, {n_images} {type_label} images"

        parts.append(
            f'<div class="img-type-heading">{escape(type_label)}</div>'
            f'<div class="img-all-wrap">'
            f'<a href="#" class="img-all-link" '
            f'onclick="showImgPopupB64(\'{escape(popup_title)}\', \'{escape(items_b64)}\'); return false;">'
            f'all {n_images} images</a>'
        )

        # Main image (wrapped in a link to the full image)
        parts.append(
            f'<a href="{escape(main_full)}" target="_blank">'
            f'<img src="{escape(main_url)}" title="{escape(main_title)}" class="img-main" />'
            f'</a></div>'
        )

        # Extra thumbnails (also wrapped links)
        if extras:
            parts.append('<div class="img-small-row">')
            for i, t in enumerate(extras, start=1):
                url = build_image_url(t)
                title = get_filename(t)
                full_u = url
                parts.append(
                    f'<a href="{escape(full_u)}" target="_blank">'
                    f'<img src="{escape(url)}" title="{escape(title)}" class="img-small" />'
                    f'</a>'
                )
            parts.append("</div>")

        parts.append("</div>")  # end type block

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



def render_index_alpha(rows: List[dict]) -> str:
    """
    Index of sites in alphabetical order, rendered in as many columns as needed,
    with a maximum of 60 rows per column.
    Each entry: Site Name (link to article) + coordinates (if any, link to Google Maps).
    """
    items = []
    for row in rows:
        site = (row.get("site_name_s") or "").strip() or "(Unnamed site)"
        anchor = make_site_anchor(row)

        lat_raw = (row.get("point_y_s") or "").strip()
        lon_raw = (row.get("point_x_s") or "").strip()
        lat = lon = None
        try:
            if lat_raw and lon_raw:
                lat = float(lat_raw)
                lon = float(lon_raw)
        except ValueError:
            lat = lon = None

        items.append((site, anchor, lat, lon))

    items.sort(key=lambda x: x[0].lower())

    max_rows = 60
    ncols = max(1, (len(items) + max_rows - 1) // max_rows)

    cols = []
    for c in range(ncols):
        cols.append(items[c*max_rows:(c+1)*max_rows])

    parts = []
    parts.append('<div class="index-section">')
    parts.append('<h1 class="sec-heading">Sites in alphabetical order</h1>')
    parts.append('<table class="alpha-index-table"><tr>')

    for col in cols:
        parts.append('<td class="alpha-index-col"><ul class="alpha-index-ul">')
        for site, anchor, lat, lon in col:
            site_link = f'<a href="#{escape(anchor)}">{escape(site)}</a>'
            if lat is not None and lon is not None:
                g = f'https://www.google.com/maps?q={lat:.6f},{lon:.6f}&z=14'
                coord_link = f' <span class="alpha-coords">(<a href="{escape(g)}" target="_blank">{lat:.6f}, {lon:.6f}</a>)</span>'
            else:
                coord_link = ''
            parts.append(f'<li>{site_link}{coord_link}</li>')
        parts.append('</ul></td>')
    parts.append('</tr></table>')
    parts.append('</div>')
    return "\n".join(parts)


def render_all_sites_map(rows: List[dict]) -> str:
    """
    Full-page interactive map of ALL sites with coordinates (Leaflet + OSM tiles).
    Uses a <script type="application/json"> block to safely embed data (no quoting issues).
    """
    pts = []
    for row in rows:
        lat_raw = (row.get("point_y_s") or "").strip()
        lon_raw = (row.get("point_x_s") or "").strip()
        if not lat_raw or not lon_raw:
            continue
        try:
            lat = float(lat_raw)
            lon = float(lon_raw)
        except ValueError:
            continue

        site = (row.get("site_name_s") or "").strip() or "(Unnamed site)"
        anchor = make_site_anchor(row)
        pts.append({"site": site, "anchor": anchor, "lat": lat, "lon": lon})

    if not pts:
        return '<div class="index-section"><h1 class="sec-heading">All Sites Map</h1><p>No coordinates found.</p></div>'

    pts_json = json.dumps(pts)

    parts = []
    parts.append('<div class="index-section">')
    parts.append('<h1 class="sec-heading">All Sites Map</h1>')
    parts.append('<div class="map-note">Interactive map (pan/zoom). Markers link to the site entry and to Google Maps.</div>')
    parts.append('<div id="allSitesMap" class="all-sites-map"></div>')
    parts.append('<script id="all-sites-data" type="application/json">')
    parts.append(pts_json)
    parts.append('</script>')
    parts.append('<script>')
    parts.append("""
(function(){
  function init(){
    if(typeof L === "undefined"){ return; }
    var dataEl = document.getElementById("all-sites-data");
    if(!dataEl){ return; }
    var ALL_SITES = JSON.parse(dataEl.textContent);

    var map = L.map("allSitesMap", { zoomControl: true });
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 18,
      attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    var bounds = [];
    for(var i=0;i<ALL_SITES.length;i++){
      var p = ALL_SITES[i];
      var ll = [p.lat, p.lon];
      bounds.push(ll);

      var g = "https://www.google.com/maps?q=" + p.lat + "," + p.lon + "&z=14";
      var html = ''
        + '<div style="font-weight:700; margin-bottom:4px;">' + p.site + '</div>'
        + '<div><a href="#' + p.anchor + '">Open in report</a></div>'
        + '<div><a href="' + g + '" target="_blank">Open in Google Maps</a></div>';

      L.marker(ll).addTo(map).bindPopup(html);
    }
    if(bounds.length){
      map.fitBounds(bounds, { padding: [20,20] });
    } else {
      map.setView([0,0], 2);
    }
  }
  if(document.readyState === "loading"){
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
""")
    parts.append('</script>')
    parts.append('</div>')
    return "\n".join(parts)

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
    float: left;
}

.img-main {
    width: 100%;
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
    gap: 6px;
}

.img-small-row a {
    flex: 0 0 calc((100% - 12px)/3);
    max-width: calc((100% - 12px)/3);
    display: block;
}

.img-small {
    width: 100%;
    max-width: 100%;
    border: 1px solid #ccc;
    border-radius: 2px;
    height: auto;
    padding: 2px;
}

.img-all-wrap {
  text-align: right;
  margin-bottom: 4px;
}

/* ----- Print / PDF optimization ----- */
@media print {
    /* Explicit page breaks + per-site pages */
    .page-break { break-after: page; page-break-after: always; }
    .site-card { break-before: page; page-break-before: always; }
    .site-card:first-of-type { break-before: auto; page-break-before: auto; }
    .img-popup-overlay { display: none; position: fixed !important; top: 0; left: 0; right: 0; bottom: 0; width: 100vw; height: 100vh; background: rgba(0,0,0,0.7); z-index: 2147483647; }

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
    .all-sites-iframe { width: 1000px; max-width: 100%; height: 75vh; border: 0; display: block; margin: 0 auto; }
    .all-sites-map { width: 1000px; max-width: 100%; height: calc(100vh - 180px); min-height: 700px; border: 1px solid #ccc; margin: 0 auto; }
    .map-note { font-size: 0.95em; margin: 8px 0 10px 0; }

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
    margin-top: 6px;
    display: flex;
    gap: 6px;
}

.img-small-row a {
    flex: 0 0 calc((100% - 12px)/3);
    max-width: calc((100% - 12px)/3);
    display: block;
}

.img-small {
    width: 100%;
    max-width: 100%;
    border: 1px solid #ccc;
    border-radius: 2px;
    height: auto;
    padding: 2px;
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
    print("</head><body>")
    print("<div style='max-width:1200px; margin:0 auto;'>")
    print(render_front_matter())
    print(render_index(rows))
    print('<div class="page-break"></div>')
    print(render_all_sites_map(rows))
    print('<div class="page-break"></div>')
    print(render_index_alpha(rows))
    print('<div class="page-break"></div>')
    for row in rows:
        print(render_site_div(row))
    print(IMG_POPUP_OVERLAY)
    print("</div></body></html>")


if __name__ == "__main__":
    main()
