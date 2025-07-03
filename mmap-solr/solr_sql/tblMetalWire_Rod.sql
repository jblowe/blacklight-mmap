SELECT am.*,
  j22."Type",
  j22."Corrosion",
  j22."InCatalog",
  j22."Sampled",
  j22."Elemental",
  j22."Hardness",
  j22."TotLen",
  j22."XDiam",
  j22."XType"
FROM "tblArtifact_Master" am

JOIN "tblMetalWire_Rod" j22 ON j22."MMAP_Artifact_ID" = am."MMAP_Artifact_ID";
