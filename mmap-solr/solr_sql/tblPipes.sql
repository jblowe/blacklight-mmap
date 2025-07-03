SELECT am.*,
  j30."Scond",
  j30."PipeParts",
  j30."Parts_uncertain",
  j30."Bowl_Present",
  j30."Neck_Present",
  j30."Stem_Present",
  j30."ProxEnd_Present",
  j30."Tail_Present",
  j30."PipeHgt",
  j30."PipeLen",
  j30."PipeExtDia",
  j30."PipeIntDia",
  j30."StemBoreDia",
  j30."Bowl_Shape",
  j30."PipeDesign"
FROM "tblArtifact_Master" am

JOIN "tblPipes" j30 ON j30."MMAP_Artifact_ID" = am."MMAP_Artifact_ID";
