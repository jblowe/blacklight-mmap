SELECT am.*,
  j4."OutDiam",
  j4."OrigLen",
  j4."OrigWid",
  j4."OpenWid",
  j4."OpenDeg",
  j4."Ball",
  j4."Loop",
  j4."Sampled",
  j4."Hardness",
  j4."Elemental",
  j4."In_Catalog",
  j4."Corrosion"
FROM "tblArtifact_Master" am

JOIN "tblBells" j4 ON j4."MMAP_Artifact_ID" = am."MMAP_Artifact_ID";
