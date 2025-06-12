#gunzip 4solr.fields.mmap.public.counts.csv.gz
cut -f1 4solr.fields.mmap.public.counts.csv > solr-fields.txt
perl -pe 's/_ss?//;s/_/ /g;s/(\w+\S*\w*)/\u\L$1/g;' solr-fields.txt > labels
paste labels solr-fields.txt | perl -pe "s/^(.*?)\t(.*)$/    ('\1', '\2'),/" > solr-fields.py

echo > solr-config.py
for i in SEARCH FACETS LIST TABLE GALLERY FULL; do
  echo "parmz.$i = [" >> solr-config.py
  cat solr-fields.py >> solr-config.py
  echo "]" >> solr-config.py
  echo "FIELD_DEFINITIONS['$i'] = parmz.$i" >> solr-config.py
  echo >> solr-config.py
done



