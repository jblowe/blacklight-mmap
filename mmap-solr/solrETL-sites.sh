#!/bin/bash -x
date
TABLE=$1
TABLE=${TABLE%.csv}
CORE=$2
##############################################################################
# generate multivalued field schema (in csv cells)
##############################################################################
./generate_solr_splits.sh ${TABLE}
ss_string=$(cat ${TABLE}.uploadparms.txt)
##############################################################################
# TODO: compute _i values for _dt values (to support BL date range searching)
##############################################################################
# time python3 computeTimeIntegers.py d9.csv ${TABLE}.csv
# clean up some outstanding sins perpetuated by earlier scripts
# perl -i -pe 's/\r//g;s/\\/\//g;s/\t"/\t/g;s/"\t/\t/g;s/\"\"/"/g' ${TABLE}.csv
##############################################################################
# ok, now let's load this into solr...
##############################################################################
# clear out the existing data
##############################################################################
curl -S -s "http://localhost:8983/solr/${CORE}/update" --data '<delete><query>*:*</query></delete>' -H 'Content-type:text/xml; charset=utf-8'
curl -S -s "http://localhost:8983/solr/${CORE}/update" --data '<commit/>' -H 'Content-type:text/xml; charset=utf-8'
##############################################################################
# this POSTs the csv to the Solr / update endpoint
# note, among other things, the overriding of the encapsulator with \
##############################################################################
# time curl -X POST -s \
#  'http://localhost:8983/solr/mmap-sites/update/csv?commit=true&header=true&separator=%09&split=true&separator=%7C' \
#  -H 'Content-type:text/csv; charset=utf-8' \
#  -T mmap-sites.csv
time curl -X POST -S -s \
  "http://localhost:8983/solr/${CORE}/update/csv?commit=true&header=true&separator=%09&${ss_string}f.blob_ss.split=true&f.blob_ss.separator=,&encapsulator=\\" \
  -H 'Content-type:text/plain; charset=utf-8' \
  -T ${TABLE}.csv
time python3 evaluate.py ${TABLE}.csv tmp > counts.${TABLE}.csv
rm tmp
date
