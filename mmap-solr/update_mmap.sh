
#
cd /home/ubuntu/mmap-solr/

time ./solrETL-artifacts.sh mmap  > /var/www/html/mmap-reload-artifacts.txt 2>&1
time ./reload_sites.sh /mnt/images/LaosPhotos/derivatives > /var/www/html/mmap-reload-sites.txt 2>&1
python make_report.py mmap-sites.csv aws > /var/www/html/site_report.html

