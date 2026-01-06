#!/bin/bash -x
#
# nightly update of mmap resources
#
source /home/ubuntu/.profile
cd /home/ubuntu/blacklight-mmap/mmap-solr/

# concatenate all tablet GIS files together and process into postgres
cat /mnt/images/MMAP_GIS_data/* > csvtoload.csv
time ./loadpostgres.sh csvtoload.csv "$CONNECT_STRING" mapping-tablet-to-postgres.csv >> mmap-loadpostgres.txt 2>&1

# reload artifacts solr core
time ./solrETL-artifacts.sh mmap >> mmap-reload-artifacts.txt 2>&1

# reload sites solr core
time ./reload_sites.sh /mnt/images/LaosPhotos/derivatives >> mmap-reload-sites.txt 2>&1

# regenerate site catalog
python make_report.py mmap-sites.csv aws > /var/www/html/site_report.html
