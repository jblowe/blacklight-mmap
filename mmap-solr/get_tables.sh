#!/bin/bash -x
source export_tables.sh

# run the sql extract for each of the subtables.
# (sql created by crosswalk.py)
for i in "${tables[@]}"
do

  echo $i
  psql -F $'\t' -R"@@" 'postgresql:<get the correct string from mmap staff>' -A -f $i.sql > $i.csv
  perl -i -pe 's/[\r\n]/ /g;s/\@\@/\n/g' $i.csv

done

