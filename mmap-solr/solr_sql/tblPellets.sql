SELECT am.*,
  j28."SurfCond",
  j28."UseDamage",
  j28."txtDate_Last_Modified"
FROM "tblArtifact_Master" am

JOIN "tblPellets" j28 ON j28."MMAP_Artifact_ID" = am."MMAP_Artifact_ID";
