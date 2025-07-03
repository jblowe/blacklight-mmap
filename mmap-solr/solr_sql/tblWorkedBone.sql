SELECT am.*,
  j42."Max_Thick",
  j42."SubClass",
  j42."Scond",
  j42."WorkEvidence",
  j42."FunctMod",
  j42."Damage",
  j42."MaxDiam",
  j42."MaxLen",
  j42."PerfComm",
  j42."MeasComm"
FROM "tblArtifact_Master" am

JOIN "tblWorkedBone" j42 ON j42."MMAP_Artifact_ID" = am."MMAP_Artifact_ID";
