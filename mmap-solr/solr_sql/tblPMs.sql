SELECT am.*,
  j27."ArtifactClass",
  j27."Date_Taken",
  j27."Etchant",
  j27."Magnification",
  j27."Neg No"
FROM "tblArtifact_Master" am

JOIN "tblPMs" j27 ON j27."MMAP_Artifact_ID" = am."MMAP_Artifact_ID";
