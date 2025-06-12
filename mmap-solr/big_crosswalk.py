import psycopg2

# === Configure your DB connection here ===
conn = psycopg2.connect(
    dbname="your_db_name",
    user="your_username",
    password="your_password",
    host="your_host",
    port="your_port"
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

select_columns = [f'{main_alias}."{shared_key}"']
join_clauses = []

for idx, table in enumerate(joined_tables, start=1):
    alias = f"j{idx}"
    join_clause = f'LEFT JOIN "{table}" {alias} ON {alias}."{shared_key}" = {main_alias}."{shared_key}"'
    join_clauses.append(join_clause)

    cur.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = %s
          AND column_name != %s
        ORDER BY ordinal_position;
    """, (table, shared_key))

    for row in cur.fetchall():
        col = row[0]
        select_columns.append(f'{alias}."{col}" AS "{alias}__{col}"')

# Build the final SQL
sql = "CREATE TABLE full_artifact_join AS\nSELECT\n  " + ",\n  ".join(select_columns)
sql += f"\nFROM \"{main_table}\" {main_alias}\n" + "\n".join(join_clauses) + ";"

# Output the SQL query
print(sql)

cur.close()
conn.close()
