SELECT am.*,
  j3."Anlyst",
  j3."Scond",
  j3."Length",
  j3."MaxDiam",
  j3."MinDiam",
  j3."PerfDiam",
  j3."Color",
  j3."PerfType",
  j3."Mfg",
  j3."Decor",
  j3."Shape",
  j3."Comp_Type",
  j3."Lankton_Color",
  j3."Comment"
FROM "tblArtifact_Master" am

JOIN "tblBeads" j3 ON j3."MMAP_Artifact_ID" = am."MMAP_Artifact_ID";
