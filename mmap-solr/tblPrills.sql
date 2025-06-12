SELECT am.*,
  
FROM "tblArtifact_Master" am

JOIN "tblPrills" j34 ON j34."MMAP_Artifact_ID" = am."MMAP_Artifact_ID";
