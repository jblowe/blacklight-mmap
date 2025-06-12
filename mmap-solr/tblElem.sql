SELECT am.*,
  j9."AnalysType",
  j9."Corrosion",
  j9."TestYr",
  j9."Cu",
  j9."Sn",
  j9."As",
  j9."Pb",
  j9."Sb",
  j9."Fe",
  j9."Ag",
  j9."Ni",
  j9."S",
  j9."Cl",
  j9."Cl<2%",
  j9."EDAX Sn",
  j9."EDAX Pb",
  j9."EDAX Fe"
FROM "tblArtifact_Master" am

JOIN "tblElem" j9 ON j9."MMAP_Artifact_ID" = am."MMAP_Artifact_ID";
