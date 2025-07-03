SELECT am.*,
  j36."COMMENTS"
FROM "tblArtifact_Master" am

JOIN "tblSlagPrehist" j36 ON j36."MMAP_Artifact_ID" = am."MMAP_Artifact_ID";
