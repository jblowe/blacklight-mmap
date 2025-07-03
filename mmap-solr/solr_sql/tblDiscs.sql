SELECT am.*,
  j8."Scond",
  j8."Diam",
  j8."Thick",
  j8."PerfDia",
  j8."SurfTrtmt"
FROM "tblArtifact_Master" am

JOIN "tblDiscs" j8 ON j8."MMAP_Artifact_ID" = am."MMAP_Artifact_ID";
