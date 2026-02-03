#!/bin/bash -x
#
# nightly update of mmap resources
#
PHOTO_DIR=/mnt/images/LaosPhotos
source /home/ubuntu/.profile
cd /home/ubuntu/blacklight-mmap/mmap-solr/

# update derivatives
time ./make_derivatives.sh ${PHOTO_DIR}/originals ${PHOTO_DIR}/derivatives >> mmap-derivatives.txt 2>&1

# concatenate all tablet GIS files together and process into postgres
cat /mnt/images/MMAP_GIS_data/* > csvtoload.csv
time ./loadpostgres.sh csvtoload.csv "$CONNECT_STRING" mapping-tablet-to-postgres.csv >> mmap-loadpostgres.txt 2>&1

# reload artifacts solr core
time ./solrETL-artifacts.sh mmap >> mmap-reload-artifacts.txt 2>&1

# reload sites solr core
time ./reload_sites.sh ${PHOTO_DIR}/derivatives >> mmap-reload-sites.txt 2>&1

# regenerate site catalog, but leave it in the runtime directory
python make_report.py mmap-sites.csv aws > site_report.html
