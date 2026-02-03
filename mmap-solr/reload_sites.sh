DERIVATIVES="$1"
# extract the sites table from the psql db and prep it for solr
if [ ! "${CONNECT_STRING}" ]; then
  echo set env var CONNECT_STRING please!
  exit 1
fi
psql -R"@@" -A -d "$CONNECT_STRING" -f extract_sites.sql | \
  perl -pe 's/[\r\n\t]/ /g;s/\|/\t/g;s/\@\@/\n/g' > mmap-dbsites.csv
perl -i -pe 'if (/Site_Name/) {s/\t/_s\t/g;s/$/_s/;s/Record_No_s/id/;tr/A-Z/a-z/;s/ /_/g;s/\?//g;}' mmap-dbsites.csv
grep site_name mmap-dbsites.csv | perl -pe 's/ +/_/g' > mmap-dbsites.header.csv

# make a list of the site images and prep it for solr
find "${DERIVATIVES}" -type f | grep -v DS_Store | grep -v extra_maps > sites0.tmp
perl -ne '
next if /Old-/i;
chomp ;
s#^.*?/derivatives/##;
print;print "\t";
s/Articts/Artifacts/;
s/General [Vv]/General_v/;
s#missing_site_name/#missing_site_name #;
s#/#\t#g;
# only do this once per line to insert a tab between data and site name
s/ /\t/;
s/\t\d+\. /\t/;
s#(Artifacts\t)?Studio Artifacts shot#Studio_artifact_shot#i;
s#(Artifacts\t)?Studio Individual +Shot Art#Studio_artifact_shot#i;
s#(Artifacts\t)?Studio Bag Shot Artifact#Studio_bag_shot#i;
s#(Artifacts\t)?Studio Bag Shot Art#Studio_bag_shot#i;
s#(Artifacts\t)?Studio Bag shot#Artifacts_bag_shot#i;
s#(Artifacts\t)?In situ Artifacts?#Artifacts_on_site#i;
s#Artifacts +on site#Artifacts_on_site#i;
s#Artifacts in situ#Artifacts_on_site#i;
# skip directories whose resolved names contain blanks
print "$_\n";' \
sites0.tmp > sites1.tmp
perl -ne '@x=split/\t/;print if (@x[3] =~ / /)' sites1.tmp | cut -f1 | perl -pe 's#(.*)\/.*#\1#' | uniq

perl -ne '@x=split/\t/;next if @x[3] =~ /( |JPG)/; print if /\.(jpg|jpeg|tif|gif|png|webp)/i' sites1.tmp > sites2.tmp
cat mmap-site-photos.header.csv sites2.tmp > mmap-site-photos.csv
perl -pe 's/\t/\n/g;s/\r//g;' mmap-site-photos.header.csv > mmap-site-photos.fields.txt
python3 evaluate.py mmap-site-photos.csv sites3.tmp

# merge them
python merge_sites.py mmap-dbsites.csv mmap-site-photos.csv mmap-sites.csv
head -1 mmap-sites.csv | perl -pe 's/\t/\n/g;s/\r//g;' > mmap-sites.fields.txt

# load the whole shebang into solr core mmap-sites
# ./makesolrcores.sh mmap-sites
./solrETL-sites.sh mmap-sites mmap-sites

rm *.tmp
