SELECT am.*,
  j16."Site",
  j16."Class",
  j16."Load_gm",
  j16."Area",
  j16."Hv_range"
FROM "tblArtifact_Master" am

JOIN "tblMetHardness" j16 ON j16."MMAP_Artifact_ID" = am."MMAP_Artifact_ID";
