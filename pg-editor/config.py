# config.py - user-editable configuration for the Flask Postgres Table Editor

# Branding
APP_LOGO = 'mmap-logo-pot-and-river.png'   # placed in static/img/
APP_TITLE = 'Middle Mekong Archaeology Project'
BANNER_BG = '#f9d88d'                # navbar background
BANNER_FG = '#002868'                # navbar text
BANNER_ACCENT = '#60a5fa'            # active link underline/accent

# Per-database crosswalk files (schema/table/columns) live here.
# On login the app looks for crosswalk-<dbname>.csv in this directory; if it is
# missing the app introspects the database and writes the file automatically.
CROSSWALK_DIR = 'instance/crosswalks'

# Runtime
SECRET_KEY = 'change-me'             # required; used for session signing
DEFAULT_SCHEMA = 'public'            # schema to query (normally 'public')

# Session persistence
# If the user checks "Remember my login", the app sets session.permanent=True.
# The browser will then keep the session cookie for this many days.
SESSION_LIFETIME_DAYS = 30

# Storage for per-table "Configure" preferences (View/Edit column visibility)
TABLE_CONFIG_FILE = 'instance/table_config.json'

# Pagination
PAGE_SIZE = 25

# Database connection defaults for the login form (optional)
DB_DEFAULTS = dict(
    host='localhost',
    port=5432,
    dbname='postgres',
    user='postgres',
)

# Safety: allow DELETE operations?
ALLOW_DELETES = True
