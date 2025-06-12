SELECT am.*,
  j40."Site",
  j40."Color",
  j40."Texture",
  j40."Rock_Stone_Type",
  j40."Last_Modified",
  j40."River Cobble",
  j40."Platform",
  j40."Flake_Circum",
  j40."Length",
  j40."Width",
  j40."Thickness",
  j40."Plat_Perim_Flake",
  j40."Min_Num_Flake_Scars",
  j40."Description",
  j40."Hammerstone",
  j40."Percussion"
FROM "tblArtifact_Master" am

JOIN "tblStone_Cores" j40 ON j40."MMAP_Artifact_ID" = am."MMAP_Artifact_ID";
