SELECT am.*,
  j13."Artifact_class",
  j13."Alloy",
  j13."Oli_Alloy",
  j13."Where_cut",
  j13."How_mounted",
  j13."Compositional",
  j13."Structure",
  j13."Metallographic_description",
  j13."txtPM_Path1",
  j13."txtPM_Path2",
  j13."txtPM_Path3",
  j13."txtPM_Path4",
  j13."Site",
  j13."AnalysType",
  j13."Class",
  j13."Corrosion",
  j13."TestYr",
  j13."Cu",
  j13."Sn",
  j13."As",
  j13."Pb",
  j13."Sb",
  j13."Fe",
  j13."Ag",
  j13."Ni",
  j13."S",
  j13."Cl",
  j13."EDAX Sn",
  j13."EDAX Pb",
  j13."EDAX Fe",
  j13."ArtifactID",
  j13."Load_gm",
  j13."Area",
  j13."Hv_range",
  j13."SEALIP_Sample",
  j13."208Pb/206Pb",
  j13."207Pb/206Pb",
  j13."208Pb/204Pb",
  j13."207Pb/204Pb",
  j13."206Pb/204Pb",
  j13."Sample description",
  j13."Characterization"
FROM "tblArtifact_Master" am

JOIN "tblMetAnalysis_all" j13 ON j13."MMAP_Artifact_ID" = am."MMAP_Artifact_ID";
