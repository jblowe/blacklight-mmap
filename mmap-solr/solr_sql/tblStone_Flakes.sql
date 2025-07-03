SELECT am.*,
  j41."Color",
  j41."Texture",
  j41."Rock_Stone_Type",
  j41."Length_Percussion",
  j41."Width",
  j41."Dorsal_Cortex",
  j41."Platform",
  j41."Over_Remove",
  j41."Termination",
  j41."Thickness",
  j41."Plat_Width",
  j41."Plat_Thick",
  j41."Plat_Angle",
  j41."Perc_Plat_Cort",
  j41."Perc_Dors_Cort",
  j41."Min_Scars_Dors",
  j41."Min_Step_Term",
  j41."Min_Rotation",
  j41."Comment",
  j41."Last_Modified"
FROM "tblArtifact_Master" am

JOIN "tblStone_Flakes" j41 ON j41."MMAP_Artifact_ID" = am."MMAP_Artifact_ID";
