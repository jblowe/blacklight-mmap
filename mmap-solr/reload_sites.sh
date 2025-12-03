
# extract the sites table from the psql db and prep it for solr
if [[ ! ${CONNECT_STRING} ]]; then
  echo set env var CONNECT_STRING!
  exit 1
fi
psql -R"@@" -A -d "$CONNECT_STRING" -f extract_sites.sql | \
perl -pe 's/[\r\n\t]/ /g;s/\|/\t/g;s/\@\@/\n/g' > mmap-dbsites.csv
perl -i -pe 'if (/Site_Name/) {s/\t/_s\t/g;s/$/_s/;s/Record_No_s/id/;tr/A-Z/a-z/;s/ /_/g;s/\?//g;}' mmap-dbsites.csv
grep site_name mmap-dbsites.csv | perl -pe 's/ +/_/g' > mmap-dbsites.header.csv

# make a list of the site images and prep it for solr
find ~/image_repos/LaosPhotos/derivatives -type f | grep -v DS_Store | grep -v extra_maps > mmap-site-photos.txt
perl -ne 'chomp ; s#/Users/johnlowe/image_repos/LaosPhotos/derivatives/##;print;print "\t";s/Articts/Artifacts/;s#missing_site_name/#missing_site_name #;s/General [Vv]/General_v/;s#missing_site_name/#missing_site_name #;s#/#\t#g;s/ /\t/;print "$_\n"' mmap-site-photos.txt > sites1.tmp
cat mmap-site-photos.header.csv sites1.tmp > mmap-site-photos.csv
perl -pe 's/\t/\n/g;s/\r//g;' mmap-site-photos.header.csv > mmap-site-photos.fields.txt
python3 evaluate.py mmap-site-photos.csv sites2.tmp

# merge them
python merge_sites.py mmap-dbsites.csv mmap-site-photos.csv mmap-sites.csv
head -1 mmap-sites.csv | perl -pe 's/\t/\n/g;s/\r//g;' > mmap-sites.fields.txt

# load the whole shebang into solr core mmap-sites
./makesolrcores.sh mmap-sites
./solrETL-sites.sh mmap-sites mmap-sites

rm *.tmp

