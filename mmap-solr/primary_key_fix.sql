-- 1. Dropping the original primary key
ALTER TABLE "tblArtifact_Master" DROP CONSTRAINT "tblArtifact_Master_pkey";

-- 2. Create index on Record_No
ALTER TABLE "tblArtifact_Master" ALTER COLUMN "Record_No" SET NOT NULL;
CREATE UNIQUE INDEX "tblArtifact_Master_Record_No"  ON "tblArtifact_Master"  ("Record_No");
ALTER TABLE "tblArtifact_Master" ALTER COLUMN "Record_No" SET NOT NULL; 
CREATE UNIQUE INDEX "tblArtifact_Master_pkey"  ON "tblArtifact_Master"  ("Record_No");

-- 3. Creating new primary key using existing index for Record_No
ALTER TABLE "tblArtifact_Master" ADD PRIMARY KEY USING INDEX "tblArtifact_Master_pkey";

-- 4. Set up autoincrement and set the start value based on the highest value
ALTER TABLE "tblArtifact_Master" ALTER "Record_No" ADD GENERATED ALWAYS AS IDENTITY;
SELECT SETVAL('"tblArtifact_Master_Record_No_seq"', (SELECT MAX("Record_No") FROM "tblArtifact_Master"));

-- 5. You can drop the original sequence generator if you won't need it 
DROP SEQUENCE "tblArtifact_Master_MMAP_Artifact_ID_seq";

