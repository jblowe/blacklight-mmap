from typing import Dict, List, Tuple

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
    ("General view", "General_view_THUMBNAILS_ss"),
    ("Artifacts", "Artifacts_THUMBNAILS_ss"),
    ("Misc", "Misc_THUMBNAILS_ss"),
    ("People", "People_THUMBNAILS_ss"),
]
