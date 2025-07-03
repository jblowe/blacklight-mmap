SELECT am.*,
  j18."Class",
  j18."Corr",
  j18."Sampled",
  j18."InCat",
  j18."cat",
  j18."Elem?",
  j18."Hardness",
  j18."Shape"
FROM "tblArtifact_Master" am

JOIN "tblMetalAmorph" j18 ON j18."MMAP_Artifact_ID" = am."MMAP_Artifact_ID";
