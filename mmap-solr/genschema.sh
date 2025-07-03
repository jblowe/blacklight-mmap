##############################################################################
# here are the schema changes needed: copy all the _s and _ss to _txt, and vv.
##############################################################################
perl -pe 's/\t/\n/g' $1.header4Solr.csv | \
  perl -ne 'chomp; next unless /_txt/; s/_txt$//; print "    <copyField source=\"" .$_."_txt\" dest=\"".$_."_s\"/>\n"' > $1.schemaFragment.xml
perl -pe 's/\t/\n/g' $1.header4Solr.csv | \
  perl -ne 'chomp; next unless /_s$/; s/_s$//; print "    <copyField source=\"" .$_."_s\" dest=\"".$_."_txt\"/>\n"' >> $1.schemaFragment.xml
perl -pe 's/\t/\n/g' $1.header4Solr.csv | \
  perl -ne 'chomp; next unless /_ss$/; s/_ss$//; print "    <copyField source=\"" .$_."_ss\" dest=\"".$_."_txt\"/>\n"' >> $1.schemaFragment.xml
##############################################################################
# here are the solr csv update parameters needed for multivalued fields
##############################################################################
perl -pe 's/\t/\n/g' $1.header4Solr.csv | \
  perl -ne 'chomp; next unless /_ss/; next if /blob/; print "f.$_.split=true&f.$_.separator=%7C&"' > $1.uploadparms.txt
