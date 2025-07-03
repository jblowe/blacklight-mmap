SELECT am.*,
  
FROM "tblArtifact_Master" am

JOIN "tblPrehistoric_Metal" j33 ON j33."MMAP_Artifact_ID" = am."MMAP_Artifact_ID";
