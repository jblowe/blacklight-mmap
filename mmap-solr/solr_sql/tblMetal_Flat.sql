SELECT am.*,
  j23."InCatalog",
  j23."Elemental",
  j23."Thickness",
  j23."Hardness",
  j23."Shape",
  j23."Corr",
  j23."Sampled"
FROM "tblArtifact_Master" am

JOIN "tblMetal_Flat" j23 ON j23."MMAP_Artifact_ID" = am."MMAP_Artifact_ID";
