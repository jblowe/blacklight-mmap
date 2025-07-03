SELECT am.*,
  j38."HandleCompleteness",
  j38."BowlCompleteness",
  j38."HandleLength",
  j38."HandlDiameter",
  j38."BowlDepth",
  j38."BowlThickness",
  j38."BowlInsideDiameter",
  j38."HandleShape",
  j38."BowlShape"
FROM "tblArtifact_Master" am

JOIN "tblSpoons" j38 ON j38."MMAP_Artifact_ID" = am."MMAP_Artifact_ID";
