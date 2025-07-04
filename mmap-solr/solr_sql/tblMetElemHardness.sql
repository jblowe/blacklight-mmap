SELECT am.*,
  j15."Artifact_class",
  j15."Alloy",
  j15."Where_cut",
  j15."How_mounted",
  j15."Compositional",
  j15."Structure",
  j15."Metallographic_description",
  j15."txtPM_Path1",
  j15."txtPM_Path2",
  j15."txtPM_Path3",
  j15."txtPM_Path4",
  j15."tblelemental-Cu_MMAP_Artifact_ID",
  j15."Site",
  j15."AnalysType",
  j15."Class",
  j15."Corrosion",
  j15."TestYr",
  j15."Cu",
  j15."Sn",
  j15."As",
  j15."Pb",
  j15."Sb",
  j15."Fe",
  j15."Ag",
  j15."Ni",
  j15."S",
  j15."Cl",
  j15."EDAX Sn",
  j15."EDAX Pb",
  j15."EDAX Fe",
  j15."ArtifactID",
  j15."Load_gm",
  j15."Area",
  j15."Hv_range"
FROM "tblArtifact_Master" am

JOIN "tblMetElemHardness" j15 ON j15."MMAP_Artifact_ID" = am."MMAP_Artifact_ID";
