SELECT am.*,
  
FROM "tblArtifact_Master" am

JOIN "BC Artifact Inventory" j1 ON j1."MMAP_Artifact_ID" = am."MMAP_Artifact_ID";
