SELECT am.*,
  j2."InCatalog",
  j2."Sampled",
  j2."Elemental",
  j2."Hardness",
  j2."Corrosion",
  j2."Type",
  j2."SubType",
  j2."ChordLen",
  j2."InDiam",
  j2."ShaftHt",
  j2."ShaftWth",
  j2."SurfTreat",
  j2."Wear",
  j2."Xshape",
  j2."FormEvid",
  j2."SCond"
FROM "tblArtifact_Master" am

JOIN "tblAllBangles" j2 ON j2."MMAP_Artifact_ID" = am."MMAP_Artifact_ID";
