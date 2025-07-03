SELECT am.*,
  j24."Genre",
  j24."Thickness",
  j24."Comment"
FROM "tblArtifact_Master" am

JOIN "tblMiscArt" j24 ON j24."MMAP_Artifact_ID" = am."MMAP_Artifact_ID";
