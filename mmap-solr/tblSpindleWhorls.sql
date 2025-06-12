SELECT am.*,
  j37."SurfCond",
  j37."TotalHt",
  j37."SegmentAHt",
  j37."SegmentBHt",
  j37."MaxDiam",
  j37."HoleDiam",
  j37."PerfType",
  j37."PerfSymmetry",
  j37."ConfigSegA",
  j37."ConfigSegB",
  j37."DamageComments"
FROM "tblArtifact_Master" am

JOIN "tblSpindleWhorls" j37 ON j37."MMAP_Artifact_ID" = am."MMAP_Artifact_ID";
