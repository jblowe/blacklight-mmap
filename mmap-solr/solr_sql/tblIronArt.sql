SELECT am.*,
  j12."Genre",
  j12."Haft",
  j12."Max_Thick",
  j12."Description"
FROM "tblArtifact_Master" am

JOIN "tblIronArt" j12 ON j12."MMAP_Artifact_ID" = am."MMAP_Artifact_ID";
