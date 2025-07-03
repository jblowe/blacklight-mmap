SELECT am.*,
  j25."SF Class",
  j25."SF Sub-class",
  j25."Scond"
FROM "tblArtifact_Master" am

JOIN "tblMiscClay" j25 ON j25."MMAP_Artifact_ID" = am."MMAP_Artifact_ID";
