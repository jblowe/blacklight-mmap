SELECT am.*,
  j20."Subclass",
  j20."Corr",
  j20."Sampled",
  j20."InCatalog",
  j20."Elemental",
  j20."Hardness",
  j20."OrigLen",
  j20."OrigWid",
  j20."IDSocket",
  j20."MaxShaft",
  j20."OpenWid",
  j20."OpenDeg",
  j20."MaxThick"
FROM "tblArtifact_Master" am

JOIN "tblMetalMisc" j20 ON j20."MMAP_Artifact_ID" = am."MMAP_Artifact_ID";
