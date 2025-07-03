SELECT am.*,
  j21."Record_ID",
  j21."Corrosion",
  j21."Type",
  j21."Subtype",
  j21."InCatalog",
  j21."Elemental",
  j21."Sampled",
  j21."Hardness",
  j21."HardTest",
  j21."OrigLen",
  j21."OrigLenBlade",
  j21."OrigMaxWid",
  j21."MaxBladeWidth",
  j21."BladeThickness",
  j21."Rib",
  j21."BladeShape",
  j21."OuterDiamSocket",
  j21."InnerDiamSocket",
  j21."Tang"
FROM "tblArtifact_Master" am

JOIN "tblMetalPoints" j21 ON j21."MMAP_Artifact_ID" = am."MMAP_Artifact_ID";
