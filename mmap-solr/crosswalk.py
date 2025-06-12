import psycopg2

# === Configure your DB connection here ===
conn = psycopg2.connect(
    dbname="mmap",
    user="xxxx",
    password="xxxx",
    host="<get from mmap staff>",
    port="<get from mmap staff",
    sslmode='require'
)

cur = conn.cursor()

main_table = "tblArtifact_Master"
main_alias = "am"
shared_key = "MMAP_Artifact_ID"
joined_tables = ['BC Artifact Inventory', 'tblAllBangles', 'tblBeads', 'tblBells', 'tblBuddhas',
    'tblCrucibles', 'tblCylinders', 'tblDiscs', 'tblElem', 'tblFigurines',
    'tblGlassAnalyses', 'tblIronArt', 'tblMetAnalysis_all', 'tblMetElem',
    'tblMetElemHardness', 'tblMetHardness', 'tblMetalAdze', 'tblMetalAmorph',
    'tblMetalBlades', 'tblMetalMisc', 'tblMetalPoints', 'tblMetalWire_Rod',
    'tblMetal_Flat', 'tblMiscArt', 'tblMiscClay', 'tblMiscStone', 'tblPMs',
    'tblPellets', 'tblPestles', 'tblPipes', 'tblPotLocationsSmall', 'tblPotsNew',
    'tblPrehistoric_Metal', 'tblPrills', 'tblSherds', 'tblSlagPrehist',
    'tblSpindleWhorls', 'tblSpoons', 'tblStoneAdzesNew', 'tblStone_Cores',
    'tblStone_Flakes', 'tblWorkedBone', 'tblmetallography']

cur.execute("""
    SELECT column_name
    FROM information_schema.columns
    WHERE table_schema = 'public'
      AND table_name = 'tblArtifact_Master'
    ORDER BY ordinal_position;
""")
columns = [c[0] for c in cur.fetchall()]

for idx, table in enumerate(joined_tables, start=1):
    sql = f'SELECT {main_alias}.*,\n  '
    alias = f"j{idx}"
    join_clause = f'JOIN "{table}" {alias} ON {alias}."{shared_key}" = {main_alias}."{shared_key}"'


    cur.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = %s
          AND column_name != %s
        ORDER BY ordinal_position;
    """, (table, shared_key))

    select_columns = []
    for row in cur.fetchall():
        col = row[0]
        if col not in columns:
            select_columns.append(f'{alias}."{col}"')
        else:
            print(f'duplicate column {col} in {table}')
    sql = sql + ",\n  ".join(select_columns)
    sql += f"\nFROM \"{main_table}\" {main_alias}\n" + "\n" + join_clause + ";"
    with open(f'{table}.sql','w') as table_sql:
        print(sql, file=table_sql)
        table_sql.close()

cur.close()
conn.close()
