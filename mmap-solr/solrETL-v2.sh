#!/bin/bash -x
date
##############################################################################
# move the current set of extracts to temp (thereby saving the previous run, just in case)
##############################################################################
# mv 4solr.*.csv.gz /tmp
TENANT=$1
CORE="public"
CONNECT_STRING="postgresql:<get the correct string from mmap staff>"

##############################################################################
# clear out the existing data
##############################################################################
curl -S -s "http://localhost:8983/solr/${TENANT}-${CORE}/update" --data '<delete><query>*:*</query></delete>' -H 'Content-type:text/xml; charset=utf-8'
curl -S -s "http://localhost:8983/solr/${TENANT}-${CORE}/update" --data '<commit/>' -H 'Content-type:text/xml; charset=utf-8'

##############################################################################
# extract metadata
##############################################################################
source export_tables.sh
for table in "${tables[@]}"
do

  echo "table: ${table}"
  time psql -R"@@" -A -U $USERNAME -d "$CONNECT_STRING" -f ${table}.sql | \
    perl -pe 's/[\r\n\t]/ /g;s/\|/\t/g;s/\@\@/\n/g' > ${table}.csv
  perl -i -pe 's/ 00:00:00//g' ${table}.csv
  ##############################################################################
  #  compute a boolean: hascoords = yes/no
  ##############################################################################
  # check that all rows have the same number of fields as the header
  ##############################################################################
  # export NUMCOLS=`grep Record_No ${CORE}.csv | awk '{ FS = "\t" ; print NF}'`
  export NUMCOLS=$(grep Record_No ${table}.csv | perl -pe 's/\t/\n/g' | wc -l)
  export NUMCOLS=$(bc -e "$NUMCOLS")
  echo "numcols $NUMCOLS"
  awk -F'\t' -v NUMCOLS=$NUMCOLS 'NF == NUMCOLS' ${table}.csv | \
    perl -pe 's/\\/\//g;s/\t"/\t/g;s/"\t/\t/g;' > 4solr.${table}.csv &
  awk -F'\t' -v NUMCOLS=$NUMCOLS 'NF != NUMCOLS' ${table}.csv | \
    perl -pe 's/\\/\//g' > errors.${table}.csv &
  wait
  # recover the solr header and put it back at the top of the file
  grep Record_No 4solr.${table}.csv > ${table}.header4Solr.csv
  perl -i -pe 's/\t/_s\t/g;s/$/_s/;s/Record_No_s/id/;tr/A-Z/a-z/;s/ /_/g;s/\?//g;' ${table}.header4Solr.csv
  ##############################################################################
  # generate solr schema <copyField> elements, just in case.
  # also generate parameters for POST to solr (to split _ss fields properly)
  ##############################################################################
  ./genschema.sh ${table}
  grep -v "Record_No" 4solr.${table}.csv > d8.csv
  cat ${table}.header4Solr.csv d8.csv | perl -pe 's/␥/|/g' > d9.csv
  ##############################################################################
  # compute _i values for _dt values (to support BL date range searching)
  ##############################################################################
  #time python3 computeTimeIntegers.py d9.csv 4solr.${TENANT}.${CORE}.csv
  # clean up some outstanding sins perpetuated by earlier scripts
  #perl -i -pe 's/\r//g;s/\\/\//g;s/\t"/\t/g;s/"\t/\t/g;s/\"\"/"/g' 4solr.${TENANT}.${CORE}.csv
  ##############################################################################
  # ok, now let's load this into solr...
  # clear out the existing data
  ##############################################################################
  mv d9.csv 4solr.${table}.csv
  ##############################################################################
  # this POSTs the csv to the Solr / update endpoint
  # note, among other things, the overriding of the encapsulator with \
  ##############################################################################
  ss_string=`cat uploadparms.${table}.txt`
  time curl -X POST -S -s "http://localhost:8983/solr/${TENANT}-${CORE}/update/csv?commit=true&header=true&separator=%09&${ss_string}f.blob_ss.split=true&f.blob_ss.separator=,&encapsulator=\\" -T 4solr.${table}.csv -H 'Content-type:text/plain; charset=utf-8' &
  time python3 evaluate.py 4solr.${table}.csv temp.${table}.csv > 4solr.fields.${table}.counts.csv &
  # wait for POSTs to Solr to finish
  wait
done
##############################################################################
# wrap things up: make a gzipped version of what was loaded
##############################################################################
# get rid of intermediate files
#rm -f temp*.csv temp.sql t?.*.csv d?.csv m?.csv part*.csv schema*.xml header4Solr.csv public.csv internal.csv
# zip up .csvs, save a bit of space on backups
#gzip -f 4solr.*.csv
date
