SELECT am.*,
  j26."SF Class",
  j26."Scond",
  j26."Color",
  j26."PigOnSide",
  j26."StonType",
  j26."FunctCl",
  j26."OrigShape",
  j26."ModEvidence",
  j26."ModEvidence1",
  j26."ModEvidence2",
  j26."ModEvidence3",
  j26."ModEvidence4"
FROM "tblArtifact_Master" am

JOIN "tblMiscStone" j26 ON j26."MMAP_Artifact_ID" = am."MMAP_Artifact_ID";
