SELECT am.*,
  j43."Artifact_class",
  j43."Alloy",
  j43."Where_cut",
  j43."How_mounted",
  j43."Compositional",
  j43."Structure",
  j43."Metallographic_description",
  j43."txtPM_Path1",
  j43."txtPM_Path2",
  j43."txtPM_Path3",
  j43."txtPM_Path4"
FROM "tblArtifact_Master" am

JOIN "tblmetallography" j43 ON j43."MMAP_Artifact_ID" = am."MMAP_Artifact_ID";
