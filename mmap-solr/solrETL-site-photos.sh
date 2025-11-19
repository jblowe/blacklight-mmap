find ~/image_repos/LaosPhotos/derivatives -type f | grep -v DS_Store > mmap-sites.txt
perl -ne 'chomp ; s#/Users/johnlowe/image_repos/LaosPhotos/derivatives/##;print;print "\t";s#/#\t#g;s/ /\t/;print "$_\n"' mmap-sites.txt > sites1.tmp
python3 evaluate.py sites1.tmp sites2.tmp
cat mmap-sites.header sites2.tmp > mmap-sites.csv
perl -pe 's/\t/\n/g' mmap-sites.header > mmap-sites.fields.txt
./makesolrcores.sh mmap-sites
./solrETL-sites.sh mmap
./sitesETL.sh mmap-sites.csv mmap-sites