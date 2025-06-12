SELECT am.*,
  j17."Corrosion",
  j17."Sampled",
  j17."InCatalog",
  j17."Elemental",
  j17."Hardness",
  j17."Type",
  j17."Subtype",
  j17."OrigLen",
  j17."EdgeRad",
  j17."EdgeLen",
  j17."ChordLen",
  j17."ChordHt",
  j17."WaistWid",
  j17."AvgBlWid",
  j17."BlThick",
  j17."AdzeFace",
  j17."ODSocket",
  j17."IDSocket",
  j17."OrigScktHt"
FROM "tblArtifact_Master" am

JOIN "tblMetalAdze" j17 ON j17."MMAP_Artifact_ID" = am."MMAP_Artifact_ID";
