#!/bin/bash -x
date
TABLE=$1
CORE=$2
##############################################################################
# clear out the existing data
##############################################################################
# curl -S -s "http://localhost:8983/solr/${CORE}/update" --data '<delete><query>*:*</query></delete>' -H 'Content-type:text/xml; charset=utf-8'
# curl -S -s "http://localhost:8983/solr/${CORE}/update" --data '<commit/>' -H 'Content-type:text/xml; charset=utf-8'
##############################################################################
# load file
##############################################################################
ss_string="f.THUMBNAIL_ss.split=true&f.THUMBNAIL_ss.separator=|&"
time curl -X POST -S -s "http://localhost:8983/solr/${CORE}/update/csv?commit=true&header=true&separator=%09&${ss_string}f.blob_ss.split=true&f.blob_ss.separator=,&encapsulator=\\" -T ${TABLE} -H 'Content-type:text/plain; charset=utf-8' &
time python3 evaluate.py ${TABLE} counts.${TABLE}
date
